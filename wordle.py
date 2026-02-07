"""
Wordle Master - Main Entry Point.
Handles the main menu, loading screen, and game mode selection.
"""
import sys
from typing import Optional, List, Dict, Any
import pygame

from modes import AiMode, PlayerMode, PveMode
from settings.Logic import Button
from settings import SettingsMenu
from settings import Leaderboard
from settings import DifficultyMenu

from settings.Constants import (
    WIDTH, HEIGHT, COLOR_BG, COLOR_CORRECT, COLOR_ACCENT,
    COLOR_PANEL_BG, COLOR_ABSENT_BORDER, COLOR_TEXT,
    COLOR_ABSENT, COLOR_GOLD, COLOR_GOLD_HOVER, COLOR_GOLD_BORDER
)

pygame.init()

# Global Constants
SCREEN: pygame.Surface = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Wordle Master")

FONT_TITLE: pygame.font.Font = pygame.font.SysFont("Arial", 50, bold=True)
FONT_SETTINGS: pygame.font.Font = pygame.font.SysFont("Arial", 25)


def show_loading_screen(duration: int) -> None:
    """
    Displays a loading screen for a specified duration.
    """
    splash_font: pygame.font.Font = pygame.font.SysFont("Arial", 80, bold=True)
    start_time: int = pygame.time.get_ticks()

    running: bool = True
    while running:
        current_time: int = pygame.time.get_ticks()
        if current_time - start_time >= duration:
            running = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        SCREEN.fill(COLOR_BG)

        # Draw Title
        text_surf: pygame.Surface = splash_font.render("WORDLE MASTER", True, COLOR_CORRECT)
        text_rect: pygame.Rect = text_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        SCREEN.blit(text_surf, text_rect)

        # Draw Loading Text
        loading_text = "Loading settings..."
        loading_surf: pygame.Surface = FONT_SETTINGS.render(loading_text, True, COLOR_ACCENT)
        loading_rect: pygame.Rect = loading_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 80))
        SCREEN.blit(loading_surf, loading_rect)

        pygame.display.flip()
        pygame.time.Clock().tick(30)


def get_difficulty() -> Optional[str]:
    """
    Runs a standalone loop for difficulty selection (Normal/Extreme).
    Returns: "NORMAL", "EXTREME", or None (if closed/cancelled).
    """
    screen: pygame.Surface = pygame.display.get_surface()

    btn_w: int = 300
    btn_h: int = 80
    gap: int = 20

    center_x: int = WIDTH // 2
    center_y: int = HEIGHT // 2
    start_btn_y: int = center_y - 20

    title_font: pygame.font.Font = pygame.font.SysFont("Arial", 40, bold=True)

    # Create Buttons
    btn_normal = Button(center_x - btn_w // 2, start_btn_y, btn_w, btn_h, "NORMAL",
                        color=COLOR_PANEL_BG,
                        hover_color=COLOR_CORRECT,
                        border_color=COLOR_ABSENT_BORDER,
                        action_id="NORMAL")

    btn_extreme = Button(center_x - btn_w // 2, start_btn_y + btn_h + gap, btn_w, btn_h, "EXTREME",
                         color=COLOR_PANEL_BG,
                         hover_color=COLOR_ACCENT,
                         border_color=COLOR_ABSENT_BORDER,
                         action_id="EXTREME")

    btn_back = Button(center_x - btn_w // 2, start_btn_y + 2 * (btn_h + gap), btn_w, btn_h, "BACK",
                      color=COLOR_PANEL_BG,
                      hover_color=COLOR_ABSENT,
                      border_color=COLOR_ABSENT_BORDER,
                      action_id="BACK")

    buttons: List[Button] = [btn_normal, btn_extreme, btn_back]

    # Menu Loop
    running: bool = True
    while running:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                for btn in buttons:
                    if btn.is_clicked(mouse_pos):
                        if btn.action_id == "BACK":
                            return None
                        return btn.action_id

        screen.fill(COLOR_BG)

        title_surf: pygame.Surface = title_font.render("SELECT DIFFICULTY", True, COLOR_TEXT)
        title_rect: pygame.Rect = title_surf.get_rect(center=(center_x, center_y - 100))
        screen.blit(title_surf, title_rect)

        for btn in buttons:
            btn.draw(screen)

        pygame.display.flip()
        pygame.time.Clock().tick(30)

    return None


