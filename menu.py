from board import Board, Ship
from random import randint, choice
from time import sleep
import os
import csv

def print_boards(top_board, bottom_board):
    os.system('clear')
    print(top_board)
    print(bottom_board)

def player_shoot(board):
    x, y = input('Where to shoot?\n> ').split(' ')
    x = int(x)
    y = int(y)
    if x < 0 or y < 0:
        raise IndexError
    return board.shoot(x, y)

def ai_shoot(board, not_hit):
    cordinates = choice(not_hit)
    not_hit.remove(cordinates)
    return board.shoot(*(cordinates))

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
    with open(path, 'r') as f:
        r = csv.reader(f)
        for row in r:
            board_state.append([int(x) for x in row])
    board.board = board_state

def place_phase(player_board, enemy_board):
    #manual_placement(player_board, enemy_board)
    place_from_file('ai_ships.csv', player_board)
    place_from_file('ai_ships.csv', enemy_board)

def bomb_phase(player_board, enemy_board):
    player_turn = True 
    not_hit_pl = [(x,y) for x in range(10) for y in range(10)]
    #not_hit_en = [(x,y) for x in range(10) for y in range(10)]
    err_msg = None
    while player_board.health() and enemy_board.health():
        print_boards(player_board, enemy_board)
        if err_msg:
            print(err_msg)
        if player_turn:
            try:
                #player_turn = ai_shoot(enemy_board, not_hit_en)
                player_turn = player_shoot(enemy_board)
            except ValueError:
                err_msg = 'You must give two integers'\
                        ' with a space in between'
            except IndexError:
                err_msg = 'Your cordinates must be on the board'
            else:
                err_msg = None
        else:
            player_turn = not ai_shoot(player_board, not_hit_pl)
    print_boards(player_board, enemy_board)
    return player_board.health()

def main():
    # ask for confirmation
    player_board = Board()
    enemy_board = Board(hide = True)

    place_phase(player_board, enemy_board)
    bomb_phase(player_board, enemy_board)
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


if __name__ == '__main__':
    main()
