import copy
from constants import *
board_history = []

def display_chessboard(chessboard):
    for row in chessboard:
        print(" ".join(row))
    print()

def get_positional_values(piece, row, col):
    piece_type = piece.upper()
    if piece_type == 'P':
        return PAWN_POSITION_VALUES[row][col] if piece.isupper() else PAWN_POSITION_VALUES[7 - row][col]
    elif piece_type == 'N':
        return KNIGHT_POSITION_VALUES[row][col] if piece.isupper() else KNIGHT_POSITION_VALUES[7 - row][col]
    elif piece_type == 'B':
        return BISHOP_POSITION_VALUES[row][col] if piece.isupper() else BISHOP_POSITION_VALUES[7 - row][col]
    elif piece_type == 'R':
        return ROOK_POSITION_VALUES[row][col] if piece.isupper() else ROOK_POSITION_VALUES[7 - row][col]
    elif piece_type == 'Q':
        return QUEEN_POSITION_VALUES[row][col] if piece.isupper() else QUEEN_POSITION_VALUES[7 - row][col]
    elif piece_type == 'K':
        return KING_POSITION_VALUES[row][col] if piece.isupper() else KING_POSITION_VALUES[7 - row][col]
    return 0

def calculate_board_score(chessboard):
    total_score = 0
    for row in range(8):
        for col in range(8):
            piece = chessboard[row][col]
            if piece in PIECE_VALUES:
                total_score += PIECE_VALUES[piece]
                total_score += get_positional_values(piece, row, col)
    return total_score

def generate_pawn_moves(chessboard, row, col, piece, player_color):
    pawn_direction = -1 if player_color == "w" else 1
    possible_moves = []
    
    if 0 <= row + pawn_direction < 8 and chessboard[row + pawn_direction][col] == "-":
        possible_moves.append(((row, col), (row + pawn_direction, col)))
        if (row == 6 and player_color == "w") or (row == 1 and player_color == "b"):
            if chessboard[row + 2 * pawn_direction][col] == "-":
                possible_moves.append(((row, col), (row + 2 * pawn_direction, col)))
    
    for col_offset in [-1, 1]:
        new_col = col + col_offset
        new_row = row + pawn_direction
        if 0 <= new_row < 8 and 0 <= new_col < 8:
            target_piece = chessboard[new_row][new_col]
            if target_piece != "-" and target_piece.islower() != piece.islower():
                possible_moves.append(((row, col), (new_row, new_col)))
    
    return possible_moves

def generate_knight_moves(chessboard, row, col, piece):
    knight_offsets = [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]
    possible_moves = []
    
    for row_offset, col_offset in knight_offsets:
        new_row, new_col = row + row_offset, col + col_offset
        if 0 <= new_row < 8 and 0 <= new_col < 8:
            target_piece = chessboard[new_row][new_col]
            if target_piece == "-" or target_piece.islower() != piece.islower():
                possible_moves.append(((row, col), (new_row, new_col)))
    
    return possible_moves

def generate_bishop_moves(chessboard, row, col, piece):
    bishop_directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
    possible_moves = []
    
    for row_dir, col_dir in bishop_directions:
        new_row, new_col = row + row_dir, col + col_dir
        while 0 <= new_row < 8 and 0 <= new_col < 8:
            target_piece = chessboard[new_row][new_col]
            if target_piece == "-":
                possible_moves.append(((row, col), (new_row, new_col)))
            else:
                if target_piece.islower() != piece.islower():
                    possible_moves.append(((row, col), (new_row, new_col)))
                break
            new_row += row_dir
            new_col += col_dir
    
    return possible_moves

def generate_rook_moves(chessboard, row, col, piece):
    rook_directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    possible_moves = []
    
    for row_dir, col_dir in rook_directions:
        new_row, new_col = row + row_dir, col + col_dir
        while 0 <= new_row < 8 and 0 <= new_col < 8:
            target_piece = chessboard[new_row][new_col]
            if target_piece == "-":
                possible_moves.append(((row, col), (new_row, new_col)))
            else:
                if target_piece.islower() != piece.islower():
                    possible_moves.append(((row, col), (new_row, new_col)))
                break
            new_row += row_dir
            new_col += col_dir
    
    return possible_moves

