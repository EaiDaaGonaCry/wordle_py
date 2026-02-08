"""
Unit tests for main menu navigation and app entry points.
"""
import unittest
import os
from unittest.mock import MagicMock, patch

os.environ["SDL_VIDEODRIVER"] = "dummy"
import pygame

import wordle
from settings.Constants import WIDTH, HEIGHT

class TestAppNavigation(unittest.TestCase):
    """Tests for high-level application navigation."""

    def setUp(self):
        """Initialize dummy screen for wordle module."""
        pygame.init()
        pygame.font.init()
        self.real_screen = pygame.Surface((WIDTH, HEIGHT))
        wordle.SCREEN = self.real_screen

    def make_click_event(self):
        """Create a mock left-click event."""
        event = MagicMock()
        event.type = pygame.MOUSEBUTTONDOWN
        event.button = 1
        event.pos = (0, 0)
        return event

    def make_quit_event(self):
        """Create a mock quit event."""
        event = MagicMock()
        event.type = pygame.QUIT
        return event

    # --- LOADING SCREEN ---
    @patch('pygame.display.flip')
    @patch('pygame.event.get')
    @patch('pygame.time.get_ticks')
    def test_loading_screen(self, mock_ticks, mock_events, mock_flip):
        """Test that the loading screen loop terminates correctly."""
        mock_ticks.side_effect = [0, 2000]
        mock_events.return_value = []

        wordle.show_loading_screen(1500)
        self.assertTrue(mock_flip.called)

    # --- MAIN MENU NAVIGATION ---

    @patch('pygame.quit')
    @patch('settings.Logic.Button.is_clicked')
    @patch('pygame.event.get')
    @patch('wordle.SettingsMenu.settings_menu')
    def test_navigate_to_settings(self, mock_settings, mock_events, mock_btn, _mock_quit):
        """Test navigation to settings menu."""
        mock_events.side_effect = [[self.make_click_event()], [self.make_quit_event()]]
        # Order: PVE, SINGLE, SOLVER, SETTINGS(True), RANK
        mock_btn.side_effect = [False, False, False, True, False]

        with self.assertRaises(SystemExit):
            wordle.main_menu()

        mock_settings.assert_called_once()

    @patch('pygame.quit')
    @patch('settings.Logic.Button.is_clicked')
    @patch('pygame.event.get')
    @patch('wordle.PveMode.run_pve')
    def test_navigate_to_pve(self, mock_pve, mock_events, mock_btn, _mock_quit):
        """Test navigation to PvE mode."""
        mock_events.side_effect = [[self.make_click_event()], [self.make_quit_event()]]
        # Order: PVE(True), SINGLE, SOLVER, SETTINGS, RANK
        mock_btn.side_effect = [True, False, False, False, False]

        with self.assertRaises(SystemExit):
            wordle.main_menu()

        mock_pve.assert_called_once()

    @patch('pygame.quit')
    @patch('settings.Logic.Button.is_clicked')
    @patch('pygame.event.get')
    @patch('wordle.Leaderboard.show_leaderboard')
    def test_navigate_to_ranklist(self, mock_rank, mock_events, mock_btn, _mock_quit):
        """Test navigation to Leaderboard."""
        mock_events.side_effect = [[self.make_click_event()], [self.make_quit_event()]]
        # Order: PVE, SINGLE, SOLVER, SETTINGS, RANK(True)
        mock_btn.side_effect = [False, False, False, False, True]

        with self.assertRaises(SystemExit):
            wordle.main_menu()

        mock_rank.assert_called_once()

    # --- MENU STRUCTURE CHECK ---
    def test_create_menu_buttons_structure(self):
        """Test that the main menu buttons have the correct IDs."""
        buttons = wordle.create_menu_buttons()
        self.assertEqual(len(buttons), 5)
        expected_ids = ["PVE", "SINGLE", "SOLVER", "SETTINGS", "RANK"]
        actual_ids = [btn.action_id for btn in buttons]
        self.assertEqual(actual_ids, expected_ids)


if __name__ == '__main__':
    unittest.main()