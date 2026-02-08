"""
Word Editor Module.
Allows the user to view, add, edit, and delete words from the valid words file.
"""
import sys
from typing import List, Dict, Optional, Tuple
import pygame

from settings.Logic import Button
from settings.Constants import (
    WIDTH, HEIGHT, COLOR_BG, COLOR_TEXT, COLOR_CORRECT,
    COLOR_PANEL_BG, COLOR_ACCENT, COLOR_RED, COLOR_BORDER
)

FILE_PATH = "Files/valid-wordle-words.txt"


def load_words_from_file(filepath: str) -> List[str]:
    """Loads words from the text file, stripping whitespace."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return [line.strip().upper() for line in f.readlines() if line.strip()]
    except FileNotFoundError:
        return []


def save_words_to_file(filepath: str, words: List[str]) -> None:
    """Saves the current list of words to the file."""
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            for w in words:
                if w.strip():
                    f.write(w.strip().upper() + "\n")
    except OSError as e:
        print(f"Error saving file: {e}")


def create_editor_buttons(font_ui: pygame.font.Font) -> Dict[str, Button]:
    """Creates and returns the UI buttons for the editor."""
    btn_save = Button(WIDTH - 250, HEIGHT - 80, 200, 60, "SAVE & EXIT",
                      COLOR_CORRECT, action_id="SAVE")

    btn_cancel = Button(50, HEIGHT - 80, 200, 60, "CANCEL",
                        COLOR_PANEL_BG, action_id="CANCEL")

    btn_add = Button(WIDTH - 250, 20, 200, 50, "+ ADD NEW WORD",
                     (46, 134, 193), action_id="ADD", font=font_ui)

    btn_delete = Button(50, 20, 200, 50, "DELETE SELECTED",
                        COLOR_RED, action_id="DEL", font=font_ui)

    return {
        "save": btn_save,
        "cancel": btn_cancel,
        "add": btn_add,
        "delete": btn_delete
    }


def draw_word_list(screen: pygame.Surface, words: List[str],
                   config: Dict[str, int], fonts: Tuple[pygame.font.Font, pygame.font.Font],
                   selected_index: int) -> None:
    """
    Handles the complex logic of drawing the scrollable list of words with clipping.
    """
    panel_y = config["panel_y"]
    panel_h = config["panel_h"]
    row_height = config["row_height"]
    scroll_offset = config["scroll_offset"]
    visible_rows = config["visible_rows"]
    font_text, font_ui = fonts

    # Draw Panel Background
    pygame.draw.rect(screen, (30, 30, 35), (100, panel_y, WIDTH - 200, panel_h))
    pygame.draw.rect(screen, COLOR_BORDER, (100, panel_y, WIDTH - 200, panel_h), 2)

    # Calculate visible range
    start_idx = int(scroll_offset // row_height)
    end_idx = start_idx + visible_rows + 2

    # Set Clipping Area
    old_clip = screen.get_clip()
    screen.set_clip((100, panel_y, WIDTH - 200, panel_h))

    for i in range(start_idx, min(end_idx, len(words))):
        word = words[i]
        y_pos = panel_y + (i * row_height) - scroll_offset

        # Row Rectangle
        row_rect = pygame.Rect(102, y_pos, WIDTH - 204, row_height - 2)

        # Draw Row Selection/Background
        if i == selected_index:
            pygame.draw.rect(screen, (50, 50, 60), row_rect)
            pygame.draw.rect(screen, COLOR_CORRECT, row_rect, 2)
        else:
            pygame.draw.rect(screen, COLOR_PANEL_BG, row_rect)
            pygame.draw.rect(screen, (40, 40, 45), row_rect, 1)

        # Draw Word Text
        txt_surf = font_text.render(word, True, COLOR_TEXT)
        txt_rect = txt_surf.get_rect(midleft=(120, y_pos + row_height // 2))
        screen.blit(txt_surf, txt_rect)

        # Draw Index Number
        idx_surf = font_ui.render(str(i + 1), True, COLOR_ACCENT)
        screen.blit(idx_surf, (row_rect.right - 50, row_rect.y + 15))

    screen.set_clip(old_clip)


def run_editor() -> None:
    """
    Main loop for the Word Editor.
    """
    pygame.init()
    screen = pygame.display.get_surface()
    clock = pygame.time.Clock()

    # Key repeat for faster backspace deletion
    pygame.key.set_repeat(300, 50)

    # Fonts
    font_text = pygame.font.SysFont("Arial", 28)
    font_ui = pygame.font.SysFont("Arial", 20, bold=True)

    words_list = load_words_from_file(FILE_PATH)
    buttons = create_editor_buttons(font_ui)

    # UI Configuration
    row_height = 50
    panel_y = 100
    panel_h = HEIGHT - 200
    visible_rows = panel_h // row_height

    # State variables
    scroll_offset = 0
    selected_index = -1
    running = True

    while running:
        # Dynamic scroll limit calculation
        total_content_height = len(words_list) * row_height
        max_scroll = max(0, total_content_height - panel_h)

        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # --- MOUSE WHEEL ---
            if event.type == pygame.MOUSEWHEEL:
                scroll_offset -= event.y * 30
                scroll_offset = max(0, min(scroll_offset, max_scroll))

            # --- CLICKS ---
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Button Checks
                if buttons["save"].is_clicked(mouse_pos):
                    save_words_to_file(FILE_PATH, words_list)
                    running = False

                elif buttons["cancel"].is_clicked(mouse_pos):
                    running = False

                elif buttons["add"].is_clicked(mouse_pos):
                    words_list.insert(0, "")
                    selected_index = 0
                    scroll_offset = 0

                elif buttons["delete"].is_clicked(mouse_pos):
                    if 0 <= selected_index < len(words_list):
                        words_list.pop(selected_index)
                        selected_index = -1

                # List Row Selection Check
                elif panel_y <= mouse_pos[1] <= panel_y + panel_h:
                    relative_y = mouse_pos[1] - panel_y + scroll_offset
                    clicked_idx = int(relative_y // row_height)

                    if 0 <= clicked_idx < len(words_list):
                        selected_index = clicked_idx
                    else:
                        selected_index = -1
                else:
                    selected_index = -1

            # --- TYPING ---
            if event.type == pygame.KEYDOWN:
                if 0 <= selected_index < len(words_list):
                    if event.key == pygame.K_BACKSPACE:
                        words_list[selected_index] = words_list[selected_index][:-1]
                    elif event.key == pygame.K_RETURN:
                        selected_index = -1
                    elif event.unicode.isprintable() and len(words_list[selected_index]) < 12:
                        words_list[selected_index] += event.unicode.upper()

        # --- DRAWING ---
        screen.fill(COLOR_BG)

        # Title
        title = font_ui.render(f"WORD EDITOR ({len(words_list)} words)", True, COLOR_TEXT)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 30))

        draw_config = {
            "panel_y": panel_y, "panel_h": panel_h,
            "row_height": row_height, "scroll_offset": scroll_offset,
            "visible_rows": visible_rows
        }

        draw_word_list(screen, words_list, draw_config, (font_text, font_ui), selected_index)

        # Draw Scrollbar
        if total_content_height > panel_h:
            scrollbar_h = max(30, (panel_h / total_content_height) * panel_h)
            scrollbar_y = panel_y + (scroll_offset / max_scroll) * (panel_h - scrollbar_h)
            pygame.draw.rect(screen, COLOR_ACCENT,
                             (WIDTH - 120, scrollbar_y, 10, scrollbar_h),
                             border_radius=5)

        # Draw Buttons
        buttons["save"].draw(screen)
        buttons["cancel"].draw(screen)
        buttons["add"].draw(screen)

        if selected_index != -1:
            buttons["delete"].draw(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.key.set_repeat(0)