def generate_queen_moves(chessboard, row, col, piece):
    return generate_bishop_moves(chessboard, row, col, piece) + generate_rook_moves(chessboard, row, col, piece)

def generate_king_moves(chessboard, row, col, piece, castling_rights, include_castling=True):
    king_offsets = [(1, 1), (1, -1), (-1, 1), (-1, -1), (1, 0), (-1, 0), (0, 1), (0, -1)]
    possible_moves = []
    
    for row_offset, col_offset in king_offsets:
        new_row, new_col = row + row_offset, col + col_offset
        if 0 <= new_row < 8 and 0 <= new_col < 8:
            target_piece = chessboard[new_row][new_col]
            if target_piece == "-" or target_piece.islower() != piece.islower():
                possible_moves.append(((row, col), (new_row, new_col)))
    
    if include_castling:
        if (piece == 'K' and row == 7 and col == 4) or (piece == 'k' and row == 0 and col == 4):
            player_color = 'w' if piece == 'K' else 'b'
            if validate_castling(chessboard, player_color, 'kingside', castling_rights):
                possible_moves.append(((row, col), (row, col + 2)))
            if validate_castling(chessboard, player_color, 'queenside', castling_rights):
                possible_moves.append(((row, col), (row, col - 2)))

    return possible_moves

def get_legal_moves(chessboard, player_color, castling_rights):
    pseudolegal_moves = []
    
    for row in range(8):
        for col in range(8):
            piece = chessboard[row][col]
            if piece == "-":
                continue
                
            if (player_color == "w" and piece.isupper()) or (player_color == "b" and piece.islower()):
                piece_type = piece.lower()
                if piece_type == 'p':
                    pseudolegal_moves += generate_pawn_moves(chessboard, row, col, piece, player_color)
                elif piece_type == 'n':
                    pseudolegal_moves += generate_knight_moves(chessboard, row, col, piece)
                elif piece_type == 'b':
                    pseudolegal_moves += generate_bishop_moves(chessboard, row, col, piece)
                elif piece_type == 'r':
                    pseudolegal_moves += generate_rook_moves(chessboard, row, col, piece)
                elif piece_type == 'q':
                    pseudolegal_moves += generate_queen_moves(chessboard, row, col, piece)
                elif piece_type == 'k':
                    pseudolegal_moves += generate_king_moves(chessboard, row, col, piece, castling_rights, include_castling=True)

    legal_moves = []
    for move in pseudolegal_moves:
        new_board, new_castling = execute_move(chessboard, move, castling_rights)
        king_pos = find_king_position(new_board, player_color)
        if king_pos and not is_king_under_attack(new_board, king_pos, player_color, new_castling):
            legal_moves.append(move)
    
    return legal_moves

def execute_move(chessboard, move, castling_rights):
    new_castling = copy.deepcopy(castling_rights)
    new_board = copy.deepcopy(chessboard)
    (start_row, start_col), (end_row, end_col) = move
    piece = new_board[start_row][start_col]

    if piece.lower() == 'k':
        color = 'w' if piece == 'K' else 'b'
        new_castling[color]['kingside'] = False
        new_castling[color]['queenside'] = False
    elif piece.lower() == 'r':
        color = 'w' if piece == 'R' else 'b'
        if start_col == 7: 
            new_castling[color]['kingside'] = False
        elif start_col == 0: 
            new_castling[color]['queenside'] = False

    new_board[end_row][end_col] = piece
    new_board[start_row][start_col] = '-'

    if piece.lower() == 'k' and abs(start_col - end_col) == 2:
        row = start_row 
        if end_col > start_col:
            rook_start_col = 7
            rook_end_col = end_col - 1 
        else: 
            rook_start_col = 0
            rook_end_col = end_col + 1

        rook = 'R' if piece == 'K' else 'r'
        new_board[row][rook_end_col] = rook
        new_board[row][rook_start_col] = '-'

    return new_board, new_castling

