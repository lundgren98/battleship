import sqlite3

class Data:
    def __init__(self, path: str):
        self.path = path
        self._player_table = 'players' 
        self._create_player_table()
        self._game_table = 'games' 
        self._create_game_table()

    def _execute(self, s: str, t: tuple | None = None):
        with sqlite3.connect(self.path) as conn:
            r = conn.execute(s, t) if t is not None \
                    else conn.execute(s)
        return r

    def _create_player_table(self):
        s = f'''
            CREATE TABLE IF NOT EXISTS {self._player_table}(
                name TEXT UNIQUE NOT NULL,
                pw TEXT
            )
            '''
        self._execute(s)

    def _create_game_table(self):
        s = f'''
            CREATE TABLE IF NOT EXISTS {self._game_table}(
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                date_time DATETIME,
                first_move TEXT,
                winner TEXT,
                loser TEXT,
                winner_shots INTEGER,
                loser_shots INTEGER,
                winner_surviving_ships INTEGER,
                FOREIGN KEY(winner) REFERENCES {self._player_table}(name),
                FOREIGN KEY(loser) REFERENCES {self._player_table}(name)
            )
            '''
        self._execute(s)

    def add_player(self, name: str, pw: str):
        s = f'''
            INSERT INTO {self._player_table}(name, pw)
            VALUES (?, ?)
            '''
        self._execute(s, (name, pw))

    def add_game(self, date_time: str, first_move: str,
                 winner: str, loser: str,
                 winner_shots: int, loser_shots: int,
                 winner_surviving_ships: int):
        s = f'''
            INSERT INTO {self._game_table}(
                date_time,
                first_move,
                winner,
                loser,
                winner_shots,
                loser_shots,
                winner_surviving_ships
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            '''
        values = (date_time,
                  first_move,
                  winner, loser,
                  winner_shots, loser_shots,
                  winner_surviving_ships)
        self._execute(s, values)

    def list_games(self, player = None):
        s = f'''
            SELECT * FROM {self._game_table}
            '''
        if player is not None:
            s += f'WHERE winner = "{player}" OR loser = "{player}"'
        return self._execute(s)

    def count_games(self, player = None, only_won_games = False):
        s = f'''
            SELECT COUNT(*) FROM {self._game_table}
            '''
        if player is not None:
            s += f'WHERE winner = "{player}" '
        if not only_won_games:
            s += f'OR loser = "{player}"'
        return self._execute(s)

    def max_game_id(self):
        s = f'''
            SELECT max(id) FROM {self._game_table}
            '''
        return self._execute(s)

    def avg_winner_shots(self, player = None):
        s = f'''
            SELECT AVG(winner_shots) FROM {self._game_table}
            '''
        if player is not None:
            s+= f'WHERE winner = "{player}"'
        return self._execute(s)

    def check_login(self, player, pw = None):
        s = f'''
            SELECT COUNT(*) FROM {self._player_table} WHERE name = "{player}"
            '''
        if pw is not None:
            s+= f'AND pw = "{pw}"'
        return self._execute(s)

