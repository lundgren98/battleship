from db import Data
from board import Board, Ship
from getpass import getpass
import hashlib
from random import randint, choice
from time import sleep
from datetime import datetime
import os
import csv
import json
# Optional modules
try:
    from tabulate import tabulate
    TABULATE = True
except ModuleNotFoundError:
    TABULATE = False
try:
    from readchar import readkey, key
    READCHAR = True
except ModuleNotFoundError:
    READCHAR = False

SAVE_DIR = 'save_data'
PLAYER_SAVE_FILE = f'{SAVE_DIR}/player_board.csv'
ENEMY_SAVE_FILE = f'{SAVE_DIR}/enemy_board.csv'
MOVES_SAVE_FILE = f'{SAVE_DIR}/moves.json'

language = None
moves = []

def yes_no_input(message: str, yes_is_default: bool = True) -> bool:
    """Prompt the user a yes or no question.
    Returns True if answer is yes.
    Returns False if answer is no.
    Returns the default otherwise."""
    choices, short, verbose = language['yes is default'] if yes_is_default \
            else language['no is default']
    u_input = input(f'{message} [{choices}]\n> ').lower()
    if u_input == short or u_input == verbose:
        return not yes_is_default
    return yes_is_default

def print_boards(top_board: Board, bottom_board: Board):
    os.system('cls' if os.name == 'nt' else 'clear')
    print(top_board)
    print(bottom_board)

def player_shoot(player_board: Board, enemy_board: Board) -> bool:
    """Prompt the player to shoot at enemy board.
    Returns a bool indicating if it hit a ship and should be run again."""
    u_input = input(f'{language["where to shoot"]}\n> ')
    if u_input.upper() == language['quit']:
        exit()
    if u_input.upper() == language['save']:
        if not os.path.exists(SAVE_DIR):
            os.makedirs(SAVE_DIR)
        save_moves(MOVES_SAVE_FILE)
        write_board_to_file(PLAYER_SAVE_FILE, player_board.board)
        write_board_to_file(ENEMY_SAVE_FILE, enemy_board.board)
        enemy_board.info_text.append(language['save text'])
        # Didn't hit a ship, but we want to run again
        return True
    y, x = u_input.split(' ')
    x = int(x)
    y = int(y)
    if x < 0 or y < 0:
        raise IndexError
    r = enemy_board.shoot(x, y)
    global moves
    moves.append((x,y))
    return r

def ai_shoot(board: Board,
             not_hit: list[tuple[int,int]],
             last_hit: tuple[int,int] | None = None
             ) -> bool:
    aim = None
    if last_hit is not None:
        lx, ly = last_hit
        aim = list(set(not_hit).intersection({
            (lx - 1,ly),
            (lx + 1,ly),
            (lx,ly - 1),
            (lx,ly + 1)
            }))
    x, y = choice(aim if aim else not_hit)
    not_hit.remove((x, y))
    hit = board.shoot(x, y)
    hit_str = language['hit'] if hit else language['miss']
    board.info_text.append(f'{hit_str} {x} {y}')
    free_space = board.h - len(board.info_text) - 3
    if free_space < 0:
        del board.info_text[:-free_space]
    global moves
    moves.append((x,y))
    return hit

def pick_ship(ship_list: list[int],
              top_board: Board,
              bottom_board: Board
              ) -> int:
    valid_index = False
    err_msg = None
    ship_index = None
    ship_length = None
    while not valid_index:
        print_boards(top_board, bottom_board)
        for i, s in enumerate(ship_list):
            print(f'{i+1}\t' + '#'*s)
        if err_msg:
            print(err_msg)
        try:
            ship_index = int(input(f'{language["enter ship"]}\n> ')) - 1
            if ship_index < 0:
                raise IndexError
            ship_length = ship_list[ship_index]
        except (ValueError, IndexError):
            err_msg = language['invalid ship']
        else:
            valid_index = True
    del ship_list[ship_index]
    return ship_length

