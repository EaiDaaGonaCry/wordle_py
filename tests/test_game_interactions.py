"""
Unit tests for game interactions, visual elements, and loop logic.
"""
import sys
import os
import unittest
from unittest.mock import MagicMock, patch

os.environ["SDL_VIDEODRIVER"] = "dummy"

import pygame

# Local imports
from modes import AiMode, PlayerMode, PveMode
from settings import DifficultyMenu, SettingsMenu, WordEditor, Leaderboard
from settings.Constants import COLOR_CORRECT, WIDTH, HEIGHT


class TestVisualsAndLoops(unittest.TestCase):
    """Tests for visual rendering functions and main game loops."""

    def setUp(self):
        """Initialize Pygame and mock screens for testing."""
        pygame.init()
        pygame.font.init()
        self.mock_screen = MagicMock()
        self.real_screen = pygame.Surface((WIDTH, HEIGHT))
        self.mock_font = MagicMock()
        self.mock_font.render.return_value = pygame.Surface((10, 10))

    def tearDown(self):
        """Clean up pygame events."""
        pygame.event.clear()

    # =========================================================================
    # PART 1: VISUAL TESTS (Panels & Buttons)
    # =========================================================================

    @patch('pygame.draw.rect')
    def test_aimode_draw_tile_colors(self, mock_draw_rect):
        """Test that AiMode.draw_tile picks the correct color."""
        AiMode.draw_tile(self.mock_screen, 0, 0, 50, "A", "g", self.mock_font)
        args, _ = mock_draw_rect.call_args_list[0]
        self.assertEqual(args[1], COLOR_CORRECT)

    def test_aimode_draw_history_panel(self):
        """Test drawing the history panel without errors."""
        rect = pygame.Rect(0, 0, 100, 100)
        fonts = {"med": self.mock_font, "small": self.mock_font}
        history = [("TEST", "gggg")]
        AiMode.draw_history_panel(self.real_screen, rect, history, fonts)

    def test_aimode_draw_input_panel(self):
        """Test drawing the input panel."""
        rect = pygame.Rect(0, 0, 100, 100)
        fonts = {"large": self.mock_font, "small": self.mock_font, "med": self.mock_font}
        AiMode.draw_input_panel(self.real_screen, rect, "APPLE", "xxxxx", "Msg", 5, fonts)

    def test_aimode_draw_stats_panel(self):
        """Test drawing the statistics panel."""
        rect = pygame.Rect(0, 0, 100, 100)
        fonts = {"med": self.mock_font}
        AiMode.draw_stats_panel(self.real_screen, rect, 10, 1, fonts)

    @patch('modes.PlayerMode.draw_grid')
    def test_playermode_hud(self, _):
        """Test HUD elements rendering."""
        PlayerMode.draw_hud(self.mock_screen, score=100, name="Test", current_round=1)
        self.assertGreaterEqual(self.mock_screen.blit.call_count, 3)

    @patch('pygame.mouse.get_pos')
    @patch('pygame.draw.rect')
    def test_button_draw_states(self, mock_draw_rect, mock_mouse_pos):
        """Test button hover and draw states."""
        from settings.Logic import Button
        btn = Button(10, 10, 100, 50, "Test", (100, 100, 100))
        mock_mouse_pos.return_value = (0, 0)
        btn.draw(self.mock_screen)
        self.assertEqual(mock_draw_rect.call_args[0][1], (100, 100, 100))

    # =========================================================================
    # PART 2: PLAYER MODE VISUALS (Alphabet, Grid, End Message)
    # =========================================================================

    @patch('pygame.draw.rect')
    @patch('pygame.font.SysFont')
    def test_playermode_draw_alphabet(self, mock_sysfont, mock_draw_rect):
        """Test drawing the alphabet keys."""
        mock_font_inst = MagicMock()
        mock_font_inst.render.return_value = pygame.Surface((10, 10))
        mock_sysfont.return_value = mock_font_inst
        from settings.Constants import COLOR_ABSENT
        colors = {'A': COLOR_CORRECT, 'B': COLOR_ABSENT}
        PlayerMode.draw_alphabet(self.real_screen, colors)
        self.assertGreater(mock_draw_rect.call_count, 20)

    @patch('pygame.draw.rect')
    @patch('pygame.font.SysFont')
    def test_playermode_draw_grid(self, mock_sysfont, mock_draw_rect):
        """Test drawing the main game grid."""
        mock_font_inst = MagicMock()
        mock_font_inst.render.return_value = pygame.Surface((10, 10))
        mock_sysfont.return_value = mock_font_inst
        guesses = [[('A', 0, 'g'), ('P', 1, 'y'), ('P', 2, 'x'), ('L', 3, 'x'), ('E', 4, 'g')]]
        PlayerMode.draw_grid(self.real_screen, guesses, "PEA", 0, 5, 6)
        self.assertGreater(mock_draw_rect.call_count, 50)

    @patch('pygame.draw.rect')
    @patch('pygame.font.SysFont')
    def test_playermode_draw_end_message(self, mock_sysfont, mock_draw_rect):
        """Test drawing the win/loss message."""
        mock_font_inst = MagicMock()
        mock_font_inst.render.return_value = pygame.Surface((10, 10))
        mock_sysfont.return_value = mock_font_inst
        PlayerMode.draw_end_message(self.real_screen, won=True, secret_word="TESTS", round_score=100)
        PlayerMode.draw_end_message(self.real_screen, won=False, secret_word="TESTS", round_score=0)
        self.assertEqual(mock_draw_rect.call_count, 4)

    # =========================================================================
    # PART 3: GAME LOOP TESTS (Interaction Scripts)
    # =========================================================================

    def make_key_event(self, key_code, unicode_char):
        """Helper to create a mock key event."""
        event = MagicMock()
        event.type = pygame.KEYDOWN
        event.key = key_code
        event.unicode = unicode_char
        return event

    def make_quit_event(self):
        """Helper to create a mock quit event."""
        event = MagicMock()
        event.type = pygame.QUIT
        return event

    @patch('pygame.display.get_surface')
    @patch('settings.JsonStats.save_score')
    @patch('modes.PlayerMode.load_valid_words')
    @patch('pygame.event.get')
    @patch('pygame.display.flip')
    @patch('pygame.quit')
    def test_run_game_winning_scenario(self, _quit, _flip, mock_events, mock_load_words, mock_save,
                                       mock_get_surface):
        """Test a complete winning game loop."""
        mock_get_surface.return_value = self.real_screen
        mock_load_words.return_value = ["APPLE"]
        script = [
            [self.make_key_event(pygame.K_a, 'A')],
            [self.make_key_event(pygame.K_p, 'P')],
            [self.make_key_event(pygame.K_p, 'P')],
            [self.make_key_event(pygame.K_l, 'L')],
            [self.make_key_event(pygame.K_e, 'E')],
            [self.make_key_event(pygame.K_RETURN, '')],
            [MagicMock(type=pygame.MOUSEBUTTONDOWN, pos=(WIDTH // 2 - 100, 500))],
            [self.make_quit_event()]
        ]
        mock_events.side_effect = script
        with patch('settings.Logic.Button.is_clicked') as mock_click:
            mock_click.side_effect = [False, True]
            result = PlayerMode.run_game({"difficulty": "NORMAL"})
        self.assertEqual(result, "HOME")
        mock_save.assert_called_with("Player", 750)

    @patch('pygame.display.get_surface')
    @patch('settings.Logic.load_valid_words')
    @patch('pygame.event.get')
    @patch('pygame.display.flip')
    @patch('pygame.quit')
    def test_run_ai_mode_flow(self, _quit, _flip, mock_events, mock_load_words, mock_get_surface):
        """Test the flow of the AI Solver mode."""
        mock_get_surface.return_value = self.real_screen
        mock_load_words.return_value = ["APPLE"]
        script = [
            [self.make_key_event(pygame.K_g, 'g')],
            [self.make_key_event(pygame.K_g, 'g')],
            [self.make_key_event(pygame.K_g, 'g')],
            [self.make_key_event(pygame.K_g, 'g')],
            [self.make_key_event(pygame.K_g, 'g')],
            [self.make_key_event(pygame.K_RETURN, '')],
            [MagicMock(type=pygame.MOUSEBUTTONDOWN, pos=(0, 0))],
            [self.make_quit_event()]
        ]
        mock_events.side_effect = script
        with patch('settings.Logic.Button.is_clicked') as mock_click:
            mock_click.side_effect = [False, True]
            result = AiMode.run_ai_mode("NORMAL")
        self.assertEqual(result, "HOME")

    @patch('settings.SettingsMenu.game_settings', new_callable=dict)
    @patch('settings.WordEditor.run_editor')
    @patch('pygame.event.get')
    @patch('pygame.display.get_surface')
    @patch('pygame.display.flip')
    def test_settings_menu_interactions(self, _flip, mock_get_surface, mock_events,
                                        mock_run_editor, mock_settings):
        """Test interaction with settings menu buttons."""
        mock_settings.update({"player_name": "Test", "word_length": 5, "max_attempts": 6})
        mock_get_surface.return_value = self.real_screen
        click = MagicMock(type=pygame.MOUSEBUTTONDOWN, pos=(0, 0))
        mock_events.side_effect = [[click], [click], [click], [click]]

        # Flattened logic for button clicks
        f1 = [False, False, False, True, False, False, False]
        f2 = [False, False, False, False, False, True, False]
        f3 = [False, True, False, False, False, False, False]
        f4 = [True, False, False, False, False, False, False]

        with patch('settings.Logic.Button.is_clicked') as mock_btn:
            mock_btn.side_effect = f1 + f2 + f3 + f4
            SettingsMenu.settings_menu()

        self.assertEqual(mock_settings["word_length"], 6)
        self.assertEqual(mock_settings["max_attempts"], 7)
        mock_run_editor.assert_called_once()

    @patch('pygame.event.get')
    @patch('pygame.display.get_surface')
    @patch('pygame.display.flip')
    def test_difficulty_menu_selection(self, _flip, mock_get_surface, mock_events):
        """Test selecting a difficulty."""
        mock_get_surface.return_value = self.real_screen
        click = MagicMock(type=pygame.MOUSEBUTTONDOWN, pos=(0, 0))
        mock_events.side_effect = [[click], [self.make_quit_event()]]
        with patch('settings.Logic.Button.is_clicked') as mock_btn:
            mock_btn.side_effect = [True, False, False]
            self.assertEqual(DifficultyMenu.get_difficulty(), "NORMAL")

    # =========================================================================
    # PART 4: WORD EDITOR & LEADERBOARD VISUALS
    # =========================================================================

    def test_create_editor_buttons(self):
        """Test that editor buttons are created correctly."""
        buttons = WordEditor.create_editor_buttons(self.mock_font)
        self.assertIn("save", buttons)
        self.assertIn("cancel", buttons)
        self.assertIn("add", buttons)
        self.assertIn("delete", buttons)
        self.assertEqual(buttons["add"].text, "+ ADD NEW WORD")

    @patch('pygame.draw.rect')
    def test_draw_word_list_scrolling(self, mock_draw_rect):
        """Test scrolling logic in word editor drawing."""
        words = ["APPLE", "BANANA", "CHERRY", "DATE", "ELDERBERRY"]
        config = {
            "panel_y": 100, "panel_h": 400,
            "row_height": 50, "scroll_offset": 0,
            "visible_rows": 5
        }
        fonts = (self.mock_font, self.mock_font)
        WordEditor.draw_word_list(self.mock_screen, words, config, fonts, selected_index=1)
        self.assertGreater(mock_draw_rect.call_count, 10)

        mock_draw_rect.reset_mock()
        config["scroll_offset"] = 100
        WordEditor.draw_word_list(self.mock_screen, words, config, fonts, selected_index=-1)
        self.assertGreater(mock_draw_rect.call_count, 5)

    @patch('settings.JsonStats.load_leaderboard')
    @patch('pygame.event.get')
    @patch('pygame.display.get_surface')
    @patch('pygame.display.flip')
    def test_show_leaderboard_data(self, _flip, mock_get_surface, mock_events, mock_load_data):
        """Test displaying leaderboard data."""
        mock_get_surface.return_value = self.real_screen
        mock_load_data.return_value = [{'name': 'Winner', 'score': 1000}]
        click_back = MagicMock(type=pygame.MOUSEBUTTONDOWN, pos=(0, 0))
        mock_events.side_effect = [[click_back]]
        with patch('settings.Logic.Button.is_clicked') as mock_btn_click:
            mock_btn_click.return_value = True
            Leaderboard.show_leaderboard()
        mock_load_data.assert_called_once()

    @patch('pygame.draw.rect')
    @patch('pygame.font.SysFont')
    def test_pve_draw_mini_grid(self, mock_sysfont, mock_draw_rect):
        """Test drawing the mini grid for PvE mode."""
        mock_font_inst = MagicMock()
        mock_font_inst.render.return_value = pygame.Surface((10, 10))
        mock_sysfont.return_value = mock_font_inst
        guesses = [[('A', 0, 'g'), ('P', 1, 'y'), ('P', 2, 'x'), ('L', 3, 'x'), ('E', 4, 'g')]]
        PveMode.draw_mini_grid(
            self.real_screen, start_x=0, start_y=0, width=200,
            guesses=guesses, current_guess="TE",
            word_length=5, max_attempts=6, label="PLAYER"
        )
        self.assertGreater(mock_draw_rect.call_count, 50)


if __name__ == '__main__':
    unittest.main()