from board import Board, Ship
from random import randint, choice
from time import sleep
import os
import csv

SAVE_DIR = 'save_data'
PLAYER_SAVE_FILE = f'{SAVE_DIR}/player_board.csv'
ENEMY_SAVE_FILE = f'{SAVE_DIR}/enemy_board.csv'

def yes_no_input(message, yes_is_default = True):
    if yes_is_default:
        choices = 'Y/n'
        short = 'n'
        verbose = 'no'
    else:
        choices = 'y/N'
        short = 'y'
        verbose = 'yes'
    u_input = input(f'{message} [{choices}]\n> ').lower()
    if u_input == short or u_input == verbose:
        return not yes_is_default
    return yes_is_default

def print_boards(top_board, bottom_board):
    os.system('clear')
    print(top_board)
    print(bottom_board)

def player_shoot(player_board, enemy_board):
    u_input = input('Where to shoot?\n> ')
    if u_input.lower() == 'quit':
        exit()
    if u_input.lower() == 'save':
        if not os.path.exists(SAVE_DIR):
            os.makedirs(SAVE_DIR)
        write_board_to_file(PLAYER_SAVE_FILE,
                            player_board.board)
        write_board_to_file(ENEMY_SAVE_FILE,
                            enemy_board.board)
        enemy_board.info_text.append('The game has been saved')
        return True
    x, y = u_input.split(' ')
    x = int(x)
    y = int(y)
    if x < 0 or y < 0:
        raise IndexError
    return enemy_board.shoot(x, y)

def ai_shoot(board, not_hit):
    x, y = choice(not_hit)
    not_hit.remove((x, y))
    hit = board.shoot(x, y)
    hit_str = 'hit' if hit else 'missed'
    board.info_text.append(f'Enemy {hit_str} at {x} {y}')
    free_space = board.h - len(board.info_text) - 3
    if free_space < 0:
        del board.info_text[:-free_space]
    return hit

def pick_ship(ship_list, top_board, bottom_board):
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
            ship_index = int(input('Pick a ship to place\n> ')) - 1
            if ship_index < 0:
                raise IndexError
            ship_length = ship_list[ship_index]
        except (ValueError, IndexError):
            err_msg = 'You must pick one of the numbered ships'
        else:
            valid_index = True
    del ship_list[ship_index]
    return ship_length

def pick_direction(top_board, bottom_board):
    direction = None
    while direction not in ['H', 'V']:
        print_boards(top_board, bottom_board)
        if direction is not None:
            print('You must pick either V or H')
        direction = input('Enter V to place vertically, '
                          'or H to place horizontally\n> ').upper()
    return direction

def pick_cordinates(ship_list, player_board, enemy_board, err_msg = None):
    valid_cordinates = False
    cordinates = None
    while not valid_cordinates:
        print_boards(player_board, enemy_board)
        if err_msg:
            print(err_msg)
        try:
            u_input = input('Enter cordinates\n> ')
            x, y = u_input.split(' ')
            cordinates = (int(x), int(y))
        except ValueError:
            err_msg = 'Cordinates must be two integers '\
                    'with a space between'
            continue
        valid_cordinates = True
    return cordinates

def manual_placement(player_board, enemy_board):
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
                err_msg = 'You cannot place a ship here'

def place_from_file(path, board):
    board_state = []
    try:
        with open(path, 'r') as f:
            r = csv.reader(f)
            for row in r:
                board_state.append([int(x) for x in row])
    except FileNotFoundError:
        print(f'Could not find file {path}')
    except ValueError:
        print(f'Invalid file {path}')
    else:
        board.board = board_state
        return True
    return False

def place_phase(player_board, enemy_board):
    if yes_no_input('Do you want to load ship placement from file?'):
        if not place_from_file(input('file to read: '), player_board):
            return True
    else:
        manual_placement(player_board, enemy_board)
    place_from_file('ai_ships.csv', enemy_board)
    return False

def bomb_phase(player_board, enemy_board):
    player_turn = True 
    not_hit_pl = [(x,y) for x in range(10) for y in range(10)]
    not_hit_en = [(x,y) for x in range(10) for y in range(10)]
    err_msg = None
    enemy_board.info_text = ['X hit shot', 'O missed shot','',
                             'Write SAVE to save your game',
                             'Write QUIT to quit']
    while player_board.health() and enemy_board.health():
        print_boards(player_board, enemy_board)
        if err_msg:
            print(err_msg)
        if player_turn:
            try:
                #player_turn = ai_shoot(enemy_board, not_hit_en)
                player_turn = player_shoot(player_board, enemy_board)
            except ValueError:
                err_msg = 'You must give two integers'\
                        ' with a space in between'
            except IndexError:
                err_msg = 'Your cordinates must be on the board'
            else:
                del player_board.info_text[:]
                err_msg = None
        else:
            player_turn = not ai_shoot(player_board, not_hit_pl)
    print_boards(player_board, enemy_board)
    return player_board.health()

def print_winner_message(player_board, enemy_board):
    if player_board.health():
        win_or_lose = 'WON'
        winner = 'you'
        loser_board = enemy_board
    else:
        win_or_lose = 'LOST'
        winner = 'your enemy'
        loser_board = player_board
    print(f'YOU {win_or_lose}! It took {winner} '
          f'{loser_board.shots_fired()} tries.')

def save_stats(path, player_board, enemy_board):
    if player_board.health():
        winner = 'you'
        tries = enemy_board.shots_fired()
    else:
        winner = 'enemy'
        tries = player_board.shots_fired()
    with open(path, 'a') as f:
        f.write(f'{winner},{tries}\n')

def save_ship_placement(board):
    if not yes_no_input('Do you want to save your ship placements?'):
        return False
    path = input('file to write: ')
    if os.path.exists(path):
        if not yes_no_input(
                f'The file {path} already exists.\n'
                'Are you sure you want to overwrite it?', False):
            return True
    ships = [[v & Board.SHIP for v in row] for row in board.board]
    write_board_to_file(path, ships)
    return False

def write_board_to_file(path, board):
    with open(path, 'w') as f:
        for row in board:
            f.write(','.join(map(str, row)) + '\n')

def main():
    player_board = Board()
    enemy_board = Board(hide = True)
    if os.path.exists(f'{SAVE_DIR}/player_board.csv') \
            and os.path.exists(f'{SAVE_DIR}/enemy_board.csv') \
            and yes_no_input(
                    'A save file exists\n'
                    'Do you want to load and continue from this file?'):
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
