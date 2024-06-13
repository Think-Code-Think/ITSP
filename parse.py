import chess
import chess.pgn
import numpy as np
import os
import multiprocessing
import random
import h5py
import logging

logging.basicConfig(level=logging.INFO)

def read_games(fn):
    with open(fn) as f:
        while True:
            try:
                game = chess.pgn.read_game(f)
            except KeyboardInterrupt:
                raise
            except Exception as e:
                logging.warning(f"Error reading game: {e}")
                continue

            if not game:
                break
            
            yield game

def bb2array(b, flip=False):
    x = np.zeros(64, dtype=np.int8)
    
    for piece_type in chess.PIECE_TYPES:
        for pos in b.pieces(piece_type, chess.WHITE):
            x[pos] = piece_type
        for pos in b.pieces(piece_type, chess.BLACK):
            x[pos] = -piece_type

    if flip:
        x = x[::-1]
        x = -x

    return x

def parse_game(game):
    result_map = {'1-0': 1, '0-1': -1, '1/2-1/2': 0}
    result = game.headers.get('Result')
    if result not in result_map:
        return None
    y = result_map[result]

    node = game.end()
    if not node.board().is_game_over():
        return None

    nodes = []
    moves_left = 0
    while node:
        nodes.append((moves_left, node, node.board().turn == chess.BLACK))
        node = node.parent
        moves_left += 1

    if len(nodes) < 10:
        logging.info(f"Short game: {game.headers}")

    nodes.pop()

    moves_left, node, flip = random.choice(nodes)
    board = node.board()
    x = bb2array(board, flip=flip)

    parent_board = node.parent.board()
    x_parent = bb2array(parent_board, flip=(not flip))
    if flip:
        y = -y

    moves = list(parent_board.legal_moves)
    random_move = random.choice(moves)
    parent_board.push(random_move)
    x_random = bb2array(parent_board, flip=flip)

    parent_board.pop()  # Restore the board state

    if moves_left < 3:
        logging.info(f"{moves_left} moves left, winner: {y}, headers: {game.headers}")

    return (x, x_parent, x_random, moves_left, y)

def read_all_games(fn_in, fn_out):
    with h5py.File(fn_out, 'w') as g:
        X = g.create_dataset('x', (0, 64), dtype='b', maxshape=(None, 64), chunks=True)
        Xr = g.create_dataset('xr', (0, 64), dtype='b', maxshape=(None, 64), chunks=True)
        Xp = g.create_dataset('xp', (0, 64), dtype='b', maxshape=(None, 64), chunks=True)
        Y = g.create_dataset('y', (0,), dtype='b', maxshape=(None,), chunks=True)
        M = g.create_dataset('m', (0,), dtype='b', maxshape=(None,), chunks=True)
        
        size = 0
        line = 0
        for game in read_games(fn_in):
            parsed_game = parse_game(game)
            if parsed_game is None:
                continue
            x, x_parent, x_random, moves_left, y = parsed_game

            if line + 1 >= size:
                size = 2 * size + 1
                logging.info(f"Resizing to {size}")
                [d.resize(size=size, axis=0) for d in (X, Xr, Xp, Y, M)]

            X[line] = x
            Xr[line] = x_random
            Xp[line] = x_parent
            Y[line] = y
            M[line] = moves_left

            line += 1

        [d.resize(size=line, axis=0) for d in (X, Xr, Xp, Y, M)]

def read_all_games_2(args):
    return read_all_games(*args)

def parse_dir(directory):
    files = []
    for fn_in in os.listdir(directory):
        if not fn_in.endswith('.pgn'):
            continue
        fn_in = os.path.join(directory, fn_in)
        fn_out = fn_in.replace('.pgn', '.hdf5')
        if not os.path.exists(fn_out):
            files.append((fn_in, fn_out))

    with multiprocessing.Pool() as pool:
        pool.map(read_all_games_2, files)

if __name__ == '__main__':
    directory = r'C:\Users\Swarup\Desktop\ITSP\Database'  # Or another directory
    parse_dir(directory)