def minimax(chessboard, depth, is_maximizing, alpha, beta, castling_rights):
    if depth == 0:
        return calculate_board_score(chessboard), None

    current_player = 'w' if is_maximizing else 'b'
    legal_moves = get_legal_moves(chessboard, current_player, castling_rights)
    
    if not legal_moves:
        king_position = find_king_position(chessboard, current_player)
        if king_position and is_king_under_attack(chessboard, king_position, current_player, castling_rights):
            return (-float('inf') if is_maximizing else float('inf')), None
        else:
            return 0, None 

    best_move = None
    
    if is_maximizing:
        max_score = -float('inf')
        for move in legal_moves:
            new_board, new_castling = execute_move(chessboard, move, castling_rights)
            current_score, _ = minimax(new_board, depth - 1, False, alpha, beta, new_castling)
            if current_score > max_score:
                max_score = current_score
                best_move = move
            alpha = max(alpha, current_score)
            if beta <= alpha:
                break
        return max_score, best_move
    else:
        min_score = float('inf')
        for move in legal_moves:
            new_board, new_castling = execute_move(chessboard, move, castling_rights)
            current_score, _ = minimax(new_board, depth - 1, True, alpha, beta, new_castling)
            if current_score < min_score:
                min_score = current_score
                best_move = move
            beta = min(beta, current_score)
            if beta <= alpha:
                break
        return min_score, best_move

def find_best_move(chessboard, depth=3, is_maximizing=True, castling_rights=None):
    if castling_rights is None:
        castling_rights = reset_castling_rights()
    _, best_move = minimax(chessboard, depth, is_maximizing, -float('inf'), float('inf'), castling_rights)
    return best_move
def is_king_under_attack(chessboard, king_position, player_color, castling_rights):
    opponent_color = 'b' if player_color == 'w' else 'w'
    opponent_moves = []
    
    for row in range(8):
        for col in range(8):
            piece = chessboard[row][col]
            if piece == "-":
                continue
                
            if (piece.isupper() and opponent_color == 'w') or (piece.islower() and opponent_color == 'b'):
                piece_type = piece.lower()
                if piece_type == 'p':
                    opponent_moves += generate_pawn_moves(chessboard, row, col, piece, opponent_color)
                elif piece_type == 'n':
                    opponent_moves += generate_knight_moves(chessboard, row, col, piece)
                elif piece_type == 'b':
                    opponent_moves += generate_bishop_moves(chessboard, row, col, piece)
                elif piece_type == 'r':
                    opponent_moves += generate_rook_moves(chessboard, row, col, piece)
                elif piece_type == 'q':
                    opponent_moves += generate_queen_moves(chessboard, row, col, piece)
                elif piece_type == 'k':
                    # Disable castling checks when verifying king safety
                    opponent_moves += generate_king_moves(chessboard, row, col, piece, castling_rights, include_castling=False)
    
    return any(move[1] == king_position for move in opponent_moves)

def find_king_position(chessboard, player_color):
    king_symbol = 'K' if player_color == 'w' else 'k'
    for row in range(8):
        for col in range(8):
            if chessboard[row][col] == king_symbol:
                return (row, col)
    return None

def check_king_status(chessboard):
    white_king_exists = any('K' in row for row in chessboard)
    black_king_exists = any('k' in row for row in chessboard)
    return white_king_exists, black_king_exists

def save_board_state(chessboard):
    board_history.append(copy.deepcopy(chessboard))

def validate_castling(board, player_color, side, castling_rights):
    row = 7 if player_color == 'w' else 0
    king_col = 4
    rook_col = 7 if side == 'kingside' else 0
    step = 1 if side == 'kingside' else -1

    if not castling_rights[player_color][side]:
        return False
    if board[row][king_col].lower() != 'k' or board[row][rook_col].lower() != 'r':
        return False
    for col in range(min(king_col, rook_col) + 1, max(king_col, rook_col)):
        if board[row][col] != '-':
            return False
    king_pos = (row, king_col)
    if is_king_under_attack(board, king_pos, player_color, castling_rights):
        return False

    current_castling = copy.deepcopy(castling_rights)
    for i in (1, 2):
        new_col = king_col + step * i
        temp_board, new_castling = execute_move(board, ((row, king_col), (row, new_col)), current_castling)
        if is_king_under_attack(temp_board, (row, new_col), player_color, new_castling):
            return False
        current_castling = new_castling 

    return True
def reset_castling_rights():
    castling_rights['w'] = {'kingside': True, 'queenside': True}
    castling_rights['b'] = {'kingside': True, 'queenside': True}