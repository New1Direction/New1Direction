"""Tests for the game rules. Run:  python3 -m unittest discover scripts"""
import unittest

from game import COLUMNS, ROWS, column_from_title, new_game, with_move


def play(moves: list[int]) -> dict:
    """Play columns in order, with a different player for every move."""
    game = new_game()
    for index, column in enumerate(moves):
        game, _ = with_move(game, f"player{index}", column)
    return game


class TitleTests(unittest.TestCase):
    def test_reads_columns_one_to_seven(self):
        self.assertEqual(column_from_title("drop 1"), 0)
        self.assertEqual(column_from_title("  Drop 7 "), 6)

    def test_rejects_everything_else(self):
        for title in ["drop 0", "drop 8", "drop", "drop x", "drop 3; rm -rf /", "drop -1", "light a window", "drop 3 4"]:
            self.assertIsNone(column_from_title(title), title)


class MoveTests(unittest.TestCase):
    def test_discs_stack_from_the_bottom_and_turns_alternate(self):
        game = play([3, 3])
        self.assertEqual(game["board"][ROWS - 1][3], "a")
        self.assertEqual(game["board"][ROWS - 2][3], "b")
        self.assertEqual(game["turn"], "a")
        self.assertEqual(game["moves"], 2)

    def test_nobody_moves_twice_in_a_row(self):
        game, _ = with_move(new_game(), "ares", 0)
        again, message = with_move(game, "ARES", 1)
        self.assertEqual(again, game)
        self.assertIn("Someone else", message)

    def test_a_full_column_is_refused(self):
        game = play([2] * ROWS)
        refused, message = with_move(game, "late", 2)
        self.assertEqual(refused, game)
        self.assertIn("full", message)

    def test_four_across_wins_and_scores(self):
        game = play([0, 0, 1, 1, 2, 2, 3])
        self.assertEqual(game["winner"], "a")
        self.assertEqual(game["line"], [[ROWS - 1, 0], [ROWS - 1, 1], [ROWS - 1, 2], [ROWS - 1, 3]])
        self.assertEqual(game["score"]["a"], 1)

    def test_four_up_wins(self):
        self.assertEqual(play([4, 5, 4, 5, 4, 5, 4])["winner"], "a")

    def test_diagonals_win(self):
        rising = play([0, 1, 1, 2, 2, 3, 2, 3, 3, 6, 3])
        self.assertEqual(rising["winner"], "a")
        falling = play([6, 5, 5, 4, 4, 3, 4, 3, 3, 0, 3])
        self.assertEqual(falling["winner"], "a")

    def test_the_next_move_after_a_win_starts_a_new_game_and_keeps_score(self):
        finished = play([0, 0, 1, 1, 2, 2, 3])
        fresh, _ = with_move(finished, "newcomer", 6)
        self.assertIsNone(fresh["winner"])
        self.assertEqual(fresh["moves"], 1)
        self.assertEqual(fresh["score"]["a"], 1)
        self.assertEqual(fresh["board"][ROWS - 1][6], "a")

    def test_a_full_board_with_no_line_is_a_draw(self):
        # Columns filled in an order that never makes four in a line.
        order = [0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 2, 3, 2, 3, 2, 3, 3, 2, 3, 2, 3, 2,
                 4, 5, 4, 5, 4, 5, 5, 4, 5, 4, 5, 4, 6, 6, 6, 6, 6, 6]
        game = play(order)
        self.assertEqual(game["moves"], COLUMNS * ROWS)
        self.assertEqual(game["winner"], "draw")
        self.assertEqual(game["score"]["draw"], 1)


if __name__ == "__main__":
    unittest.main()
