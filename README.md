## How to play

Run `main.py` with python

#### Requirements

* python 3.10

#### Optional requrements

* termcolor (color support)
* tabulate (nicer looking tables)

### How do change language

The game looks for `language/default.json` and picks `language/english.json` if it can't find it.

To change language, either

1. Copy the language file of your choice
1. Name the copy `default.json`
1. Place the copy in the `language/` directory

or

1. Make a symlink in the directory `language/` called `default.json` pointing to your language file
