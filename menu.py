from board import Board, Ship
from random import randint, choice
from time import sleep
import os
import csv
import json

SAVE_DIR = 'save_data'
PLAYER_SAVE_FILE = f'{SAVE_DIR}/player_board.csv'
ENEMY_SAVE_FILE = f'{SAVE_DIR}/enemy_board.csv'

language = None

def yes_no_input(message: str, yes_is_default: bool = True) -> bool:
    """Prompt the user a yes or no question.
    Returns True if answer is yes.
    Returns False if answer is no.
    Returns the default otherwise."""
    choices, short, verbose = language['yes is default'] if yes_is_default \
            else language['no is default']
    
#    if yes_is_default:
#        choices = 'Y/n'
#        short = 'n'
#        verbose = 'no'
#    else:
#        choices = 'y/N'
#        short = 'y'
#        verbose = 'yes'
    u_input = input(f'{message} [{choices}]\n> ').lower()
    if u_input == short or u_input == verbose:
        return not yes_is_default
    return yes_is_default

def print_boards(top_board: Board, bottom_board: Board):
    os.system('clear')
    print(top_board)
    print(bottom_board)

def player_shoot(player_board: Board, enemy_board: Board) -> bool:
    """Prompt the player to shoot at enemy board.
    Returns a bool indicating if it hit a ship or not."""
    u_input = input(f'{language["where to shoot"]}\n> ')
    if u_input.upper() == language['quit']:
        exit()
    if u_input.upper() == language['save']:
        if not os.path.exists(SAVE_DIR):
            os.makedirs(SAVE_DIR)
        write_board_to_file(PLAYER_SAVE_FILE, player_board.board)
        write_board_to_file(ENEMY_SAVE_FILE, enemy_board.board)
        enemy_board.info_text.append(language['save text'])
        # Exploiting the fact that a hit means you can shoot again
        return True
    x, y = u_input.split(' ')
    x = int(x)
    y = int(y)
    if x < 0 or y < 0:
        raise IndexError
    return enemy_board.shoot(x, y)

def ai_shoot(board: Board, not_hit: list[tuple[int,int]]) -> bool:
    x, y = choice(not_hit)
    not_hit.remove((x, y))
    hit = board.shoot(x, y)
    hit_str = language['hit'] if hit else language['miss']
    board.info_text.append(f'{hit_str} {x} {y}')
    free_space = board.h - len(board.info_text) - 3
    if free_space < 0:
        del board.info_text[:-free_space]
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
            x, y = u_input.split(' ')
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
    print('Placing ships, this may take a while.')
    err_msg = None
    ship_list = [4, 3, 3, 2, 2, 2, 1, 1, 1, 1]
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
        auto_placement(player_board) # Only for testing
        #manual_placement(player_board, enemy_board)
    auto_placement(enemy_board)
    return False

def bomb_phase(player_board: Board, enemy_board: Board) -> int:
    """Run the bomb phase of the game.
    Returns how many of the player's ship spaces has not been hit."""
    player_turn = True 
    not_hit_pl = [(x,y) for x in range(10) for y in range(10)]
    not_hit_en = [(x,y) for x in range(10) for y in range(10)]
    err_msg = None
    enemy_board.info_text = language['help text'] 
    # Game continues until either runs out of health
    while player_board.health() and enemy_board.health():
        print_boards(player_board, enemy_board)
        if err_msg:
            print(err_msg)
        if player_turn:
            try:
                player_turn = ai_shoot(enemy_board, not_hit_en) # Only for testing
                #player_turn = player_shoot(player_board, enemy_board)
            except ValueError:
                err_msg = language['invalid cordinates']
            except IndexError:
                err_msg = language['out of bound cordinates']
            else:
                del player_board.info_text[:]
                err_msg = None
        else:
            player_turn = not ai_shoot(player_board, not_hit_pl)
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

def save_stats(path: str, player_board: Board, enemy_board: Board):
    if player_board.health():
        winner = 'you'
        tries = enemy_board.shots_fired()
    else:
        winner = 'enemy'
        tries = player_board.shots_fired()
    with open(path, 'a') as f:
        f.write(f'{winner},{tries}\n')

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

def write_board_to_file(path: str, board: Board):
    with open(path, 'w') as f:
        for row in board:
            f.write(','.join(map(str, row)) + '\n')

def load_language(path):
    global language
    with open(path, 'r') as f:
        language = json.load(f)

def main():
    load_language('language/swedish.json')
    player_board = Board(hp_str = language['hp'],
                         shots_str = language['shots'])
    enemy_board = Board(hide = True,
                        hp_str = language['hp'],
                        shots_str = language['shots'])
    if os.path.exists(PLAYER_SAVE_FILE) and os.path.exists(ENEMY_SAVE_FILE) \
            and yes_no_input(language['save file exists']):
        place_from_file(PLAYER_SAVE_FILE, player_board)
        place_from_file(ENEMY_SAVE_FILE, enemy_board)
    else:
        while place_phase(player_board, enemy_board):
            pass
    bomb_phase(player_board, enemy_board)
    print_winner_message(player_board, enemy_board)
    save_stats('stats.csv', player_board, enemy_board)
    while save_ship_placement(player_board):
        pass


if __name__ == '__main__':
    main()
