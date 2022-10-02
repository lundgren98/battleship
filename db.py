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

    def add_game(self, first_move: str,
                 winner: str, loser: str,
                 winner_shots: int, loser_shots: int,
                 winner_surviving_ships: int):
        s = f'''
            INSERT INTO {self._game_table}(
                first_move,
                winner,
                loser,
                winner_shots,
                loser_shots,
                winner_surviving_ships
            )
            VALUES (?, ?, ?, ?, ?, ?)
            '''
        values = (first_move,
                  winner, loser,
                  winner_shots, loser_shots,
                  winner_surviving_ships)
        self._execute(s, values)

    def count_games(self):
        s = f'''
            SELECT COUNT(*) FROM {self._game_table}
            '''
        return self._execute(s)

if __name__ == '__main__':
    data = Data('stats.db')
    count = tuple(data.count_games())[0][0]
    print(count)

