import enum
import chess.pgn
import numpy as np
import copy

# noinspection PyArgumentList
Winner = enum.Enum("Winner", "black white draw")

# input planes
# noinspection SpellCheckingInspection
pieces_order = 'KQRBNPkqrbnp' # 12x8x8
castling_order = 'KQkq'       # 4x8x8
# fifty-move-rule             # 1x8x8
# en en_passant               # 1x8x8

ind = {pieces_order[i]: i for i in range(12)}


class ChessEnv:
    """
    Represents a chess environment where a chess game is played/

    Attributes:
        :ivar chess.Board board: current board state
        :ivar int num_halfmoves: number of half moves performed in total by each player
        :ivar Winner winner: winner of the game
        :ivar boolean resigned: whether non-winner resigned
        :ivar str result: str encoding of the result, 1-0, 0-1, or 1/2-1/2
    """
    def __init__(self):
        self.board = None
        self.num_halfmoves = 0
        self.winner = None  # type: Winner
        self.resigned = False
        self.result = None

    def reset(self):
        """
        Resets to begin a new game
        :return ChessEnv: self
        """
        self.board = chess.Board()
        self.num_halfmoves = 0
        self.winner = None
        self.resigned = False
        return self

    def update(self, board):
        """
        Like reset, but resets the position to whatever was supplied for board
        :param chess.Board board: position to reset to
        :return ChessEnv: self
        """
        self.board = chess.Board(board)
        self.winner = None
        self.resigned = False
        return self

    @property
    def done(self):
        return self.winner is not None

    @property
    def white_won(self):
        return self.winner == Winner.white

    @property
    def white_to_move(self):
        return self.board.turn == chess.WHITE

    def step(self, action: str, check_over = True):
        """

        Takes an action and updates the game state

        :param str action: action to take in uci notation
        :param boolean check_over: whether to check if game is over
        """
        if check_over and action is None:
            return self._resign()

        self.board.push_uci(action)

        self.num_halfmoves += 1

        if check_over and self.board.result(claim_draw=True) != "*":
            return self._game_over()
        return 1

    def _game_over(self):
        if self.winner is None:
            self.result = self.board.result(claim_draw = True)
            if self.result == '1-0':
                self.winner = Winner.white
            elif self.result == '0-1':
                self.winner = Winner.black
            else:
                self.winner = Winner.draw
        return 0

    def _resign(self):
        self.resigned = True
        if self.white_to_move: # WHITE RESIGNED!
            self.winner = Winner.black
            self.result = "0-1"
        else:
            self.winner = Winner.white
            self.result = "1-0"
        return 0

    def adjudicate(self):
        score = self.testeval(absolute = True)
        if abs(score) < 0.01:
            self.winner = Winner.draw
            self.result = "1/2-1/2"
        elif score > 0:
            self.winner = Winner.white
            self.result = "1-0"
        else:
            self.winner = Winner.black
            self.result = "0-1"

    def ending_average_game(self):
        self.winner = Winner.draw
        self.result = "1/2-1/2"

    def copy(self):
        env = copy.copy(self)
        env.board = copy.copy(self.board)
        return env

    def render(self):
        print("\n")
        print(self.board)
        print("\n")

    def bitboard(self):
        board = np.zeros((12),dtype=np.uint64)
        pieces = {
            "K": 0, "Q": 1, "R": 2, "N": 3, "B": 4, "P": 5,
            "k": 6, "q": 7, "r": 8, "n": 9, "b": 10, "p": 11,
        }
        tmp = {}
        for i, p in zip(self.board_idx, reversed(str(self.board.copy()).replace('\n', ' ').split(' '))):
            if p == '.':
                continue
            if not pieces[p] in tmp:
                tmp[pieces[p]] = [i,]
            else:
                tmp[pieces[p]].append(i)
        for key, val in tmp.items():
            board[key] = self.posToint(val)
        return board

    def posToint(self, n):
        if isinstance(n, int):
            return np.uint64(pow(2,8*(n//8))*pow(2,(7-(n%8))))
        elif isinstance(n, list):
            bitboard = 0
            for i in n:
                bitboard += pow(2,8*(i//8))*pow(2,(7-(i%8)))
            return np.uint64(bitboard)
        else:
            raise Exception('Bad input: posToint only accepts int or list of int.')

    @property
    def board_idx(self):
        return [56,57,58,59,60,61,62,63,
                48,49,50,51,52,53,54,55,
                40,41,42,43,44,45,46,47,
                32,33,34,35,36,37,38,39,
                24,25,26,27,28,29,30,31,
                16,17,18,19,20,21,22,23,
                8,9,10,11,12,13,14,15,
                0,1,2,3,4,5,6,7]

    @property
    def name_to_num(self):
        return {'a1': 0,'b1': 1,'c1': 2,'d1': 3,'e1': 4,'f1': 5,'g1': 6,'h1': 7,
                'a2': 8,'b2': 9,'c2':10,'d2':11,'e2':12,'f2':13,'g2':14,'h2':15,
                'a3':16,'b3':17,'c3':18,'d3':19,'e3':20,'f3':21,'g3':22,'h3':23,
                'a4':24,'b4':25,'c4':26,'d4':27,'e4':28,'f4':29,'g4':30,'h4':31, 
                'a5':32,'b5':33,'c5':34,'d5':35,'e5':36,'f5':37,'g5':38,'h5':39,
                'a6':40,'b6':41,'c6':42,'d6':43,'e6':44,'f6':45,'g6':46,'h6':47,
                'a7':48,'b7':49,'c7':50,'d7':51,'e7':52,'f7':53,'g7':54,'h7':55,
                'a8':56,'b8':57,'c8':58,'d8':59,'e8':60,'f8':61,'g8':62,'h8':63}

    @property
    def num_to_name(self):
        return dict([[v,k] for k,v in self.name_to_num.items()])

    def getRankIdx(self, n):
        return n//8

    def getFileIdx(self, n):
        return n%8


    @property
    def observation(self):
        return self.board.fen()

    def deltamove(self, fen_next):
        moves = list(self.board.legal_moves)
        for mov in moves:
            self.board.push(mov)
            fee = self.board.fen()
            self.board.pop()
            if fee == fen_next:
                return mov.uci()
        return None

    def replace_tags(self):
        return replace_tags_board(self.board.fen())

    def canonical_input_planes(self):
        """

        :return: a representation of the board using an (18, 8, 8) shape, good as input to a policy / value network
        """
        return canon_input_planes(self.board.fen())

    def testeval(self, absolute=False) -> float:
        return testeval(self.board.fen(), absolute)


def testeval(fen, absolute = False) -> float:
    piece_vals = {'K': 3, 'Q': 14, 'R': 5, 'B': 3.25, 'N': 3, 'P': 1} # somehow it doesn't know how to keep its queen
    ans = 0.0
    tot = 0
    for c in fen.split(' ')[0]:
        if not c.isalpha():
            continue

        if c.isupper():
            ans += piece_vals[c]
            tot += piece_vals[c]
        else:
            ans -= piece_vals[c.upper()]
            tot += piece_vals[c.upper()]
    v = ans/tot
    if not absolute and is_black_turn(fen):
        v = -v
    assert abs(v) < 1
    return np.tanh(v * 3) # arbitrary


def check_current_planes(realfen, planes):
    cur = planes[0:12]
    assert cur.shape == (12, 8, 8)
    fakefen = ["1"] * 64
    for i in range(12):
        for rank in range(8):
            for file in range(8):
                if cur[i][rank][file] == 1:
                    assert fakefen[rank * 8 + file] == '1'
                    fakefen[rank * 8 + file] = pieces_order[i]

    castling = planes[12:16]
    fiftymove = planes[16][0][0]
    ep = planes[17]

    castlingstring = ""
    for i in range(4):
        if castling[i][0][0] == 1:
            castlingstring += castling_order[i]

    if len(castlingstring) == 0:
        castlingstring = '-'

    epstr = "-"
    for rank in range(8):
        for file in range(8):
            if ep[rank][file] == 1:
                epstr = coord_to_alg((rank, file))

    realfen = maybe_flip_fen(realfen, flip=is_black_turn(realfen))
    realparts = realfen.split(' ')
    assert realparts[1] == 'w'
    assert realparts[2] == castlingstring
    assert realparts[3] == epstr
    assert int(realparts[4]) == fiftymove
    # realparts[5] is the fifty-move clock, discard that
    return "".join(fakefen) == replace_tags_board(realfen)


def canon_input_planes(fen):
    """

    :param fen:
    :return : (18, 8, 8) representation of the game state
    """
    fen = maybe_flip_fen(fen, is_black_turn(fen))
    return all_input_planes(fen)


def all_input_planes(fen):
    current_aux_planes = aux_planes(fen)

    history_both = to_planes(fen)

    ret = np.vstack((history_both, current_aux_planes))
    assert ret.shape == (18, 8, 8)
    return ret


def maybe_flip_fen(fen, flip = False):
    if not flip:
        return fen
    foo = fen.split(' ')
    rows = foo[0].split('/')
    def swapcase(a):
        if a.isalpha():
            return a.lower() if a.isupper() else a.upper()
        return a
    def swapall(aa):
        return "".join([swapcase(a) for a in aa])
    return "/".join([swapall(row) for row in reversed(rows)]) \
        + " " + ('w' if foo[1] == 'b' else 'b') \
        + " " + "".join(sorted(swapall(foo[2]))) \
        + " " + foo[3] + " " + foo[4] + " " + foo[5]


def aux_planes(fen):
    foo = fen.split(' ')

    en_passant = np.zeros((8, 8), dtype=np.float32)
    if foo[3] != '-':
        eps = alg_to_coord(foo[3])
        en_passant[eps[0]][eps[1]] = 1

    fifty_move_count = int(foo[4])
    fifty_move = np.full((8, 8), fifty_move_count, dtype=np.float32)

    castling = foo[2]
    auxiliary_planes = [np.full((8, 8), int('K' in castling), dtype=np.float32),
                        np.full((8, 8), int('Q' in castling), dtype=np.float32),
                        np.full((8, 8), int('k' in castling), dtype=np.float32),
                        np.full((8, 8), int('q' in castling), dtype=np.float32),
                        fifty_move,
                        en_passant]

    ret = np.asarray(auxiliary_planes, dtype=np.float32)
    assert ret.shape == (6, 8, 8)
    return ret

# FEN board is like this:
# a8 b8 .. h8
# a7 b7 .. h7
# .. .. .. ..
# a1 b1 .. h1
# 
# FEN string is like this:
#  0  1 ..  7
#  8  9 .. 15
# .. .. .. ..
# 56 57 .. 63

# my planes are like this:
# 00 01 .. 07
# 10 11 .. 17
# .. .. .. ..
# 70 71 .. 77
#


def alg_to_coord(alg):
    rank = 8 - int(alg[1])        # 0-7
    file = ord(alg[0]) - ord('a') # 0-7
    return rank, file


def coord_to_alg(coord):
    letter = chr(ord('a') + coord[1])
    number = str(8 - coord[0])
    return letter + number


def to_planes(fen):
    board_state = replace_tags_board(fen)
    pieces_both = np.zeros(shape=(12, 8, 8), dtype=np.float32)
    for rank in range(8):
        for file in range(8):
            v = board_state[rank * 8 + file]
            if v.isalpha():
                pieces_both[ind[v]][rank][file] = 1
    assert pieces_both.shape == (12, 8, 8)
    return pieces_both


def replace_tags_board(board_san):
    board_san = board_san.split(" ")[0]
    board_san = board_san.replace("2", "11")
    board_san = board_san.replace("3", "111")
    board_san = board_san.replace("4", "1111")
    board_san = board_san.replace("5", "11111")
    board_san = board_san.replace("6", "111111")
    board_san = board_san.replace("7", "1111111")
    board_san = board_san.replace("8", "11111111")
    return board_san.replace("/", "")


def is_black_turn(fen):
    return fen.split(" ")[1] == 'b'