def pick_direction(top_board: Board, bottom_board: Board) -> str:
    direction = None
    while direction not in ['H', 'V']:
        print_boards(top_board, bottom_board)
        if direction is not None:
            print(language['invalid direction'])
        direction = input(f'{language["enter direction"]}\n> ').upper()
    return direction

def pick_cordinates(ship_list: list,
                    player_board: Board,
                    enemy_board: Board,
                    err_msg: str | None = None
                    ) -> tuple[int, int]:
    valid_cordinates = False
    cordinates = None
    while not valid_cordinates:
        print_boards(player_board, enemy_board)
        if err_msg:
            print(err_msg)
        try:
            u_input = input(f'{language["enter cordinates"]}\n> ')
            y, x = u_input.split(' ')
            cordinates = (int(x), int(y))
        except ValueError:
            err_msg = language['invalid cordinates']
            continue
        valid_cordinates = True
    return cordinates

def manual_placement(player_board: Board, enemy_board: Board):
    err_msg = None
    ship_list = [4, 3, 3, 2, 2, 2, 1, 1, 1, 1]
    while ship_list:
        ship_length = pick_ship(ship_list, player_board, enemy_board)
        direction = pick_direction(player_board, enemy_board)
        valid_cordinates = False
        err_msg = None
        while not valid_cordinates:
            cordinates = pick_cordinates(
                    ship_list, player_board, enemy_board, err_msg)
            ship = Ship(cordinates, direction, ship_length)
            try:
                valid_cordinates = player_board.place_ship(ship)
            except IndexError:
                valid_cordinates = False
            if not valid_cordinates:
                err_msg = language['cannot place ship'] 

def auto_placement(board: Board):
    print(language["placing ships"])
    err_msg = None
    ship_list = [1, 1, 1, 1, 2, 2, 2, 3, 3, 4]
    while ship_list:
        ship_length = ship_list.pop()
        valid_cordinates = False
        while not valid_cordinates:
            direction = choice(['V','H'])
            max_x = board.w
            max_y = board.h
            max_x -= 1 if direction == 'V' else ship_length
            max_y -= ship_length if direction == 'V' else 1
            x = randint(0,max_x)
            y = randint(0,max_y)
            cordinates = (x, y)
            ship = Ship(cordinates, direction, ship_length)
            try:
                valid_cordinates = board.place_ship(ship)
            except IndexError:
                valid_cordinates = False

def place_from_file(path: str, board: Board):
    """Set the board state according to file.
    Returns a bool indicating success."""
    board_state = []
    try:
        with open(path, 'r') as f:
            r = csv.reader(f)
            for row in r:
                board_state.append([int(x) for x in row])
    except FileNotFoundError:
        print(f'{language["no file"]} {path}')
    except ValueError:
        print(f'{language["invalid file"]} {path}')
    else:
        board.board = board_state
        return True
    return False

def place_phase(player_board: Board, enemy_board: Board) -> bool:
    """Returns a bool indicating if something went wrong."""
    if yes_no_input(language['load ship placement']):
        if not place_from_file(
                input(f'{language["file to read"]}: '),
                player_board):
            return True
    else:
        #auto_placement(player_board) # Only for testing
        manual_placement(player_board, enemy_board)
    auto_placement(enemy_board)
    return False

def show_replay(path: str):
    player_board = Board(hp_str = language['hp'],
                         shots_str = language['shots'])
    enemy_board = Board(hp_str = language['hp'],
                         shots_str = language['shots'])
    load_moves(f'{path}/moves.json')
    place_from_file(f'{path}/player_ships.csv', player_board)
    place_from_file(f'{path}/enemy_ships.csv', enemy_board)
    player_turn = True
    enemy_board.info_text = [language["press any key"]] if READCHAR \
            else [language["press enter"]]
    for cordinates in moves:
        print_boards(player_board, enemy_board)
        if READCHAR:
            k = readkey()
            if k == 'q':
                exit()
        else:
            input()
        if player_turn:
            player_turn = enemy_board.shoot(*(cordinates))
            hit_str = language['you hit'] if player_turn \
                    else language['you miss']
        else:
            player_turn = not player_board.shoot(*(cordinates))
            hit_str = language['miss'] if player_turn \
                    else language['hit']
        player_board.info_text.append(
                f'{hit_str} {" ".join([str(v) for v in cordinates])}')
        free_space = player_board.h - len(player_board.info_text) - 3
        if free_space < 0:
            del player_board.info_text[:-free_space]
    print_boards(player_board, enemy_board)
    exit()

