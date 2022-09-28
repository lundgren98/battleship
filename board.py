class Ship:
    def __init__(self, position, direction, length):
        self.position = position
        self.direction = direction
        self.length = length

    def all_cordinates(self):
        r = []
        x, y = self.position
        for i in range(self.length):
            r.append((x, y))
            if self.direction == 'H':
                y += 1
            else:
                x += 1
        return r

    def water_space(self):
        cords = self.all_cordinates()
        ret = []
        for row in range(-1,2):
            for col in range(-1,2):
                ret.extend([(x+col,y+row) for x, y in cords])
        return list(set(ret))

class Board:
    WATER = 0
    HIT   = 1
    SHIP  = 2
    def __init__(self, h = 10, w = 10, hide = False):
        self.h = h
        self.w = w
        self.hide = hide
        self.board = [[Board.WATER] * w for _ in range(h)] 

    def space_is_occupied(self, cordinates):
        for x, y in cordinates:
            if self.board[y][x] & Board.SHIP:
                return True
        return False

    def get_cordinates_on_board(self, cordinates):
        ret = []
        for x, y in cordinates:
            if x in range(self.w) and y in range(self.h):
                ret.append((x,y))
        return ret

    def is_cordinates_on_board(self, cordinates):
        for x, y in cordinates:
            if x in range(self.w) and y in range(self.h):
                continue
            return False
        return True

    def place_ship(self, ship):
        cordinates = ship.all_cordinates()
        if not self.is_cordinates_on_board(cordinates):
            return False
        water_space = self.get_cordinates_on_board(ship.water_space())
        if self.space_is_occupied(water_space):
            return False
        for x, y in cordinates:
            self.board[y][x] = Board.SHIP
        return True

    def shoot(self, x, y):
        self.board[y][x] |= Board.HIT
        return bool(self.board[y][x] & Board.SHIP)
    
    def health(self):
        hp = 0
        for row in self.board:
            for col in row:
                hp += col == Board.SHIP
        return hp

    def shots_fired(self):
        shots = 0
        for row in self.board:
            for col in row:
                shots += col & Board.HIT
        return shots

    def __str__(self):
        display_state = ".O#X"
        s = f'+-0123456789-+ HP: {self.health()}\n'
        for row in range(self.h):
            s += f'{row} '
            for col in range(self.w):
                position_state = self.board[row][col]
                if self.hide and not (position_state & Board.HIT):
                    position_state &= ~Board.SHIP
                s += display_state[position_state]
            s += ' |'
            if row == 0:
                s += f' Shots: {self.shots_fired()}'
            s += '\n'
        s += '+-' + self.w * '-' + '-+'
        return s


if __name__ == '__main__':
    b = Board(10, 10)
    s1 = Ship((1, 4), 'V', 4)
    s2 = Ship((8, 1), 'H', 4)
    for s in (s1, s2):
        b.place_ship(s)
    print(b)

