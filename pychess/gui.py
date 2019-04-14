# -*- coding: utf-8 -*- 
from .chess import *
from tkinter import Tk, Canvas, Button, BOTH, BOTTOM, PhotoImage
from tkinter.ttk import Frame
from PIL import Image, ImageTk
import os
import gc

path = os.path.dirname(os.path.abspath(__file__))

class ChessGUI(Frame):
    def __init__(self, master, game):
        super().__init__(master)
        self.game = game
        self.dark_cell = '#2c1b0f'
        self.light_cell = '#e7cba3'
        self.selected_cell = '#ecf27b'
        self.path_cell = '#82f47e'
        self.pieces = {}
        self.master = master
        self.player = 1
        self.moves_tmp = []
        self.input = []
        self.turnend = False
        self.__initUI()
        self.welcome()
    
    def __initUI(self):
        self.master.title("Python GUI Chess") 
        self.pack(fill=BOTH, expand=1)
        self.canvas = Canvas(self, width=64*8+100, height=64*8+100)
        self.canvas.pack(fill=BOTH, side=BOTTOM)
        self.load_image()
        self.init_board()
        self.draw_pieces(self.game.board)
        
    def load_image(self):
        for name in ['wPawn', 'wRook', 'wKnight', 'wBishop', 'wQueen', 'wKing', 'bPawn', 'bRook', 'bKnight', 'bBishop', 'bQueen', 'bKing']:
            self.pieces[name] = ImageTk.PhotoImage(Image.open(path+'/img/%s.png' %name))
    
    def init_board(self):
        self.canvas.create_rectangle(0,0,50+8*64+50,50+8*64+50,fill='#3c281a')
        self.canvas.create_rectangle(45,45,45+8*64+10,45+8*64+10,fill=self.light_cell)
        for i in range(8):
            for j in range(8):
                if i % 2 == 0:
                    self.canvas.create_rectangle(50+i*64, 50+j*64, 50+(i+1)*64, 50+(j+1)*64, fill=self.light_cell if j%2 == 0 else self.dark_cell)
                else:
                    self.canvas.create_rectangle(50+i*64, 50+j*64, 50+(i+1)*64, 50+(j+1)*64, fill=self.dark_cell if j%2 == 0 else self.light_cell)
        
        for h in [22,78+64*8]:
            for i, t in enumerate(['a','b','c','d','e','f','g','h']):
                self.canvas.create_text(80+64*i,h,text=t, font=('Arial', 14),fill='#636363',tags=('file'))
        for w in [22,78+64*8]:
            for i in range(8):
                self.canvas.create_text(w,80+64*i,text=str(8-i), font=('Arial', 14),fill='#636363',tags=('rank'))
        
    def update_board(self, r, c):
        if 0 <= r < 8 and 0 <= c < 8:
            self.canvas.delete('selected')
            self.canvas.delete('path')
            n = 8*(7-r)+c
            moves = [m for m in self.moves_tmp if m[0] == n]
            self.canvas.create_rectangle(50+c*64, 50+r*64, 50+(c+1)*64, 50+(r+1)*64, fill=self.selected_cell, tags=('selected'))
            if bool(moves):
                for move in moves:
                    i = self.game.getFileIdx(move[1])
                    j = 7-self.game.getRankIdx(move[1])
                    self.canvas.create_rectangle(50+i*64, 50+j*64, 50+(i+1)*64, 50+(j+1)*64, fill=self.path_cell, tags=('path'))
                self.draw_pieces(self.game.board)
            return moves
        return []

    def draw_pieces(self, board, flip=False):
        self.canvas.delete('piece')
        sym = ['wKing','wQueen','wRook','wKnight','wBishop','wPawn','bKing','bQueen','bRook','bKnight','bBishop','bPawn']
        for piece in range(12):
            tmp = int(board[piece])
            for num in reversed(range(64)):
                if tmp//pow(2,num) == 1:
                    n = int(self.game.ref['BoardNum'][num])
                    if not flip:
                        i = self.game.getFileIdx(n)
                        j = 7-self.game.getRankIdx(n)
                    else:
                        i = 7-self.getFileIdx(n)
                        j = self.getRankIdx(n)
                    self.canvas.create_image(82+i*64,82+j*64,image=self.pieces[sym[piece]], tags=(sym[piece], 'piece'), anchor='c')
                    tmp %= pow(2,num)
                    if tmp == 0:
                        break
    
    def welcome(self):
        self.canvas.unbind("<Button-1>")
        self.canvas.bind("<Button-1>", self.__click_welcome)
        self.canvas.create_oval(50+64*1.5, 50+64*1.5, 50+64*6.5, 50+64*6.5,tags="welcome", fill="orange", outline="white")
        self.canvas.create_text(50+64*4, 50+64*4,text="Welcome!", tags="welcome",fill="white", font=("Arial", 32))
        self.canvas.create_text(50+64*4, 50+64*5.5,text="New Game", tags="welcome",fill="white", font=("Arial", 16))
        self.master.mainloop()

    def __click_welcome(self, event):
        x, y = event.x, event.y
        if 278 < x < 335 and 394 < y < 410:
            # New Game
            self.canvas.delete('welcome')
            self.game.initBoard(self.game.board)
            self.main()

    def turnGUI(self):
        while not self.turnend:
            self.canvas.unbind("<Button-1>")
            self.canvas.bind("<Button-1>", self.__click_turn)
            self.master.update()
        self.turnend = False

    def __click_turn(self, event):
        x, y = event.x, event.y
        j = (x-50)//64
        i = (y-50)//64
        n = 8*(7-i)+j
        if len([m for m in self.input if m[1] == n]) == 1:
            move = [m for m in self.input if m[1] == n][0]
            self.game.move(self.game.board, self.player, move)
            self.input = []
            self.draw_pieces(self.game.board)
            self.turnend = True
            return                
        else:
            self.input = self.update_board(i,j)   

    def victory(self, name):
        self.canvas.unbind("<Button-1>")
        self.canvas.bind("<Button-1>", self.__click_victory)
        self.canvas.create_oval(50+64*1.5, 50+64*1.5, 50+64*6.5, 50+64*6.5,tags="victory", fill="orange", outline="white")
        self.canvas.create_text(50+64*4, 50+64*4,text="%s win!" %name, tags="victory",fill="white", font=("Arial", 32))
        self.canvas.create_text(50+64*4, 50+64*5,text="New Game", tags="victory",fill="white", font=("Arial", 14))
        self.canvas.create_text(50+64*4, 50+64*6,text="Exit", tags="victory",fill="white", font=("Arial", 14))
        self.master.mainloop()
    
    def __click_victory(self, event):
        x, y = event.x, event.y
        if 260 < x < 352 and 364 < y < 378:
            # New Game
            self.canvas.delete('victory')
            self.game.initBoard()
            self.main()            
        elif 290 < x < 324 and 427 < y < 439:
            # Exit
            self.master.quit()

    def main(self):
        while not self.game.finished(self.game.board, self.player):
            self.master.update()
            self.moves_tmp = self.game.nextMoves(self.game.board,self.player) 
            if not self.moves_tmp:
                break
            self.turnGUI()
            self.draw_pieces(self.game.board)
            self.player *= -1
        self.player *= -1
        if self.player == self.game.white:
            self.victory('White')
        if self.player == self.game.black:
            self.victory('Black')
        gc.collect()
        self.master.mainloop()

def main():
    gui = ChessGUI(Tk(),Chess())
    gui.main()
        
if __name__ == '__main__':
    main()