def bomb_phase(player_board: Board, enemy_board: Board) -> int:
    """Run the bomb phase of the game.
    Returns how many of the player's ship spaces has not been hit."""
    global moves
    player_turn = True 
    not_hit_pl = [(x,y) for x in range(10) for y in range(10)]
    not_hit_en = [(x,y) for x in range(10) for y in range(10)]
    ai_last_hit = None
    err_msg = None
    enemy_board.info_text = language['help text'] 
    # Game continues until either runs out of health
    while player_board.health() and enemy_board.health():
        print_boards(player_board, enemy_board)
        if err_msg:
            print(err_msg)
        if player_turn:
            try:
                #player_turn = ai_shoot(enemy_board, not_hit_en) # Only for testing
                player_turn = player_shoot(player_board, enemy_board)
            except ValueError:
                err_msg = language['invalid cordinates']
            except IndexError:
                err_msg = language['out of bound cordinates']
            else:
                del player_board.info_text[:]
                err_msg = None
        else:
            ai_hit = ai_shoot(player_board, not_hit_pl, ai_last_hit)
            if ai_hit:
                ai_last_hit = moves[-1]
            player_turn = not ai_hit
    print_boards(player_board, enemy_board)
    return player_board.health()

def print_winner_message(player_board: Board, enemy_board: Board):
    if player_board.health():
        win_or_lose = language['win message']
        loser_board = enemy_board
    else:
        win_or_lose = language['lose message']
        loser_board = player_board
    print(' '.join([win_or_lose[0],
                    str(loser_board.shots_fired()),
                    win_or_lose[1]]))

def save_db_stats(db: Data, player_board: Board,
                  enemy_board: Board, player_name: str = 'guest'):
    if player_board.health():
        winner_health = player_board.health()
        winner = player_name
        loser = 'enemy'
        winner_tries = enemy_board.shots_fired()
        loser_tries = player_board.shots_fired()
    else:
        winner_health = enemy_board.health()
        winner = 'enemy'
        loser = player_name
        winner_tries = player_board.shots_fired()
        loser_tries = enemy_board.shots_fired()
    t = datetime.now().astimezone().isoformat(timespec='seconds')
    db.add_game(t, player_name, winner, loser,
                winner_tries, loser_tries, winner_health)

def save_ship_placement(board: Board) -> bool:
    """Promts the user to save the board's ship placements.
    Returns a bool indicating if something went wrong."""
    if not yes_no_input(language['save ship placement']):
        return False
    path = input(f'{language["file to write"]}: ')
    if os.path.exists(path):
        file_already_exists = ' '.join(
                [language['file already exists'][0],
                 path,
                 language['file already exists'][1]])
        if not yes_no_input(file_already_exists, False):
            return True
    #         Check for ships only
    ships = [[v & Board.SHIP for v in row] for row in board.board]
    write_board_to_file(path, ships)
    return False

def save_moves(path: str):
    with open(path, 'w') as f:
        json.dump(moves, f)

def write_board_to_file(path: str, board: Board):
    with open(path, 'w') as f:
        for row in board:
            f.write(','.join(map(str, row)) + '\n')

def save_replay(db: Data, player_board: Board, enemy_board: Board):
    game_id = tuple(db.max_game_id())[0][0]
    player_ships = [[v & Board.SHIP for v in row] for row in player_board.board]
    enemy_ships = [[v & Board.SHIP for v in row] for row in enemy_board.board]
    directory = f'{SAVE_DIR}/{game_id}'
    if not os.path.exists(directory):
        os.makedirs(directory)
    save_moves(f'{directory}/moves.json')
    write_board_to_file(f'{directory}/player_ships.csv', player_ships)
    write_board_to_file(f'{directory}/enemy_ships.csv', enemy_ships)

