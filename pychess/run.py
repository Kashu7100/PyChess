import os
import sys
import multiprocessing as mp

def main():
    print('Python Chess')
    print('[*] Usage: newgame, help, quit')
    print('[*] >>> Example:')
    print('[*] >>> Player: c2c4')
    mp.set_start_method('spawn')
    sys.setrecursionlimit(10000)
    from .alpha_zero import manager
    manager.start()

if __name__ == "__main__":
    main()