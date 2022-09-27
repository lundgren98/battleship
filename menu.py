from board import Board, Ship
from random import randint, choice
from time import sleep

def print_boards(top_board, bottom_board):
    print(top_board)
    print(bottom_board)

def player_shoot(board):
    x, y = input('Where to shoot?\n> ').split(' ')
    x = int(x)
    y = int(y)
    return board.shoot(x, y)

def enemy_shoot(board, not_hit):
    cordinates = choice(not_hit)
    not_hit.remove(cordinates)
    return board.shoot(*(cordinates))

def main():
    # show ships DONE
    # choose ship to place DONE
    # redo if cannot place ship
    # ask for confirmation
    player_board = Board()
    enemy_board = Board(hide = True)
    print_boards(player_board, enemy_board)
## PLACE SHIPS
#    ships = [4, 3, 3, 2, 2, 2, 1, 1, 1, 1]
#    while ships:
#        try:
#            player_board.place_ship(Ship.create_ship(ships))
#        except Exception:
#            print('FEL')
#        print_boards(player_board, enemy_board)

# HARD CODING SHIPS
    player_board.place_ship(Ship((0,0), 'V', 4))
    player_board.place_ship(Ship((0,2), 'V', 3))
    player_board.place_ship(Ship((0,4), 'V', 3))
    player_board.place_ship(Ship((0,6), 'V', 2))
    player_board.place_ship(Ship((0,8), 'V', 2))
    player_board.place_ship(Ship((6,0), 'V', 2))
    player_board.place_ship(Ship((6,2), 'V', 1))
    player_board.place_ship(Ship((6,4), 'V', 1))
    player_board.place_ship(Ship((6,6), 'V', 1))
    player_board.place_ship(Ship((6,8), 'V', 1))

    enemy_board.place_ship(Ship((0,0), 'V', 4))
    enemy_board.place_ship(Ship((0,2), 'V', 3))
    enemy_board.place_ship(Ship((0,4), 'V', 3))
    enemy_board.place_ship(Ship((0,6), 'V', 2))
    enemy_board.place_ship(Ship((0,8), 'V', 2))
    enemy_board.place_ship(Ship((6,0), 'V', 2))
    enemy_board.place_ship(Ship((6,2), 'V', 1))
    enemy_board.place_ship(Ship((6,4), 'V', 1))
    enemy_board.place_ship(Ship((6,6), 'V', 1))
    enemy_board.place_ship(Ship((6,8), 'V', 1))

    player_turn = True 
    not_hit_en = [(x,y) for x in range(10) for y in range(10)]
    not_hit_pl = [(x,y) for x in range(10) for y in range(10)]
    while player_board.health() and enemy_board.health():
        sleep(0.2)
        print_boards(player_board, enemy_board)
        if player_turn:
            player_turn = enemy_shoot(enemy_board, not_hit_en)
        else:
            player_turn = not enemy_shoot(player_board, not_hit_pl)
    print_boards(player_board, enemy_board)
    if player_board.health():
        print('YOU WON!')
    else:
        print('YOU LOST!')


if __name__ == '__main__':
    main()
