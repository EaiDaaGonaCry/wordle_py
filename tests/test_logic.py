"""
Unit tests for game logic, data handling, and algorithmic functions.
"""
import unittest
from unittest.mock import patch, mock_open, MagicMock, call

from settings import JsonStats, WordEditor, Logic
from modes import PlayerMode, PveMode
from settings.Logic import (
    colour_set, filter_words, get_best_word, lie_detector,
    levenshtein_distance, triplets_maker, get_pattern_string,
    colour_value_helper, get_best_lie, load_valid_words,
    init_extreme_candidates, remove_useless_words, Button
)


class TestFileOperationsAndData(unittest.TestCase):
    """Tests for file I/O operations (Leaderboard, Word Editor, API Keys)."""

    # --- 1. JSON STATS (Leaderboard) ---

    def test_load_leaderboard_file_not_found(self):
        """Test behavior when leaderboard file is missing."""
        with patch("os.path.exists", return_value=False):
            data = JsonStats.load_leaderboard()
            self.assertEqual(data, [])

    def test_load_leaderboard_corrupted(self):
        """Test behavior when leaderboard JSON is corrupted."""
        with patch("os.path.exists", return_value=True):
            with patch("builtins.open", mock_open(read_data="{broken_json")):
                data = JsonStats.load_leaderboard()
                self.assertEqual(data, [])

    @patch("settings.JsonStats.load_leaderboard")
    @patch("builtins.open", new_callable=mock_open)
    @patch("os.makedirs")
    @patch("json.dump")
    def test_save_score_top_10_logic(self, mock_dump, _mock_dirs, _mock_file, mock_load):
        """Ensure only top 10 scores are saved."""
        existing_data = [{"name": f"P{i}", "score": i * 10} for i in range(10)]
        mock_load.return_value = existing_data
        JsonStats.save_score("Champion", 999)
        saved_list = mock_dump.call_args[0][0]
        self.assertEqual(len(saved_list), 10)
        self.assertEqual(saved_list[0]['score'], 999)
        self.assertEqual(saved_list[-1]['score'], 10)

    # --- 2. WORD EDITOR (File I/O) ---

    def test_editor_load_words(self):
        """Test loading words from a text file."""
        fake_content = "  apple \n BANANA \n\n"
        with patch("builtins.open", mock_open(read_data=fake_content)):
            words = WordEditor.load_words_from_file("dummy.txt")
            self.assertEqual(words, ["APPLE", "BANANA"])

    def test_editor_save_words(self):
        """Test saving words to a text file."""
        words_to_save = ["APPLE", "", "  ", "ZEBRA"]
        m_open = mock_open()
        with patch("builtins.open", m_open):
            WordEditor.save_words_to_file("dummy.txt", words_to_save)
            handle = m_open()
            self.assertIn(call("APPLE\n"), handle.write.call_args_list)
            self.assertIn(call("ZEBRA\n"), handle.write.call_args_list)
            self.assertNotIn(call("\n"), handle.write.call_args_list)

    # --- 3. PVE MODE (API Key) ---

    def test_get_api_key_exists(self):
        """Test reading the API key from a file."""
        with patch("os.path.exists", return_value=True):
            with patch("builtins.open", mock_open(read_data="MY_SECRET_KEY")):
                key = PveMode.get_api_key()
                self.assertEqual(key, "MY_SECRET_KEY")

    def test_get_api_key_missing(self):
        """Test behavior when API key file is missing."""
        with patch("os.path.exists", return_value=False):
            key = PveMode.get_api_key()
            self.assertIsNone(key)

    # --- 4. LOGIC EDGE CASES (Complex Filtering) ---

    def test_filter_words_yellow_conflict(self):
        """Test logic filtering with yellow letter conflicts."""
        words = ["APPLE", "STARK"]
        filtered = Logic.filter_words("yxxxx", "APPLE", words)
        self.assertNotIn("APPLE", filtered)
        self.assertIn("STARK", filtered)

    def test_filter_words_grey_duplicate(self):
        """Test logic filtering with grey letter duplicates."""
        words = ["EERIE", "SPEED"]
        filtered = Logic.filter_words("xxyyx", "SPEED", words)
        self.assertNotIn("SPEED", filtered)
        self.assertIn("EERIE", filtered)