def load_moves(path: str):
    global moves
    with open(path, 'r') as f:
        moves = json.load(f)

def load_language(path):
    global language
    with open(path, 'r', encoding='utf-8') as f:
        language = json.load(f)

def replay_menu(db: Data, name: str = 'guest'):
    if not yes_no_input(language["show replay"], False):
        return False
    table = db.list_games(name)
    headers = language['table title']
    if TABULATE:
        print(tabulate(table, headers=headers))
    else:
        just = [4,10,10,10,10,11,10]
        s = [w.ljust(just[i]) for i, w in enumerate(headers)]
        print(''.join(s))
        print('-'*sum(just))
        for row in table:
            s = ''
            for i, item in enumerate(row):
                s += str(item).ljust(just[i])
            print(s)
    print(language["enter game id"])
    u_input = input('> ').upper()
    if u_input == language["dir"]:
        print(language["enter replay dir"], end='')
        replay_dir = input(': ')
    else:
        try:
            num = int(u_input)
        except ValueError:
            print(language["not an option"])
            return True
        replay_dir = f'{SAVE_DIR}/{num}'
    try:
        show_replay(replay_dir)
    except FileNotFoundError:
        print(language["no file"])
        return True

def login_menu(db: Data):
    for i, opt in enumerate(language["login menu"]):
        print(f'{i+1}. {opt}')
    u_input = input('> ')
    if u_input not in ['1','2','3']:
        print(language["not an option"])
        return None
    if u_input == '3':
        return 'guest'
    name = input(language["enter username"])
    pw = getpass(prompt=language["enter password"]).encode('utf-8')
    pw = hashlib.sha256(pw).hexdigest()
    if u_input == '1':
        exists = list(db.check_login(name, pw))[0][0]
        if exists:
            return name
        print(language["wrong login"])
        return None
    if u_input == '2':
        exists = list(db.check_login(name))[0][0]
        if exists:
            print(' '.join([language['user already exists'][0],
                            name,
                            language['user already exists'][1]]))
            return None
        db.add_player(name, pw)

def print_welcome_message(data: Data, name):
    count_wins = tuple(data.count_games(name, True))[0][0]
    if count_wins < 1:
        return
    count_games = tuple(data.count_games(name))[0][0]
    avg = tuple(data.avg_winner_shots(name))[0][0]
    pair_msg = [f'{name}!\n', count_wins, count_games, avg]
    for i, msg in enumerate(pair_msg):
        print(f'{language["welcome message"][i]} {msg}', end=' ')
    print()


def main():
    data = Data('stats.db')
    if os.path.exists('language/default.json'):
        load_language('language/default.json')
    else:
        load_language('language/english.json')

    while not (name := login_menu(data)):
        pass
    print_welcome_message(data, name)
    while replay_menu(data, name):
        pass

    player_board = Board(hp_str = language['hp'],
                         shots_str = language['shots'])
    enemy_board = Board(hide = True,
                        hp_str = language['hp'],
                        shots_str = language['shots'])
    if os.path.exists(PLAYER_SAVE_FILE) and os.path.exists(ENEMY_SAVE_FILE) \
            and yes_no_input(language['save file exists']):
        load_moves(MOVES_SAVE_FILE)
        place_from_file(PLAYER_SAVE_FILE, player_board)
        place_from_file(ENEMY_SAVE_FILE, enemy_board)
    else:
        while place_phase(player_board, enemy_board):
            pass
    bomb_phase(player_board, enemy_board)
    print_winner_message(player_board, enemy_board)
    save_db_stats(data, player_board, enemy_board, name)
    save_replay(data, player_board, enemy_board)
    while save_ship_placement(player_board):
        pass


if __name__ == '__main__':
    main()