def create_menu_buttons() -> List[Button]:
    """Helper to create the list of main menu buttons."""
    btn_w: int = 400
    btn_h: int = 100
    gap: int = 30
    center_x: int = (WIDTH - btn_w) // 2
    start_y: int = 200

    # Game modes
    btn_pve = Button(center_x, start_y, btn_w, btn_h, "PVE",
                     color=COLOR_PANEL_BG,
                     hover_color=COLOR_ABSENT,
                     border_color=COLOR_ABSENT_BORDER,
                     action_id="PVE")

    btn_single = Button(center_x, start_y + btn_h + gap, btn_w, btn_h, "SINGLE PLAYER",
                        color=COLOR_PANEL_BG,
                        hover_color=COLOR_ABSENT,
                        border_color=COLOR_ABSENT_BORDER,
                        action_id="SINGLE")

    btn_solver = Button(center_x, start_y + 2 * (btn_h + gap), btn_w, btn_h, "SOLVER",
                        color=COLOR_PANEL_BG,
                        hover_color=COLOR_ABSENT,
                        border_color=COLOR_ABSENT_BORDER,
                        action_id="SOLVER")

    # Bottom Extras
    bottom_w: int = 140
    bottom_h: int = 70

    btn_settings = Button(WIDTH - bottom_w - 20, HEIGHT - bottom_h - 20, bottom_w, bottom_h, "settings",
                          color=COLOR_PANEL_BG,
                          hover_color=COLOR_ABSENT,
                          border_color=COLOR_ABSENT_BORDER,
                          action_id="SETTINGS",
                          font=FONT_SETTINGS)

    btn_rank = Button(20, HEIGHT - bottom_h - 20, bottom_w, bottom_h, "RANKLIST",
                      color=COLOR_GOLD,
                      hover_color=COLOR_GOLD_HOVER,
                      border_color=COLOR_GOLD_BORDER,
                      action_id="RANK",
                      font=FONT_SETTINGS,
                      text_color=(255, 255, 255))

    return [btn_pve, btn_single, btn_solver, btn_settings, btn_rank]


def handle_menu_action(action_id: str) -> None:
    """Handles the logic when a main menu button is clicked."""
    if action_id == "SETTINGS":
        SettingsMenu.settings_menu()

    elif action_id == "RANK":
        Leaderboard.show_leaderboard()

    elif action_id == "PVE":
        PveMode.run_pve(SettingsMenu.game_settings)
        pygame.display.set_caption("Wordle Master")

    elif action_id == "SINGLE":
        difficulty: Optional[str] = DifficultyMenu.get_difficulty()
        if difficulty:
            settings: Dict[str, Any] = SettingsMenu.game_settings.copy()
            settings["difficulty"] = difficulty
            curr: str = "RESTART"

            while curr == "RESTART":
                curr = PlayerMode.run_game(settings)

            if curr == "QUIT":
                pygame.quit()
                sys.exit()
            pygame.display.set_caption("Wordle Master")

    elif action_id == "SOLVER":
        difficulty = DifficultyMenu.get_difficulty()
        if difficulty:
            curr = "RESTART"
            while curr == "RESTART":
                length: int = int(SettingsMenu.game_settings["word_length"])
                curr = AiMode.run_ai_mode(difficulty, word_length=length)

            if curr == "QUIT":
                pygame.quit()
                sys.exit()
            pygame.display.set_caption("Wordle Master")


def main_menu() -> None:
    """
    The main menu loop.
    Displays buttons and handles navigation to other modes.
    """
    buttons = create_menu_buttons()

    running: bool = True
    while running:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                for btn in buttons:
                    if btn.is_clicked(mouse_pos):
                        handle_menu_action(btn.action_id)

        SCREEN.fill(COLOR_BG)

        # Title
        title_surf: pygame.Surface = FONT_TITLE.render("WORDLE MASTER", True, COLOR_TEXT)
        title_rect: pygame.Rect = title_surf.get_rect(center=(WIDTH // 2, 100))
        SCREEN.blit(title_surf, title_rect)

        for btn in buttons:
            btn.draw(SCREEN)

        pygame.display.flip()


if __name__ == "__main__":
    show_loading_screen(1500)
    SettingsMenu.settings_menu()
    main_menu()