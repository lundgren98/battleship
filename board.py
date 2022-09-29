class Ship:
    def __init__(self, position, direction, length):
        self.position = position
        self.direction = direction
        self.length = length

    def all_cordinates(self) -> list[tuple[int,int]]:
        r = []
        x, y = self.position
        for i in range(self.length):
            r.append((x, y))
            if self.direction == 'V':
                y += 1
            else:
                x += 1
        return r

    def water_space(self) -> list[tuple[int,int]]:
        cords = self.all_cordinates()
        ret = []
        for row in range(-1,2):
            for col in range(-1,2):
                ret.extend([(x+col,y+row) for x, y in cords])
        return list(set(ret))

class Board:
    # Constants for the state of each place
    WATER = 0
    HIT   = 1
    SHIP  = 2
    def __init__(self, h: int = 10, w: int = 10, hide: bool = False,
                 hp_str: str = 'HP', shots_str = 'Shots'):
        self.h = h
        self.w = w
        self.hide = hide
        # Fill the board with water
        self.board = [[Board.WATER] * w for _ in range(h)] 
        self._hp_str = hp_str 
        self._shots_str = shots_str 
        self.info_text = []

    def space_is_occupied(self, cordinates: list[tuple[int,int]]) -> bool:
        for x, y in cordinates:
            if self.board[y][x] & Board.SHIP:
                return True
        return False

    def get_cordinates_on_board(self,
                                cordinates: list[tuple[int,int]]
                                ) -> list[tuple[int,int]]:
        ret = []
        for x, y in cordinates:
            if x in range(self.w) and y in range(self.h):
                ret.append((x,y))
        return ret

    def is_cordinates_on_board(self, cordinates: list[tuple[int,int]]) -> bool:
        for x, y in cordinates:
            if x in range(self.w) and y in range(self.h):
                continue
            return False
        return True

    def place_ship(self, ship: Ship) -> bool:
        """Tries to place a ship on the board.
        Return bool indicating success."""
        cordinates = ship.all_cordinates()
        if not self.is_cordinates_on_board(cordinates):
            return False
        water_space = self.get_cordinates_on_board(ship.water_space())
        if self.space_is_occupied(water_space):
            return False
        for x, y in cordinates:
            self.board[y][x] = Board.SHIP
        return True

    def shoot(self, x: int, y: int) -> bool:
        """Changes state at row y and column x to indicate it being hit.
        Returns a bool indicating if a ship was hit."""
        self.board[y][x] |= Board.HIT
        return bool(self.board[y][x] & Board.SHIP)
    
    def health(self) -> int:
        hp = 0
        for row in self.board:
            for col in row:
                # we only want surviving ships
                hp += col == Board.SHIP
        return hp

    def shots_fired(self) -> int:
        shots = 0
        for row in self.board:
            for col in row:
                shots += col & Board.HIT
        return shots

    def __str__(self):
        display_state = ".O#X"
        # text to show to the right of the board
        text = [f'{self._hp_str}: {self.health()}',
                f'{self._shots_str}: {self.shots_fired()}',
                '']
        text.extend(self.info_text)

        # TODO: this is dependant on self.w being 10
        s = f'+-0123456789-+\n'

        for row in range(self.h):
            s += f'{row} '
            for col in range(self.w):
                position_state = self.board[row][col]
                # Hide ships that aren't hit if self.hide
                if self.hide and not (position_state & Board.HIT):
                    position_state &= ~Board.SHIP
                s += display_state[position_state]
            text_row = text[row] if len(text) > row else ''
            s += f' | {text_row}\n'
        s += '+-' + self.w * '-' + '-+'
        return s

# TEST CASES
if __name__ == '__main__':
    b = Board(10, 10)
    s1 = Ship((1, 4), 'V', 4)
    s2 = Ship((8, 1), 'H', 4)
    for s in (s1, s2):
        b.place_ship(s)
    print(b)

