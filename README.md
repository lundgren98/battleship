## About

Battleship is a two player game where oponents take turns trying to shoot down
eachother's ships.

In this version of the game you are playing against the computer.

## How to play

Run `main.py` with python

### Placement phase

![pick ship](images/pick_ship.png)

Pick one of the numbered ships.

![pick direction](images/pick_direction.png)

Choose if you want to place it vertically or horizontally.

![pick cordinates](images/pick_cordinates.png)

And place it with cordinates `ROW` `COLUMN`.

![pick ship again](images/pick_ship_2.png)

### Bomb phase

![shoot ship](images/bomb.png)

![shoot ship again](images/bomb2.png)

Type in the cordinates where you want to shoot.
If it's a hit, you can shoot again.

![You won](images/win.png)

You win the game when all the oponents ships have been shot down.

#### Requirements

* python 3.10

#### Optional requrements

* [termcolor](https://pypi.org/project/termcolor/) (color support)
* [tabulate](https://pypi.org/project/tabulate/) (nicer looking tables)
* [readchar](https://pypi.org/project/readchar/) (press any key when viewing replays)

### How to change language

The game looks for `language/default.json` and picks `language/english.json` if it can't find it.

To change language, either

1. Copy the language file of your choice
1. Name the copy `default.json`
1. Place the copy in the `language/` directory

or

1. Make a symlink in the directory `language/` called `default.json` pointing to your language file
