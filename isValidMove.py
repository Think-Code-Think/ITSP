import chess

def find_valid_moves(fen):
    # Create a board from the given FEN
    board = chess.Board(fen)
    
    # Check if it's a legal position
    if not board.is_valid():
        raise ValueError("The provided FEN position is not valid.")
    
    # Determine whose turn it is
    turn = "White" if board.turn == chess.WHITE else "Black"
    
    # Check if there is a check
    in_check = board.is_check()
    
    # Check if castling is allowed
    castling_rights = {
        "white_kingside": board.has_kingside_castling_rights(chess.WHITE),
        "white_queenside": board.has_queenside_castling_rights(chess.WHITE),
        "black_kingside": board.has_kingside_castling_rights(chess.BLACK),
        "black_queenside": board.has_queenside_castling_rights(chess.BLACK)
    }
    
    # Generate all legal moves
    legal_moves = list(board.legal_moves)
    
    move_list = []
    for move in legal_moves:
        move_info = {
            "uci": move.uci(),
            "san": board.san(move),
            "from_square": chess.square_name(move.from_square),
            "to_square": chess.square_name(move.to_square),
            "promotion": chess.piece_name(move.promotion) if move.promotion else None
        }
        move_list.append(move_info)
    
    return {
        "turn": turn,
        "in_check": in_check,
        "castling_rights": castling_rights,
        "legal_moves": move_list
    }

if __name__ == "__main__":
    # Example FEN string
    fen = "r1bqkbnr/pppppppp/n7/8/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3"
    
    result = find_valid_moves(fen)
    
    print(f"Turn: {result['turn']}")
    print(f"In Check: {result['in_check']}")
    print("Castling Rights:")
    print(f"  White Kingside: {result['castling_rights']['white_kingside']}")
    print(f"  White Queenside: {result['castling_rights']['white_queenside']}")
    print(f"  Black Kingside: {result['castling_rights']['black_kingside']}")
    print(f"  Black Queenside: {result['castling_rights']['black_queenside']}")
    print("Legal Moves:")
    for move in result['legal_moves']:
        promotion_info = f" (promotion to {move['promotion']})" if move['promotion'] else ""
        print(f"  {move['san']} ({move['uci']}) from {move['from_square']} to {move['to_square']}{promotion_info}")
