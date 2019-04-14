# -*- coding: utf-8 -*- 
import numpy as np
import os
import sys
import gc

path = os.path.dirname(os.path.abspath(__file__))

# bitboard np.array((12),dtype=uint64)
# 64 bit array, one bit per board position
# [WhiteKing,WhiteQueen,WhiteRooks,WhiteKnights,WhiteBishops,WhitePawns,
#  BlackKing,BlackQueen,BlackRooks,BlackKnights,BlackBishops,BlackPawns]
# 
# board index
# [[ 56 57 58 59 60 61 62 63
#    48 49 50 51 52 53 54 55
#    40 41 42 43 44 45 46 47
#    32 33 34 35 36 37 38 39
#    24 25 26 27 28 29 30 31
#    16 17 18 19 20 21 22 23
#    8  9  10 11 12 13 14 15 
#    0  1  2  3  4  5  6  7 ]]
#
# board representation in bits
# [56 57 58 59 60 61 62 63 48 49 50 51 52 53 54 55 40 41 42 43 44 45 46 47 32 33 34 35 36 37 38 39 24 25 26 27 28 29 30 31 16 17 18 19 20 21 22 23 8  9  10 11 12 13 14 15 0  1  2  3  4  5  6  7]

class Chess(object):
    def __init__(self):
        self.board = np.zeros((14),dtype=np.uint64)
        self.boards = [np.zeros((14),dtype=np.uint64)]
        self.ref = {}
        self.history = []
        self.white = 1
        self.black = -1
        self.empty = -1
        self.wKing = 0
        self.wQueen = 1
        self.wRooks = 2
        self.wKnights = 3
        self.wBishops = 4
        self.wPawns = 5
        self.bKing = 6
        self.bQueen = 7
        self.bRooks = 8
        self.bKnights = 9
        self.bBishops = 10
        self.bPawns = 11
        self.casling = 12
        self.en_passant = 13
        self.initBoard(self.board)
        self.initLookupTable()
        self.history.append(self.board)

    def save(self, filename='log.txt'):
        print('[*] Saving history...')
        with open(path+'/'+filename, 'w') as file:
            for i in self.history:
                file.write(self.moveToname(i))
    
    def load(self, filename='log.txt'):
        print('[*] Start loading ...')
        with open(path+'/'+filename, 'r') as file:
            history = file.readlines()
        moves = []
        for name in history:
            moves.append(self.nameTomove(name))
        self.initBoard(self.boards[0])
        for i, move in enumerate(moves):
            self.boards.append(self.move(self.boards[i].copy(),pow(-1,i),move))
        print('[*] Loading completed.')

    def initBoard(self, board):
        board[self.wKing] = self.posToint(4)
        board[self.wQueen] = self.posToint(3)
        board[self.wRooks] = self.posToint([0,7])
        board[self.wKnights] = self.posToint([1,6])
        board[self.wBishops] = self.posToint([2,5])
        board[self.wPawns] = self.posToint([i for i in range(8,16)])
        board[self.bKing] = self.posToint(60)
        board[self.bQueen] = self.posToint(59)
        board[self.bRooks] = self.posToint([56,63])
        board[self.bKnights] = self.posToint([57,62])
        board[self.bBishops] = self.posToint([58,61])
        board[self.bPawns] = self.posToint([i for i in range(48,56)])
        board[self.casling] = self.posToint([2,6,58,62])
    
    def initLookupTable(self):
        self.ref['BoardNum'] = np.array([ 7, 6, 5, 4, 3, 2, 1, 0,
                                         15,14,13,12,11,10, 9, 8,
                                         23,22,21,20,19,18,17,16,
                                         31,30,29,28,27,26,25,24,
                                         39,38,37,36,35,34,33,32,
                                         47,46,45,44,43,42,41,40,
                                         55,54,53,52,51,50,49,48,
                                         63,62,61,60,59,58,57,56])
        self.ref['NameToNum'] = {'a1': 0,'b1': 1,'c1': 2,'d1': 3,'e1': 4,'f1': 5,'g1': 6,'h1': 7,
                                 'a2': 8,'b2': 9,'c2':10,'d2':11,'e2':12,'f2':13,'g2':14,'h2':15,
                                 'a3':16,'b3':17,'c3':18,'d3':19,'e3':20,'f3':21,'g3':22,'h3':23,
                                 'a4':24,'b4':25,'c4':26,'d4':27,'e4':28,'f4':29,'g4':30,'h4':31, 
                                 'a5':32,'b5':33,'c5':34,'d5':35,'e5':36,'f5':37,'g5':38,'h5':39,
                                 'a6':40,'b6':41,'c6':42,'d6':43,'e6':44,'f6':45,'g6':46,'h6':47,
                                 'a7':48,'b7':49,'c7':50,'d7':51,'e7':52,'f7':53,'g7':54,'h7':55,
                                 'a8':56,'b8':57,'c8':58,'d8':59,'e8':60,'f8':61,'g8':62,'h8':63}
        self.ref['NumToName'] = dict([[v,k] for k,v in self.ref['NameToNum'].items()])
        self.ref['MaskRank'] = np.zeros((8),dtype=np.uint64)
        self.ref['MaskRank'][0] = self.posToint([0,1,2,3,4,5,6,7])          # Mask Rank 1
        self.ref['MaskRank'][1] = self.posToint([8,9,10,11,12,13,14,15])    # Mask Rank 2
        self.ref['MaskRank'][2] = self.posToint([16,17,18,19,20,21,22,23])  # Mask Rank 3
        self.ref['MaskRank'][3] = self.posToint([24,25,26,27,28,29,30,31])  # Mask Rank 4
        self.ref['MaskRank'][4] = self.posToint([32,33,34,35,36,37,38,39])  # Mask Rank 5
        self.ref['MaskRank'][5] = self.posToint([40,41,42,43,44,45,46,47])  # Mask Rank 6
        self.ref['MaskRank'][6] = self.posToint([48,49,50,51,52,53,54,55])  # Mask Rank 7
        self.ref['MaskRank'][7] = self.posToint([56,57,58,59,60,61,62,63])  # Mask Rank 8
        self.ref['ClearRank'] = np.zeros((8),dtype=np.uint64)
        self.ref['ClearRank'][0] = self.reverse(self.posToint([0,1,2,3,4,5,6,7]))         # Clear Rank 1
        self.ref['ClearRank'][1] = self.reverse(self.posToint([8,9,10,11,12,13,14,15]))   # Clear Rank 2
        self.ref['ClearRank'][2] = self.reverse(self.posToint([16,17,18,19,20,21,22,23])) # Clear Rank 3
        self.ref['ClearRank'][3] = self.reverse(self.posToint([24,25,26,27,28,29,30,31])) # Clear Rank 4
        self.ref['ClearRank'][4] = self.reverse(self.posToint([32,33,34,35,36,37,38,39])) # Clear Rank 5
        self.ref['ClearRank'][5] = self.reverse(self.posToint([40,41,42,43,44,45,46,47])) # Clear Rank 6
        self.ref['ClearRank'][6] = self.reverse(self.posToint([48,49,50,51,52,53,54,55])) # Clear Rank 7
        self.ref['ClearRank'][7] = self.reverse(self.posToint([56,57,58,59,60,61,62,63])) # Clear Rank 8
        self.ref['MaskFile'] = np.zeros((8),dtype=np.uint64)
        self.ref['MaskFile'][0] = self.posToint([0,8,16,24,32,40,48,56])   # Mask File A
        self.ref['MaskFile'][1] = self.posToint([1,9,17,25,33,41,49,57])   # Mask File B
        self.ref['MaskFile'][2] = self.posToint([2,10,18,26,34,42,50,58])  # Mask File C
        self.ref['MaskFile'][3] = self.posToint([3,11,19,27,35,43,51,59])  # Mask File D
        self.ref['MaskFile'][4] = self.posToint([4,12,20,28,36,44,52,60])  # Mask File E
        self.ref['MaskFile'][5] = self.posToint([5,13,21,29,37,45,53,61])  # Mask File F
        self.ref['MaskFile'][6] = self.posToint([6,14,22,30,38,46,54,62])  # Mask File G
        self.ref['MaskFile'][7] = self.posToint([7,15,23,31,39,47,55,63])  # Mask File H
        self.ref['ClearFile'] = np.zeros((8),dtype=np.uint64)
        self.ref['ClearFile'][0] = self.reverse(self.posToint([0,8,16,24,32,40,48,56]))  # Clear File A
        self.ref['ClearFile'][1] = self.reverse(self.posToint([1,9,17,25,33,41,49,57]))  # Clear File B
        self.ref['ClearFile'][2] = self.reverse(self.posToint([2,10,18,26,34,42,50,58])) # Clear File C
        self.ref['ClearFile'][3] = self.reverse(self.posToint([3,11,19,27,35,43,51,59])) # Clear File D
        self.ref['ClearFile'][4] = self.reverse(self.posToint([4,12,20,28,36,44,52,60])) # Clear File E
        self.ref['ClearFile'][5] = self.reverse(self.posToint([5,13,21,29,37,45,53,61])) # Clear File F
        self.ref['ClearFile'][6] = self.reverse(self.posToint([6,14,22,30,38,46,54,62])) # Clear File G
        self.ref['ClearFile'][7] = self.reverse(self.posToint([7,15,23,31,39,47,55,63])) # Clear File H
        self.ref['MaskDiagonal1'] = np.zeros((15),dtype=np.uint64)
        self.ref['MaskDiagonal1'][0] = self.posToint(56)                        # Mask Diagonal / A8
        self.ref['MaskDiagonal1'][1] = self.posToint([57,48])                   # Mask Diagonal / B8~A7
        self.ref['MaskDiagonal1'][2] = self.posToint([58,49,40])                # Mask Diagonal / C8~A6
        self.ref['MaskDiagonal1'][3] = self.posToint([59,50,41,32])             # Mask Diagonal / D8~A5
        self.ref['MaskDiagonal1'][4] = self.posToint([60,51,42,33,24])          # Mask Diagonak / E8~A4
        self.ref['MaskDiagonal1'][5] = self.posToint([61,52,43,34,25,16])       # Mask Diagonak / F8~A3
        self.ref['MaskDiagonal1'][6] = self.posToint([62,53,44,35,26,17,8])     # Mask Diagonal / G8~A2
        self.ref['MaskDiagonal1'][7] = self.posToint([63,54,45,36,27,18,9,0])   # Mask Diagonal / H8~A1
        self.ref['MaskDiagonal1'][8] = self.posToint([55,46,37,28,19,10,1])     # Mask Diagonal / H7~B1
        self.ref['MaskDiagonal1'][9] = self.posToint([47,38,29,20,11,2])        # Mask Diagonal / H6~C1
        self.ref['MaskDiagonal1'][10] = self.posToint([39,30,21,12,3])          # Mask Diagonal / H5~D1
        self.ref['MaskDiagonal1'][11] = self.posToint([31,22,13,4])             # Mask Diagonal / H4~E1
        self.ref['MaskDiagonal1'][12] = self.posToint([23,14,5])                # Mask Diagonal / H3~F1
        self.ref['MaskDiagonal1'][13] = self.posToint([15,6])                   # Mask Diagonal / H2~G1
        self.ref['MaskDiagonal1'][14] = self.posToint(7)                        # Mask Diagonal / H1
        self.ref['ClearDiagonal1'] = np.zeros((15),dtype=np.uint64)
        self.ref['ClearDiagonal1'][0] = self.reverse(self.posToint(56))                        # Clear Diagonal / A8
        self.ref['ClearDiagonal1'][1] = self.reverse(self.posToint([57,48]))                   # Clear Diagonal / B8~A7
        self.ref['ClearDiagonal1'][2] = self.reverse(self.posToint([58,49,40]))                # Clear Diagonal / C8~A6
        self.ref['ClearDiagonal1'][3] = self.reverse(self.posToint([59,50,41,32]))             # Clear Diagonal / D8~A5
        self.ref['ClearDiagonal1'][4] = self.reverse(self.posToint([60,51,42,33,24]))          # Clear Diagonak / E8~A4
        self.ref['ClearDiagonal1'][5] = self.reverse(self.posToint([61,52,43,34,25,16]))       # Clear Diagonak / F8~A3
        self.ref['ClearDiagonal1'][6] = self.reverse(self.posToint([62,53,44,35,26,17,8]))     # Clear Diagonal / G8~A2
        self.ref['ClearDiagonal1'][7] = self.reverse(self.posToint([63,54,45,36,27,18,9,0]))   # Clear Diagonal / H8~A1
        self.ref['ClearDiagonal1'][8] = self.reverse(self.posToint([55,46,37,28,19,10,1]))     # Clear Diagonal / H7~B1
        self.ref['ClearDiagonal1'][9] = self.reverse(self.posToint([47,38,29,20,11,2]))        # Clear Diagonal / H6~C1
        self.ref['ClearDiagonal1'][10] = self.reverse(self.posToint([39,30,21,12,3]))          # Clear Diagonal / H5~D1
        self.ref['ClearDiagonal1'][11] = self.reverse(self.posToint([31,22,13,4]))             # Clear Diagonal / H4~E1
        self.ref['ClearDiagonal1'][12] = self.reverse(self.posToint([23,14,5]))                # Clear Diagonal / H3~F1
        self.ref['ClearDiagonal1'][13] = self.reverse(self.posToint([15,6]))                   # Clear Diagonal / H2~G1
        self.ref['ClearDiagonal1'][14] = self.reverse(self.posToint(7))                        # Clear Diagonal / H1
        self.ref['MaskDiagonal2'] = np.zeros((15),dtype=np.uint64)
        self.ref['MaskDiagonal2'][0] = self.posToint(0)                         # Mask Diagonal \ A1
        self.ref['MaskDiagonal2'][1] = self.posToint([8,1])                     # Mask Diagonal \ A2~B1
        self.ref['MaskDiagonal2'][2] = self.posToint([16,9,2])                  # Mask Diagonal \ A3~C1
        self.ref['MaskDiagonal2'][3] = self.posToint([24,17,10,3])              # Mask Diagonal \ A4~D1
        self.ref['MaskDiagonal2'][4] = self.posToint([32,25,18,11,4])           # Mask Diagonak \ A5~E1 
        self.ref['MaskDiagonal2'][5] = self.posToint([40,33,26,19,12,5])        # Mask Diagonak \ A6~F1
        self.ref['MaskDiagonal2'][6] = self.posToint([48,41,34,27,20,13,6])     # Mask Diagonal \ A7~G1
        self.ref['MaskDiagonal2'][7] = self.posToint([56,49,42,35,28,21,14,7])  # Mask Diagonal \ A8~H1
        self.ref['MaskDiagonal2'][8] = self.posToint([57,50,43,36,29,22,15])    # Mask Diagonal \ B8~H2
        self.ref['MaskDiagonal2'][9] = self.posToint([58,51,44,37,30,23])       # Mask Diagonal \ C8~H3
        self.ref['MaskDiagonal2'][10] = self.posToint([59,52,45,38,31])         # Mask Diagonal \ D8~H4
        self.ref['MaskDiagonal2'][11] = self.posToint([60,53,46,39])            # Mask Diagonal \ E8~H5
        self.ref['MaskDiagonal2'][12] = self.posToint([61,54,47])               # Mask Diagonal \ F8~H6
        self.ref['MaskDiagonal2'][13] = self.posToint([62,55])                  # Mask Diagonal \ G8~H7
        self.ref['MaskDiagonal2'][14] = self.posToint(63)                       # Mask Diagonal \ H8
        self.ref['ClearDiagonal2'] = np.zeros((15),dtype=np.uint64)
        self.ref['ClearDiagonal2'][0] = self.reverse(self.posToint(0))                         # Clear Diagonal \ A1
        self.ref['ClearDiagonal2'][1] = self.reverse(self.posToint([8,1]))                     # Clear Diagonal \ A2~B1
        self.ref['ClearDiagonal2'][2] = self.reverse(self.posToint([16,9,2]))                  # Clear Diagonal \ A3~C1
        self.ref['ClearDiagonal2'][3] = self.reverse(self.posToint([24,17,10,3]))              # Clear Diagonal \ A4~D1
        self.ref['ClearDiagonal2'][4] = self.reverse(self.posToint([32,25,18,11,4]))           # Clear Diagonak \ A5~E1 
        self.ref['ClearDiagonal2'][5] = self.reverse(self.posToint([40,33,26,19,12,5]))        # Clear Diagonak \ A6~F1
        self.ref['ClearDiagonal2'][6] = self.reverse(self.posToint([48,41,34,27,20,13,6]))     # Clear Diagonal \ A7~G1
        self.ref['ClearDiagonal2'][7] = self.reverse(self.posToint([56,49,42,35,28,21,14,7]))  # Clear Diagonal \ A8~H1
        self.ref['ClearDiagonal2'][8] = self.reverse(self.posToint([57,50,43,36,29,22,15]))    # Clear Diagonal \ B8~H2
        self.ref['ClearDiagonal2'][9] = self.reverse(self.posToint([58,51,44,37,30,23]))       # Clear Diagonal \ C8~H3
        self.ref['ClearDiagonal2'][10] = self.reverse(self.posToint([59,52,45,38,31]))         # Clear Diagonal \ D8~H4
        self.ref['ClearDiagonal2'][11] = self.reverse(self.posToint([60,53,46,39]))            # Clear Diagonal \ E8~H5
        self.ref['ClearDiagonal2'][12] = self.reverse(self.posToint([61,54,47]))               # Clear Diagonal \ F8~H6
        self.ref['ClearDiagonal2'][13] = self.reverse(self.posToint([62,55]))                  # Clear Diagonal \ G8~H7
        self.ref['ClearDiagonal2'][14] = self.reverse(self.posToint(63))                       # Clear Diagonal \ H8
        self.initBishopMask()
        self.initRookMask()

    def initBishopMask(self):
        self.ref['MaskBishop'] = np.zeros((64),dtype=np.uint64)
        for square in range(64):
            self.ref['MaskBishop'][square] |= self.ref['MaskDiagonal1'][self.getDiagonalIdx1(square)]
            self.ref['MaskBishop'][square] |= self.ref['MaskDiagonal2'][self.getDiagonalIdx2(square)]
            self.ref['MaskBishop'][square] &= self.reverse(self.posToint(square))

    def initRookMask(self):
        self.ref['MaskRook'] = np.zeros((64),dtype=np.uint64)
        for square in range(64):
            self.ref['MaskRook'][square] |= self.ref['MaskRank'][self.getRankIdx(square)]
            self.ref['MaskRook'][square] |= self.ref['MaskFile'][self.getFileIdx(square)]
            self.ref['MaskRook'][square] &= self.reverse(self.posToint(square))

    def moveToname(self, move):
        return self.ref['NumToName'][move[0]]+self.ref['NumToName'][move[1]]
    
    def nameTomove(self, name):
        return [self.ref['NameToNum'][name[0:2]],self.ref['NameToNum'][name[2:4]]]

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
    
    def getMoves(self, pos, movement):
        moves = []
        for i in reversed(range(64)):
            if int(movement)//pow(2,i) == 1:
                moves.append([int(pos),int(self.ref['BoardNum'][i])])
                movement = int(movement) % pow(2,i)
                if int(movement) == 0:
                    break
        return moves
    
    def getRankIdx(self, n):
        return n//8

    def getFileIdx(self, n):
        return n%8
    
    def getDiagonalIdx1(self, n):
        if n in [56]:
            return 0
        elif n in [57,48]:
            return 1
        elif n in [58,49,40]:
            return 2
        elif n in [59,50,41,32]:
            return 3
        elif n in [60,51,42,33,24]:
            return 4
        elif n in [61,52,43,34,25,16]:
            return 5
        elif n in [62,53,44,35,26,17,8]:
            return 6
        elif n in [63,54,45,36,27,18,9,0]:
            return 7
        elif n in [55,46,37,28,19,10,1]:
            return 8
        elif n in [47,38,29,20,11,2]:
            return 9
        elif n in [39,30,21,12,3]:
            return 10
        elif n in [31,22,13,4]:
            return 11
        elif n in [23,14,5]:
            return 12
        elif n in [15,6]:
            return 13
        elif n in [7]:
            return 14 
    
    def getDiagonalIdx2(self, n):
        if n in [0]:
            return 0 
        elif n in [8,1]:
            return 1    
        elif n in [16,9,2]:
            return 2            
        elif n in [24,17,10,3]:
            return 3            
        elif n in [32,25,18,11,4]:
            return 4           
        elif n in [40,33,26,19,12,5]:
            return 5        
        elif n in [48,41,34,27,20,13,6]:
            return 6     
        elif n in [56,49,42,35,28,21,14,7]:
            return 7  
        elif n in [57,50,43,36,29,22,15]:
            return 8  
        elif n in [58,51,44,37,30,23]:
            return 9      
        elif n in [59,52,45,38,31]:
            return 10        
        elif n in [60,53,46,39]:
            return 11            
        elif n in [61,54,47]:
            return 12               
        elif n in [62,55]:
            return 13             
        elif n in [63]:
            return 14  

    def getPiece(self, board, n):
        i = self.posToint(n)
        if board[self.wKing] & i > np.uint(0):
            return self.wKing
        elif board[self.wQueen] & i > np.uint(0):
            return self.wQueen
        elif board[self.wRooks] & i > np.uint(0):
            return self.wRooks
        elif board[self.wKnights] & i > np.uint(0):
            return self.wKnights
        elif board[self.wBishops] & i > np.uint(0):
            return self.wBishops
        elif board[self.wPawns] & i > np.uint(0):
            return self.wPawns
        elif board[self.bKing] & i > np.uint(0):
            return self.bKing
        elif board[self.bQueen] & i > np.uint(0):
            return self.bQueen
        elif board[self.bRooks] & i > np.uint(0):
            return self.bRooks
        elif board[self.bKnights] & i > np.uint(0):
            return self.bKnights
        elif board[self.bBishops] & i > np.uint(0):
            return self.bBishops
        elif board[self.bPawns] & i > np.uint(0):
            return self.bPawns
        else:
            return self.empty
    
    def getColor(self, piece):
        if piece in [self.wPawns,self.wRooks,self.wBishops,self.wKnights,self.wQueen,self.wKing]:
            return self.white
        elif piece in [self.bPawns,self.bRooks,self.bBishops,self.bKnights,self.bQueen,self.bKing]:
            return self.black
        else:
            return 0
    
    def ownSide(self, board, player):
        if player == self.white:
            return np.bitwise_or.reduce(board[:6])
        elif player == self.black:
            return np.bitwise_or.reduce(board[6:12])
    
    def allPieces(self, board):
        return np.bitwise_or.reduce(board[:12])

    def reverse(self, bitboard):
        return np.uint64(18446744073709551615) ^ np.uint64(bitboard)
    
    def movementKing(self, n, board, player):
        king_loc = self.posToint(n)
        king_loc_a = king_loc & self.ref['ClearFile'][0]
        king_loc_h = king_loc & self.ref['ClearFile'][7]
        king_cas = ((king_loc >> np.uint(2) | king_loc << np.uint(2)) & board[self.casling] & self.reverse(self.allPieces(board)) >> np.uint(1)) if n in [4,60] else np.uint(0)
        king_cas &= ((self.reverse(self.allPieces(board)) & self.ref['MaskFile'][3]) << np.uint(1) | king_loc >> np.uint(2))
        moves = king_cas | king_loc_a << np.uint(9) | king_loc << np.uint(8) | king_loc_h << np.uint(7) | king_loc_h >> np.uint(1) | king_loc_h >> np.uint(9) | king_loc >> np.uint(8) | king_loc_a >> np.uint(7) | king_loc_a << np.uint(1)
        return moves & (self.reverse(self.ownSide(board, player)))

    def movementKnight(self, n, board, player):
        knight_loc = self.posToint(n)
        knight_loc_ab = knight_loc & self.ref['ClearFile'][0] & self.ref['ClearFile'][1]
        knight_loc_a = knight_loc & self.ref['ClearFile'][0]
        knight_loc_h = knight_loc & self.ref['ClearFile'][7]
        knight_loc_gh = knight_loc & self.ref['ClearFile'][6] & self.ref['ClearFile'][7]
        moves = knight_loc_ab << np.uint(10) | knight_loc_a << np.uint(17) | knight_loc_h << np.uint(15) | knight_loc_gh << np.uint(6) | knight_loc_gh >> np.uint(10) | knight_loc_h >> np.uint(17) | knight_loc_a >> np.uint(15) | knight_loc_ab >> np.uint(6)
        return moves & (self.reverse(self.ownSide(board, player)))
    
    def movementPawn(self, n, board, player):
        pawn_loc = self.posToint(n)
        if player == self.white:
            pawn_one = (pawn_loc << np.uint(8)) & self.reverse(self.allPieces(board))
            pawn_two = (pawn_loc & self.ref['MaskRank'][1]) << np.uint(16) & self.reverse(self.allPieces(board)) if pawn_one > 0 else np.uint(0)
            pawn_left = (pawn_loc & self.ref['ClearFile'][0]) << np.uint(9) & self.ownSide(board, self.black)
            pawn_right = (pawn_loc & self.ref['ClearFile'][7]) << np.uint(7) & self.ownSide(board, self.black)
            pawn_en = ((pawn_loc & self.ref['ClearFile'][0]) << np.uint(9) | (pawn_loc & self.ref['ClearFile'][7]) << np.uint(7)) & board[self.en_passant]
        elif player == self.black:
            pawn_one = (pawn_loc >> np.uint(8)) & self.reverse(self.allPieces(board))
            pawn_two = (pawn_loc & self.ref['MaskRank'][6]) >> np.uint(16) & self.reverse(self.allPieces(board)) if pawn_one > 0 else np.uint(0)
            pawn_left = (pawn_loc & self.ref['ClearFile'][0]) >> np.uint(7)  & self.ownSide(board, self.white)
            pawn_right = (pawn_loc & self.ref['ClearFile'][7]) >> np.uint(9)  & self.ownSide(board, self.white)
            pawn_en = ((pawn_loc & self.ref['ClearFile'][0]) >> np.uint(7) | (pawn_loc & self.ref['ClearFile'][7]) >> np.uint(9)) & board[self.en_passant]
        return pawn_one | pawn_two | pawn_left | pawn_right | pawn_en
    
    def movementRook(self, n, board, player):
        result = self.ref['MaskRook'][n]
        occ = result & self.allPieces(board)
        rank = self.getRankIdx(n)
        file = self.getFileIdx(n)
        for i in range(rank+1,8):
            tmp = occ & self.ref['MaskRank'][i]
            if tmp > np.uint(0):
                for j in range(7,i,-1):
                    result &= self.ref['ClearRank'][j]
                break   
        for i in reversed(range(0,rank)):
            tmp = occ & self.ref['MaskRank'][i]
            if tmp > np.uint(0):
                for j in range(0,i):
                    result &= self.ref['ClearRank'][j]
                break    
        for i in range(file+1,8):
            tmp = occ & self.ref['MaskFile'][i]
            if tmp > np.uint(0):
                for j in range(7,i,-1):
                    result &= self.ref['ClearFile'][j]
                break 
        for i in reversed(range(0,file)):
            tmp = occ & self.ref['MaskFile'][i]
            if tmp > np.uint(0):
                for j in range(0,i):
                    result &= self.ref['ClearFile'][j]
                break
        return result & (self.reverse(self.ownSide(board, player)))    

    def movementBishop(self, n, board, player):
        result = self.ref['MaskBishop'][n]
        occ = result & self.allPieces(board)
        d1 = self.getDiagonalIdx1(n)
        d2 = self.getDiagonalIdx2(n)
        for i in range(d1-1,-1,-1):
            tmp = occ & self.ref['MaskDiagonal1'][i]
            if tmp > np.uint(0):
                for j in range(0,i):
                    result &= self.ref['ClearDiagonal1'][j]
                break
        for i in range(d1+1,15):
            tmp = occ & self.ref['MaskDiagonal1'][i]
            if tmp > np.uint(0):
                for j in range(14,i,-1):
                    result &= self.ref['ClearDiagonal1'][j]
                break
        for i in range(d2-1,-1,-1):
            tmp = occ & self.ref['MaskDiagonal2'][i]
            if tmp > np.uint(0):
                for j in range(0,i):
                    result &= self.ref['ClearDiagonal2'][j]
                break
        for i in range(d2+1,15):
            tmp = occ & self.ref['MaskDiagonal2'][i]
            if tmp > np.uint(0):
                for j in range(14,i,-1):
                    result &= self.ref['ClearDiagonal2'][j]
                break
        return result & (self.reverse(self.ownSide(board, player)))  

    def movementQueen(self, n, board, player):
        return self.movementRook(n, board, player) | self.movementBishop(n, board, player)

    # move: [n, next_n]
    def move(self, board, player, move):
        piece = self.getPiece(board, move[0])
        opponent = self.getPiece(board,move[1])
        if self.getColor(piece) is not player:
            raise Exception('Invalid movement.',move)
            #return None
        # capture
        if opponent != -1:
            board[opponent] ^= self.posToint(move[1])
        # pawn promotion
        if piece == self.wPawns and move[0] in range(48,56) and move[1] in range(56,64):
            board[self.wPawns] ^= self.posToint(move[0])
            board[self.wQueen] |= self.posToint(move[1])
            board[self.en_passant] = np.uint(0)
        elif piece == self.bPawns and move[0] in range(8,16) and move[1] in range(0,8):
            board[self.bPawns] ^= self.posToint(move[0])
            board[self.bQueen] |= self.posToint(move[1])
            board[self.en_passant] = np.uint(0)
        # en passant
        elif piece == self.wPawns and self.posToint(move[1]) == board[self.en_passant]:
            board[self.wPawns] ^= self.posToint(move[0])
            board[self.wPawns] |= self.posToint(move[1])
            board[self.bPawns] ^= (self.posToint(move[1]) >> np.uint(8))
            board[self.en_passant] = np.uint(0)
        elif piece == self.bPawns and self.posToint(move[1]) == board[self.en_passant]:
            board[self.bPawns] ^= self.posToint(move[0])
            board[self.bPawns] |= self.posToint(move[1])
            board[self.wPawns] ^= (self.posToint(move[1]) << np.uint(8))
            board[self.en_passant] = np.uint(0)
        # castling
        elif piece == self.wKing and move[0] == 4 and move[1] == 2:
            board[self.wKing] ^= self.posToint(move[0])
            board[self.wKing] |= self.posToint(move[1])
            board[self.wRooks] ^= self.posToint(0)
            board[self.wRooks] |= self.posToint(3)
            board[self.en_passant] = np.uint(0)
            board[self.casling] &= self.posToint([58,62])
        elif piece == self.wKing and move[0] == 4 and move[1] == 6:
            board[self.wKing] ^= self.posToint(move[0])
            board[self.wKing] |= self.posToint(move[1])
            board[self.wRooks] ^= self.posToint(7)
            board[self.wRooks] |= self.posToint(5)
            board[self.en_passant] = np.uint(0)
            board[self.casling] &= self.posToint([58,62])
        elif piece == self.bKing and move[0] == 60 and move[1] == 58:
            board[self.bKing] ^= self.posToint(move[0])
            board[self.bKing] |= self.posToint(move[1])
            board[self.bRooks] ^= self.posToint(56)
            board[self.bRooks] |= self.posToint(59)
            board[self.en_passant] = np.uint(0)
            board[self.casling] &= self.posToint([2,6])
        elif piece == self.bKing and move[0] == 60 and move[1] == 62:
            board[self.bKing] ^= self.posToint(move[0])
            board[self.bKing] |= self.posToint(move[1])
            board[self.bRooks] ^= self.posToint(63)
            board[self.bRooks] |= self.posToint(61)
            board[self.en_passant] = np.uint(0)
            board[self.casling] &= self.posToint([2,6])
        else:
            board[piece] ^= self.posToint(move[0])
            board[piece] |= self.posToint(move[1])
            board[self.en_passant] = np.uint(0)
            # en passant
            if piece == self.wPawns and move[0] in range(8,16) and move[1] in range(24,32):
                board[self.en_passant] |= (self.posToint(move[1]) >> np.uint(8))
            elif piece == self.bPawns and move[0] in range(48,56) and move[1] in range(32,40):
                board[self.en_passant] |= (self.posToint(move[1]) << np.uint(8))
            # castling
            elif piece == self.wKing and move[0] == 4:
                board[self.casling] &= self.posToint([58,62])
            elif piece == self.bKing and move[0] == 60:
                board[self.casling] &= self.posToint([2,6])
            elif piece == self.wRooks and move[0] == 0:
                board[self.casling] &= self.posToint([6,58,62])
            elif piece == self.wRooks and move[0] == 7:
                board[self.casling] &= self.posToint([2,58,62])
            elif piece == self.bRooks and move[0] == 56:
                board[self.casling] &= self.posToint([2,6,62])
            elif piece == self.bRooks and move[0] == 63:
                board[self.casling] &= self.posToint([2,6,58])
        return board
    
    def isCheck(self, board, player):
        if player == self.white:
            king = board[self.wKing]
        elif player == self.black:
            king = board[self.bKing]
        for i in range(64):
            piece = self.getPiece(board,i)
            if piece == self.empty or self.getColor(piece) != -player:
                continue
            elif piece in [self.wKing, self.bKing]:
                movement = self.movementKing(i,board,-player)
            elif piece in [self.wBishops, self.bBishops]:
                movement = self.movementBishop(i,board,-player)
            elif piece in [self.wKnights, self.bKnights]:
                movement = self.movementKnight(i,board,-player)
            elif piece in [self.wRooks, self.bRooks]:
                movement = self.movementRook(i,board,-player)
            elif piece in [self.wQueen, self.bQueen]:
                movement = self.movementQueen(i,board,-player)
            elif piece in [self.wPawns, self.bPawns]:
                movement = self.movementPawn(i,board,-player)
            if movement & king > np.uint(0):
                return True
        return False

    def nextMoves(self, board, player):
        moves = []
        for i in range(64):
            piece = self.getPiece(board,i)
            if piece == self.empty or self.getColor(piece) != player:
                continue
            elif piece in [self.wKing, self.bKing]:
                movement = self.movementKing(i,board,player)
            elif piece in [self.wBishops, self.bBishops]:
                movement = self.movementBishop(i,board,player)
            elif piece in [self.wKnights, self.bKnights]:
                movement = self.movementKnight(i,board,player)
            elif piece in [self.wRooks, self.bRooks]:
                movement = self.movementRook(i,board,player)
            elif piece in [self.wQueen, self.bQueen]:
                movement = self.movementQueen(i,board,player)
            elif piece in [self.wPawns, self.bPawns]:
                movement = self.movementPawn(i,board,player)
            for m in self.getMoves(i,movement):
                nextState = self.move(board.copy(),player,m)
                if not self.isCheck(nextState, player):
                    moves.append(m)
        gc.collect()
        return moves

    def finished(self, board, player):
        if player == self.white and board[self.wKing] == np.uint(0):
            return True
        if player == self.black and board[self.bKing] == np.uint(0):
            return True
        return False

    def drawBoard(self, board, player, flip=False):
        os.system('cls' if os.name == 'nt' else 'clear')
        print('turn: {}'.format('White' if player > 0 else 'Black'))
        b = board.copy()
        sym = ['K','Q','R','N','B','P','k','q','r','n','b','p']
        view = np.array([[' ' for _ in range(8)] for _ in range(8)], dtype=str)
        for piece in range(12):
            tmp = int(b[piece])
            for i in reversed(range(64)):
                if tmp//pow(2,i) == 1:
                    n = int(self.ref['BoardNum'][i])
                    if not flip:
                        view[7-self.getRankIdx(n)][self.getFileIdx(n)] = sym[piece]
                    else:
                        view[self.getRankIdx(n)][7-self.getFileIdx(n)] = sym[piece]
                    tmp %= pow(2,i)
                    if tmp == 0:
                        break
        for i, row in enumerate(view):
            print('  +---+---+---+---+---+---+---+---+')
            print('{} | {} | {} | {} | {} | {} | {} | {} | {} |'.format(8-i, *row))
        print('  +---+---+---+---+---+---+---+---+')
        print('    a   b   c   d   e   f   g   h')  
