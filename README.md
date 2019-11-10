<p align="center">
  <img src="assets/logo.png"/>
</p>

PyChess is a pure Python chess library with move generation and move validation.
PyChess uses a bitboard representation for its internal calculations.

## Overview

| Component | Description |
| ---- | --- |
| **pychess** | a python chess library |
| **pychess.chess** | the main chess class with bitboard representation dealing the all calculations |
| **pychess.gui** | draws beautiful GUI using tkinter for pychess |
| **pychess.img** | images used for GUI |

## Install 
```bash
$ pip install -v git+https://github.com/Kashu7100/PyChess.git
```
or
```bash
$ git clone https://github.com/Kashu7100/PyChess.git
$ cd PyChess
$ python setup.py install
```

## Play Game
Once PyChess is installed, one can use `chess` command to run the game.

```
$ chess
```

<p align="center">
  <img src="assets/chess.PNG" width="350" height="350"/>

  <img src="assets/selected.PNG" width="350" height="350"/>
</p>

## License

Source codes in the repository follows [MIT](http://www.opensource.org/licenses/MIT) license.