class TestWordleLogic(unittest.TestCase):
    """Tests for the core Wordle game logic (coloring, patterns, etc.)."""

    def test_colour_set_exact_match(self):
        """Test generation of Green patterns."""
        res = colour_set("APPLE", "APPLE", 5)
        pattern = get_pattern_string(res)
        self.assertEqual(pattern, "ggggg")

    def test_colour_set_no_match(self):
        """Test generation of all Grey patterns."""
        res = colour_set("ABCDE", "FGHIK", 5)
        pattern = get_pattern_string(res)
        self.assertEqual(pattern, "xxxxx")

    def test_colour_set_mixed(self):
        """Test generation of mixed patterns."""
        res = colour_set("SPEED", "EERIE", 5)
        triplets = sorted(res, key=lambda x: x[1])
        self.assertEqual(triplets[2][2], 'y')

    def test_colour_set_duplicates(self):
        """Test handling of duplicate letters in coloring."""
        res = colour_set("AABBB", "ABBAA", 5)
        pattern = get_pattern_string(res)
        self.assertEqual(pattern, "gygyx")

    def test_filter_words(self):
        """Test word filtering based on patterns."""
        words = ["APPLE", "ACORN", "BEAST"]
        filtered = filter_words("ggggg", "APPLE", words)
        self.assertEqual(filtered, ["APPLE"])
        filtered = filter_words("gxxxx", "APPLE", words)
        self.assertIn("ACORN", filtered)

    def test_remove_useless_words(self):
        """Test optimization of word lists."""
        words = ["APPLE", "ZEBRA"]
        res = remove_useless_words("APPLE", "ZEBRA", words)
        self.assertIn("ZEBRA", res)

    def test_triplets_maker(self):
        """Test helper for creating logic triplets."""
        t = triplets_maker("gx", "HI")
        self.assertEqual(t[0], ('H', 0, 'g'))

    def test_levenshtein(self):
        """Test Levenshtein distance calculation."""
        self.assertEqual(levenshtein_distance("kitten", "sitting"), 3)

    def test_colour_value_helper(self):
        """Test heuristic value calculation for colors."""
        triplets = [('A', 0, 'g'), ('B', 1, 'y'), ('C', 2, 'x')]
        self.assertEqual(colour_value_helper(triplets), 4)

    def test_get_best_word(self):
        """Test selection of the best next guess."""
        candidates = ["ABCDE", "FGHIJ"]
        best = get_best_word(candidates)
        self.assertIn(best, candidates)

    def test_get_best_lie(self):
        """Test generating a lie for Ai Mode."""
        pool = ["APPLE", "ABUSE"]
        lie = get_best_lie("APPLE", pool, 5)
        self.assertTrue(isinstance(lie, list))

    def test_lie_detector(self):
        """Test logic to detect inconsistencies."""
        pool = {"APPLE": 0}
        new_pool = lie_detector("xxxxx", "APPLE", pool)
        self.assertEqual(new_pool["APPLE"], 1)

    def test_init_extreme(self):
        """Test initialization of extreme mode candidates."""
        res = init_extreme_candidates(["A", "B"])
        self.assertEqual(res, {"A": 0, "B": 0})

    def test_load_valid_words_success(self):
        """Test loading valid words."""
        mock_data = "APPLE\nZEBRA\nERROR\n"
        with patch("builtins.open", mock_open(read_data=mock_data)):
            words = load_valid_words("dummy.txt", 5)
            self.assertIn("APPLE", words)

    def test_load_valid_words_missing(self):
        """Test fallback when word file is missing."""
        with patch("builtins.open", side_effect=FileNotFoundError):
            words = load_valid_words("missing.txt")
            self.assertEqual(words, ["ERROR"])

    def test_button_logic(self):
        """Test button click detection."""
        with patch('pygame.font.SysFont'):
            btn = Button(10, 10, 100, 50, "TEST", (255, 255, 255))
            self.assertTrue(btn.is_clicked((50, 30)))
            self.assertFalse(btn.is_clicked((200, 200)))


class TestGameRulesAndBots(unittest.TestCase):
    """Tests for scoring and bot behaviors."""

    def test_calculate_score(self):
        """Test score calculation."""
        score = PlayerMode.calculate_score(word_length=5, max_attempts=6,
                                           attempts_taken=4, difficulty="Normal")
        self.assertEqual(score, 450)

    def test_edit_distance_bot(self):
        """Test the simple edit distance bot."""
        all_words = ["HELLO", "WORLD", "TESTS"]
        guess = PveMode.get_edit_distance_guess(["HELLO", "WORLD"], "HELIP", all_words)
        self.assertEqual(guess, "HELLO")
        guess_rand = PveMode.get_edit_distance_guess([], "ABC", all_words)
        self.assertIn(guess_rand, all_words)

    @patch('modes.PveMode.CLIENT')
    def test_gemini_bot(self, mock_client):
        """Test successful Gemini API call."""
        mock_response = MagicMock()
        mock_response.text = "APPLE"
        mock_client.models.generate_content.return_value = mock_response
        history = [[('T', 0, 'g'), ('R', 1, 'x'), ('A', 2, 'y'), ('I', 3, 'x'), ('N', 4, 'x')]]
        guess = PveMode.get_gemini_guess(history, 5)
        self.assertEqual(guess, "APPLE")
        mock_client.models.generate_content.assert_called_once()

    @patch('modes.PveMode.CLIENT')
    def test_gemini_bot_exception(self, mock_client):
        """Test that the game doesn't crash if Google API fails."""
        mock_client.models.generate_content.side_effect = Exception("API Down")
        result = PveMode.get_gemini_guess([], 5)
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()