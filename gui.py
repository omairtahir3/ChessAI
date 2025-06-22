import pygame
import copy
from pygame.locals import QUIT, MOUSEBUTTONDOWN
from engine import *
from constants import *

class ChessGame:
    def __init__(self):
        pygame.init()
        self.board = copy.deepcopy(STARTING_BOARD)
        self.current_player = 'w'
        self.selected_piece = None
        self.valid_moves = []
        self.game_over = False
        self.game_result = None
        self.winner = None 
        self.history = []
        self.square_size = 80
        self.width = self.height = 8 * self.square_size
        self.piece_images = self.load_images()
        self.message_font = pygame.font.Font(None, 60)
        self.subtext_font = pygame.font.Font(None, 36)
        self.move_indicator = self.create_move_indicator()
        self.castling_rights = {
            'w': {'kingside': True, 'queenside': True},
            'b': {'kingside': True, 'queenside': True}
        } 

    def create_move_indicator(self):
        indicator = pygame.Surface((self.square_size, self.square_size), pygame.SRCALPHA)
        pygame.draw.circle(indicator, (100, 100, 100, 128), 
                          (self.square_size//2, self.square_size//2), 
                          self.square_size//6)
        return indicator

    def load_images(self):
        images = {}
        for piece_code, image_path in PIECE_IMAGES.items():
            try:
                images[piece_code] = pygame.transform.scale(
                    pygame.image.load(image_path), 
                    (self.square_size, self.square_size)
                )
            except Exception as e:
                print(f"Error loading {image_path}: {e}")
                font = pygame.font.Font(None, 36)
                color = (0, 0, 0) if piece_code.islower() else (255, 255, 255)
                images[piece_code] = font.render(piece_code, True, color)
        return images

    def draw_board(self, screen):
        colors = [(235, 235, 208), (119, 148, 85)] 
        for row in range(8):
            for col in range(8):
                rect = (
                    col * self.square_size,
                    row * self.square_size,
                    self.square_size,
                    self.square_size
                )
                color = colors[(row + col) % 2]
                pygame.draw.rect(screen, color, rect)
            
                piece = self.board[row][col]
                if piece != '-':
                    screen.blit(self.piece_images[piece], rect[:2])

        if self.selected_piece:
            sr, sc = self.selected_piece
            piece = self.board[sr][sc]
        
            if (piece.lower() == 'k' 
                and ((self.current_player == 'w' and piece == 'K') 
                or (self.current_player == 'b' and piece == 'k'))):
                    player_color = 'w' if piece == 'K' else 'b'
            
                    if validate_castling(self.board, player_color, 'kingside', self.castling_rights):
                        indicator_col = sc + 2
                        screen.blit(self.move_indicator,
                           (indicator_col * self.square_size,
                            sr * self.square_size))

                    if validate_castling(self.board, player_color, 'queenside', self.castling_rights):
                        indicator_col = sc - 2 
                        screen.blit(self.move_indicator,
                           (indicator_col * self.square_size,
                            sr * self.square_size))

        if self.selected_piece:
            sr, sc = self.selected_piece
            pygame.draw.rect(screen, (255, 255, 0), 
                        (sc * self.square_size,
                         sr * self.square_size,
                         self.square_size,
                         self.square_size), 3)

        for move in self.valid_moves:
            if move[0] == self.selected_piece:
                er, ec = move[1]
                screen.blit(self.move_indicator,
                       (ec * self.square_size,
                        er * self.square_size))
        if self.game_over:
            self.draw_game_over_overlay(screen)

    def draw_game_over_overlay(self,screen):
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))

        if self.game_result == 'checkmate':
            text = f"CHECKMATE! {self.get_winner_text()} WINS!"
            color = (255, 215, 0)  
        else:
            text = "STALEMATE! GAME DRAWN"
            color = (200, 200, 200) 

        text_surf = self.message_font.render(text, True, color)
        text_rect = text_surf.get_rect(center=(self.width//2, self.height//2))
        screen.blit(text_surf, text_rect)

        subtext = "Click to exit" if self.game_result == 'checkmate' else "Game drawn"
        sub_surf = self.subtext_font.render(subtext, True, (255, 255, 255))
        sub_rect = sub_surf.get_rect(center=(self.width//2, self.height//2 + 50))
        screen.blit(sub_surf, sub_rect)

        if self.game_result == 'checkmate':
            king_pos = find_king_position(self.board, self.current_player)
            if king_pos:
                k_row, k_col = king_pos
                x = k_col * self.square_size
                y = k_row * self.square_size
                
                pygame.draw.line(screen, (255, 0, 0), (x, y),
                                (x + self.square_size, y + self.square_size), 5)
                pygame.draw.line(screen, (255, 0, 0), 
                                (x + self.square_size, y),
                                (x, y + self.square_size), 5)

    def handle_click(self, pos):
        col = pos[0] // SQUARE_SIZE
        row = pos[1] // SQUARE_SIZE
        clicked_pos = (row, col)

        if self.selected_piece is None:
            piece = self.board[row][col]
            if piece != '-' and ((self.current_player == 'w' and piece.isupper()) or 
                           (self.current_player == 'b' and piece.islower())):
                self.selected_piece = (row, col)
                self.valid_moves = get_legal_moves(self.board, self.current_player, self.castling_rights)
        else:
            sr, sc = self.selected_piece
            er, ec = clicked_pos

            if any(move[1] == (er, ec) for move in self.valid_moves):
                self.board, self.castling_rights = execute_move(self.board, ((sr, sc), (er, ec)), self.castling_rights)
            
                self.current_player = 'b' if self.current_player == 'w' else 'w'
            
                white_king, black_king = check_king_status(self.board)
                if not white_king or not black_king:
                    self.game_over = True

            self.selected_piece = None
            self.valid_moves = []
        
    def ai_move(self):
        if not self.game_over and self.current_player == 'b':
            ai_move = find_best_move(self.board, depth=3, is_maximizing=False, castling_rights=self.castling_rights)
            if ai_move:
                self.board, self.castling_rights = execute_move(self.board, ai_move, self.castling_rights)
                self.current_player = 'w'
                self.check_game_over()
            else:
                self.game_over = True 

    def make_move(self, move):
        self.board = execute_move(self.board, move, self.castling_rights)
        self.current_player = 'b' if self.current_player == 'w' else 'w'
        self.check_game_over()

    def get_winner_text(self):
        if self.winner == 'w': return "WHITE"
        if self.winner == 'b': return "BLACK"
        return ""

    def check_game_over(self):
        legal_moves = get_legal_moves(self.board, self.current_player, self.castling_rights)
        king_pos = find_king_position(self.board, self.current_player)
        in_check = is_king_under_attack(self.board, king_pos, self.current_player, self.castling_rights)
        
        if not legal_moves:
            self.game_over = True
            self.game_result = 'checkmate' if in_check else 'stalemate'
            self.winner = 'b' if self.current_player == 'w' else 'w' if in_check else None

    def run(self):
        pygame.init()
        screen = pygame.display.set_mode((self.width, self.height))
        clock = pygame.time.Clock()
    
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                elif event.type == MOUSEBUTTONDOWN:
                    if self.game_over:
                        running = False 
                    else:
                        self.handle_click(event.pos)

            if not self.game_over and self.current_player == 'b':
                self.ai_move()

            screen.fill((0,0,0))
            self.draw_board(screen)
            pygame.display.flip()
            clock.tick(60)

        pygame.quit()

if __name__ == "__main__":
    game = ChessGame()
    game.run()