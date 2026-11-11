"""Rules for the four-in-a-row game visitors play on the profile.

Two teams, "a" and "b", take turns dropping a disc into one of seven columns.
Four in a line wins. Anyone can move for the team whose turn it is, but
nobody may move twice in a row, so one person can't play both sides.

Everything here is a pure function of the game state, which is plain JSON.
"""
from __future__ import annotations

COLUMNS, ROWS, NEEDED = 7, 6, 4
EMPTY = "."
TEAMS = ("a", "b")
MOVE_PREFIX = "drop "


def new_game(score: dict | None = None) -> dict:
    return {
        "board": [EMPTY * COLUMNS for _ in range(ROWS)],  # row 0 is the top
        "turn": "a",
        "last": None,
        "winner": None,       # "a", "b", "draw" or None while playing
        "line": [],           # the winning cells, as [row, column] pairs
        "moves": 0,
        "score": dict(score or {"a": 0, "b": 0, "draw": 0}),
    }


def column_from_title(title: str) -> int | None:
    """0-based column for an issue title like "drop 3", else None."""
    text = title.strip().lower()
    if not text.startswith(MOVE_PREFIX):
        return None
    number = text[len(MOVE_PREFIX):].strip()
    if not number.isdigit() or not 1 <= int(number) <= COLUMNS:
        return None
    return int(number) - 1


def landing_row(board: list[str], column: int) -> int | None:
    """The lowest empty row in `column`, or None if the column is full."""
    for row in range(ROWS - 1, -1, -1):
        if board[row][column] == EMPTY:
            return row
    return None


def winning_line(board: list[str], row: int, column: int) -> list[list[int]]:
    """The cells of a four-in-a-line through (row, column), or []."""
    team = board[row][column]
    for d_row, d_col in ((0, 1), (1, 0), (1, 1), (1, -1)):
        cells = [[row, column]]
        for direction in (1, -1):
            r, c = row + d_row * direction, column + d_col * direction
            while 0 <= r < ROWS and 0 <= c < COLUMNS and board[r][c] == team:
                cells.append([r, c])
                r, c = r + d_row * direction, c + d_col * direction
        if len(cells) >= NEEDED:
            return sorted(cells)
    return []


def with_move(game: dict, login: str, column: int) -> tuple[dict, str]:
    """Play `column` for `login`. Returns the new state and a short message.

    A move on a finished game starts the next one. An illegal move returns
    the state unchanged with the reason.
    """
    if game.get("winner"):
        game = new_game(game.get("score"))
    last = game.get("last") or {}
    if last.get("login", "").lower() == login.lower():
        return game, "You made the last move. Someone else has to go next."
    row = landing_row(game["board"], column)
    if row is None:
        return game, "That column is full. Pick another."

    team = game["turn"]
    board = list(game["board"])
    board[row] = board[row][:column] + team + board[row][column + 1:]
    line = winning_line(board, row, column)
    moves = game["moves"] + 1
    winner = team if line else "draw" if moves == COLUMNS * ROWS else None
    score = dict(game["score"])
    if winner:
        score[winner] = score.get(winner, 0) + 1
    updated = {
        "board": board,
        "turn": TEAMS[1 - TEAMS.index(team)],
        "last": {"login": login, "row": row, "column": column, "team": team},
        "winner": winner,
        "line": line,
        "moves": moves,
        "score": score,
    }
    message = "That wins the game!" if line else "It's a draw." if winner else "Disc dropped."
    return updated, message
