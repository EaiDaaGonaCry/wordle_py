"""
settings Menu Module.
Handles player configuration such as Name, Difficulty, and Word Length.
"""
import sys
from typing import Dict, Any, List
import pygame

from settings.Logic import Button
from settings import WordEditor
from settings.Constants import (
    WIDTH, COLOR_BG, COLOR_TEXT, COLOR_ACCENT,
    COLOR_PANEL_BG, COLOR_CORRECT, COLOR_BORDER
)

# Global Game settings Dictionary
game_settings: Dict[str, Any] = {
    "player_name": "Player",
    "word_length": 5,
    "difficulty": "NORMAL",
    "max_attempts": 6
}


def settings_menu() -> None:
    """Displays the settings Menu."""
    pygame.init()
    screen: pygame.Surface = pygame.display.get_surface()
    clock: pygame.time.Clock = pygame.time.Clock()

    font_title: pygame.font.Font = pygame.font.SysFont("Arial", 50, bold=True)
    font_label: pygame.font.Font = pygame.font.SysFont("Arial", 25)
    font_input: pygame.font.Font = pygame.font.SysFont("Arial", 30)

    center_x: int = WIDTH // 2

    # --- UI COORDINATES ---
    lbl_name_y: int = 130
    input_y: int = 160
    lbl_len_y: int = 250
    btns_len_y: int = 290
    lbl_att_y: int = 400
    btns_att_y: int = 440
    btn_edit_y: int = 560
    btn_back_y: int = 660

    # --- CREATE BUTTONS ---
    btn_len_5 = Button(center_x - 120, btns_len_y, 60, 60, "5", COLOR_PANEL_BG, action_id=5)
    btn_len_6 = Button(center_x - 30, btns_len_y, 60, 60, "6", COLOR_PANEL_BG, action_id=6)
    btn_len_7 = Button(center_x + 60, btns_len_y, 60, 60, "7", COLOR_PANEL_BG, action_id=7)
    len_btns: List[Button] = [btn_len_5, btn_len_6, btn_len_7]

    btn_att_minus = Button(center_x - 100, btns_att_y, 50, 50, "-", COLOR_PANEL_BG, action_id="DEC")
    btn_att_plus = Button(center_x + 50, btns_att_y, 50, 50, "+", COLOR_PANEL_BG, action_id="INC")

    btn_edit_file = Button(center_x - 150, btn_edit_y, 300, 50, "EDIT WORDS FILE",
                           (70, 70, 180), action_id="EDIT_FILE")

    btn_back = Button(center_x - 100, btn_back_y, 200, 60, "SAVE & BACK",
                      COLOR_PANEL_BG, action_id="BACK")

    input_rect: pygame.Rect = pygame.Rect(center_x - 100, input_y, 200, 50)
    active_input: bool = False

    running: bool = True
    while running:
        mouse_pos = pygame.mouse.get_pos()

        # Update Word Length Button States
        for btn in len_btns:
            btn.is_selected = (btn.action_id == game_settings["word_length"])
            if btn.is_selected:
                btn.color = COLOR_CORRECT
            else:
                btn.color = COLOR_PANEL_BG

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if btn_back.is_clicked(mouse_pos):
                    running = False

                if btn_edit_file.is_clicked(mouse_pos):
                    WordEditor.run_editor()

                for btn in len_btns:
                    if btn.is_clicked(mouse_pos):
                        game_settings["word_length"] = btn.action_id
                        if game_settings["max_attempts"] > game_settings["word_length"] + 1:
                            game_settings["max_attempts"] = game_settings["word_length"] + 1

                if btn_att_plus.is_clicked(mouse_pos):
                    if game_settings["max_attempts"] < game_settings["word_length"] + 1:
                        game_settings["max_attempts"] += 1
                if btn_att_minus.is_clicked(mouse_pos):
                    if game_settings["max_attempts"] > 2:
                        game_settings["max_attempts"] -= 1

                active_input = input_rect.collidepoint(mouse_pos)

            if event.type == pygame.KEYDOWN and active_input:
                if event.key == pygame.K_BACKSPACE:
                    game_settings["player_name"] = game_settings["player_name"][:-1]
                elif len(game_settings["player_name"]) < 12 and event.unicode.isprintable():
                    game_settings["player_name"] += event.unicode

        screen.fill(COLOR_BG)

        # Title
        title = font_title.render("SETTINGS", True, COLOR_TEXT)
        title_rect = title.get_rect(center=(center_x, 60))
        screen.blit(title, title_rect)

        # Player Name Label
        lbl_name = font_label.render("Player Name:", True, COLOR_ACCENT)
        lbl_name_rect = lbl_name.get_rect(center=(center_x, lbl_name_y))
        screen.blit(lbl_name, lbl_name_rect)

        # Draw Input Box
        color_input = COLOR_CORRECT if active_input else COLOR_BORDER
        pygame.draw.rect(screen, COLOR_PANEL_BG, input_rect, border_radius=5)
        pygame.draw.rect(screen, color_input, input_rect, 2, border_radius=5)

        name_surf = font_input.render(game_settings["player_name"], True, COLOR_TEXT)
        name_rect = name_surf.get_rect(center=input_rect.center)
        screen.blit(name_surf, name_rect)

        # Word Length Label & Buttons
        lbl_len = font_label.render("Word Length:", True, COLOR_ACCENT)
        lbl_len_rect = lbl_len.get_rect(center=(center_x, lbl_len_y))
        screen.blit(lbl_len, lbl_len_rect)
        for btn in len_btns:
            btn.draw(screen)

        # Attempts Label & Buttons
        lbl_att = font_label.render(f"Attempts: {game_settings['max_attempts']}",
                                    True, COLOR_ACCENT)
        lbl_att_rect = lbl_att.get_rect(center=(center_x, lbl_att_y))
        screen.blit(lbl_att, lbl_att_rect)

        btn_att_minus.draw(screen)
        btn_att_plus.draw(screen)

        # Bottom Buttons
        btn_edit_file.draw(screen)
        btn_back.draw(screen)

        pygame.display.flip()
        clock.tick(30)