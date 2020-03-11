# -*- coding: utf-8 -*- 
from .alpha_zero.env import ChessEnv
from .alpha_zero.manager import get_player
from .alpha_zero.config import Config, PlayWithHumanConfig
from tkinter import Tk, Canvas, Button, BOTH, BOTTOM, PhotoImage
from tkinter.ttk import Frame
from PIL import Image, ImageTk
import os, sys
import multiprocessing as mp
import argparse

path = os.path.dirname(os.path.abspath(__file__))

class ChessGUI(Frame):
    def __init__(self, master, env, args):
        super().__init__(master)
        config = Config()
        PlayWithHumanConfig().update_play_config(config.play)
        self.args = args
        self.agent = get_player(config)
        self.env = env.reset()
        self.dark_cell = '#2c1b0f'
        self.light_cell = '#e7cba3'
        self.selected_cell = '#ecf27b'
        self.path_cell = '#82f47e'
        self.pieces = {}
        self.master = master
        self.turn = 1
        self.moves_tmp = []
        self.input = None
        self.turnend = False
        self.__initUI__()
        self.welcome()
    
    def __initUI__(self):
        self.master.title("Python Chess") 
        self.pack(fill=BOTH, expand=1)
        self.canvas = Canvas(self, width=64*8+100, height=64*8+100)
        self.canvas.pack(fill=BOTH, side=BOTTOM)
        self.load_image()
        self.init_board()
        self.draw_pieces(self.env.bitboard())
        
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

    def draw_pieces(self, board, flip=False):
        self.canvas.delete('piece')
        sym = ['wKing','wQueen','wRook','wKnight','wBishop','wPawn','bKing','bQueen','bRook','bKnight','bBishop','bPawn']
        for piece in range(12):
            tmp = int(board[piece])
            for num in reversed(range(64)):
                if tmp//pow(2,num) == 1:
                    n = int(self.env.board_idx[num])
                    if not flip:
                        i = self.env.getFileIdx(n)
                        j = 7-self.env.getRankIdx(n)
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
            self.env.reset()
            self.main(self.args)

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
        if self.input is not None:
            n = self.update_board(i,j)   
            words = self.env.num_to_name[self.input]+self.env.num_to_name[n]
            print(words)
            try:
                self.env.step(words, True)
            except:
                self.input = None
                self.canvas.delete('selected')
                return 
            self.input = None
            self.draw_pieces(self.env.bitboard())
            self.turnend = True
            return                
        else:
            self.input = self.update_board(i,j, False)   

    def update_board(self, r, c, moved=True):
        if 0 <= r < 8 and 0 <= c < 8:
            self.canvas.delete('selected')
            # self.canvas.delete('path')
            n = 8*(7-r)+c
            if not moved:
                self.canvas.create_rectangle(50+c*64, 50+r*64, 50+(c+1)*64, 50+(r+1)*64, fill=self.selected_cell, tags=('selected'))
            else:
                self.canvas.create_rectangle(50+c*64, 50+r*64, 50+(c+1)*64, 50+(r+1)*64, fill=self.path_cell, tags=('selected'))
            # if bool(moves):
            #     for move in moves:
            #         i = self.env.getFileIdx(move[1])
            #         j = 7-self.env.getRankIdx(move[1])
            #         self.canvas.create_rectangle(50+i*64, 50+j*64, 50+(i+1)*64, 50+(j+1)*64, fill=self.path_cell, tags=('path'))
            self.draw_pieces(self.env.bitboard())
            return n
        return None

    def victory(self, name):
        self.canvas.unbind("<Button-1>")
        self.canvas.bind("<Button-1>", self.__click_victory)
        self.canvas.create_oval(50+64*1.5, 50+64*1.5, 50+64*6.5, 50+64*6.5,tags="victory", fill="orange", outline="white")
        self.canvas.create_text(50+64*4, 50+64*4,text=f"{name}", tags="victory",fill="white", font=("Arial", 32))
        self.canvas.create_text(50+64*4, 50+64*5,text="New Game", tags="victory",fill="white", font=("Arial", 16))
        self.canvas.create_text(50+64*4, 50+64*6,text="Exit", tags="victory",fill="white", font=("Arial", 16))
        self.master.mainloop()
    
    def __click_victory(self, event):
        x, y = event.x, event.y
        if 260 < x < 352 and 364 < y < 378:
            # New Game
            self.canvas.delete('victory')
            self.env.reset()
            self.draw_pieces(self.env.bitboard())
            self.turn = 1
            self.main()            
        elif 290 < x < 324 and 427 < y < 439:
            # Exit
            self.master.quit()
            self.master.destroy()

    def main(self, args):
        while True:
            self.master.update()
            if self.env.winner is not None:
                self.victory(f"{str(self.env.winner).split('.')[1]} wins!")
                break
            if (self.turn == 1 or args.mode == 2) and args.mode != 1:
                if args.assist:
                    action = self.agent.action(self.env, False)
                    n = self.env.name_to_num[action[2:4]]
                    i = self.env.getFileIdx(n)
                    j = 7-self.env.getRankIdx(n)
                    self.update_board(j, i)
                self.turnGUI()
                self.turn *= -1
            else:
                action = self.agent.action(self.env, False)
                n = self.env.name_to_num[action[2:4]]
                i = self.env.getFileIdx(n)
                j = 7-self.env.getRankIdx(n)
                self.update_board(j, i)
                self.env.step(action, True)
                self.turn *= -1
            self.draw_pieces(self.env.bitboard())
        self.master.mainloop()

def main():
    parser = argparse.ArgumentParser(description='PyChess: Python Chess with pretraind AlphaZero')
    parser.add_argument('-g', '--gui', type=bool, default=True, help='Use GUI version of PyChess. Default: True')
    parser.add_argument('-i', '--assist', type=bool, default=False, help='Enable AI assist for human player. Default: False')
    parser.add_argument('-m', '--mode', type=int, default=0, choices=[0,1,2], help='Play mode: 0 - human vs AI, 1 - AI vs AI, 2 - human vs human')
    args = parser.parse_args()

    mp.set_start_method('spawn')
    sys.setrecursionlimit(10000)
    if args.gui:
        gui = ChessGUI(Tk(),ChessEnv(), args)
    else:    
        from .alpha_zero import manager
        manager.start()

if __name__ == '__main__':
    main()