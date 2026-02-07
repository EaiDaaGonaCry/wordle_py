"""
AI Solver Mode.
In this mode, the User enters a secret word (mentally), and the AI tries to guess it.
The user provides feedback (Green/Yellow/Gray) for the AI's suggestions.
"""
import sys
import random
from typing import List, Dict, Tuple
import pygame

from settings.Logic import (
    load_valid_words, filter_words, get_best_word, lie_detector,
    init_extreme_candidates, Button
)
from settings.Constants import (
    WIDTH, HEIGHT, FONT_NAME, FONT_SIZE_TITLE, FONT_SIZE_MED,
    FONT_SIZE_SMALL, COLOR_PANEL_BG, COLOR_CORRECT, COLOR_PRESENT,
    COLOR_ABSENT, COLOR_BORDER, COLOR_BLUE, COLOR_ACCENT,
    COLOR_TEXT, COLOR_BG, COLOR_RED
)


def get_fonts() -> Dict[str, pygame.font.Font]:
    """Initializes and returns the required fonts."""
    return {
        "large": pygame.font.SysFont(FONT_NAME, FONT_SIZE_TITLE, bold=True),
        "med": pygame.font.SysFont(FONT_NAME, FONT_SIZE_MED, bold=True),
        "small": pygame.font.SysFont(FONT_NAME, FONT_SIZE_SMALL),
        "result": pygame.font.SysFont(FONT_NAME, 40, bold=True)
    }


def draw_tile(screen: pygame.Surface, x: int, y: int, size: int,
              letter: str, color_code: str, font: pygame.font.Font) -> None:
    """Draws a single letter tile with the appropriate background color."""
    bg_color = COLOR_PANEL_BG
    if color_code == 'g':
        bg_color = COLOR_CORRECT
    elif color_code == 'y':
        bg_color = COLOR_PRESENT
    elif color_code == 'x':
        bg_color = COLOR_ABSENT

    rect = pygame.Rect(x, y, size, size)
    pygame.draw.rect(screen, bg_color, rect, border_radius=4)
    pygame.draw.rect(screen, COLOR_BORDER, rect, 2, border_radius=4)

    if letter:
        text_surf = font.render(letter, True, COLOR_TEXT)
        text_rect = text_surf.get_rect(center=rect.center)
        screen.blit(text_surf, text_rect)


def draw_history_panel(screen: pygame.Surface, rect: pygame.Rect,
                       history: List[Tuple[str, str]], fonts: Dict[str, pygame.font.Font]) -> None:
    """Draws the list of previous guesses made by the AI."""
    pygame.draw.rect(screen, COLOR_PANEL_BG, rect, border_radius=10)
    pygame.draw.rect(screen, COLOR_BLUE, rect, 2, border_radius=10)

    title = fonts["med"].render("HISTORY", True, COLOR_BLUE)
    screen.blit(title, (rect.x + 20, rect.y + 20))

    start_y = rect.y + 70
    tile_size = 40
    padding = 5

    for i, (word, pattern) in enumerate(history):
        # Draw Index
        idx_surf = fonts["small"].render(f"{i + 1}.", True, COLOR_ACCENT)
        screen.blit(idx_surf, (rect.x + 15, start_y + 10))

        # Draw Word Tiles
        for j, char in enumerate(word):
            draw_tile(screen, rect.x + 50 + (j * (tile_size + padding)),
                      start_y, tile_size, char, pattern[j], fonts["med"])
        start_y += tile_size + 10


def draw_input_panel(screen: pygame.Surface, rect: pygame.Rect, current_suggestion: str,
                     input_pattern: str, message: str, word_length: int,
                     fonts: Dict[str, pygame.font.Font]) -> None:
    """Draws the main interaction area where the user inputs the color pattern."""
    pygame.draw.rect(screen, COLOR_PANEL_BG, rect, border_radius=10)
    pygame.draw.rect(screen, COLOR_CORRECT, rect, 2, border_radius=10)

    # Labels
    screen.blit(fonts["small"].render("AI SUGGESTION:", True, COLOR_CORRECT), (rect.x + 20, rect.y + 20))
    screen.blit(fonts["large"].render(current_suggestion, True, COLOR_TEXT), (rect.x + 20, rect.y + 50))
    screen.blit(fonts["small"].render("ENTER PATTERN (Click or Type G/Y/X):", True, COLOR_ACCENT),
                (rect.x + 20, rect.y + 130))

    # Tiles
    tile_size = 80
    gap = 10
    total_width = (word_length * tile_size) + ((word_length - 1) * gap)
    start_x = rect.x + (rect.width - total_width) // 2
    tile_y = rect.y + 170

    for i in range(word_length):
        color_code = input_pattern[i] if i < len(input_pattern) else ''
        letter = current_suggestion[i] if i < len(current_suggestion) else ""
        draw_tile(screen, start_x + i * (tile_size + gap), tile_y, tile_size,
                  letter, color_code, fonts["med"])

    # Message
    msg_color = COLOR_PRESENT if "Error" in message else COLOR_TEXT
    msg_surf = fonts["small"].render(message, True, msg_color)
    screen.blit(msg_surf, (rect.centerx - msg_surf.get_width() // 2, rect.y + 270))


def draw_stats_panel(screen: pygame.Surface, rect: pygame.Rect, words_left: int,
                     attempts: int, fonts: Dict[str, pygame.font.Font]) -> None:
    """Draws the statistics panel (Possible words remaining)."""
    pygame.draw.rect(screen, COLOR_PANEL_BG, rect, border_radius=10)
    pygame.draw.rect(screen, COLOR_RED, rect, 2, border_radius=10)

    screen.blit(fonts["med"].render("STATISTICS", True, COLOR_RED), (rect.x + 20, rect.y + 20))
    screen.blit(fonts["med"].render(f"POSSIBLE WORDS: {words_left}", True, COLOR_TEXT),
                (rect.x + 40, rect.y + 80))
    screen.blit(fonts["med"].render(f"ATTEMPTS: {attempts}", True, COLOR_TEXT),
                (rect.x + 40, rect.y + 140))


def draw_end_message(screen: pygame.Surface, panel_rect: pygame.Rect, won: bool,
                     word: str, fonts: Dict[str, pygame.font.Font]) -> None:
    """Draws the overlay when the game ends."""
    # Dark Overlay
    overlay_surf = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA)
    overlay_surf.fill((0, 0, 0, 230))
    screen.blit(overlay_surf, (panel_rect.x, panel_rect.y))

    center_x = panel_rect.centerx
    center_y = panel_rect.centery

    msg = "VICTORY!" if won else "GAME OVER"
    color = COLOR_CORRECT if won else COLOR_RED

    text_surf = fonts["result"].render(msg, True, color)
    text_rect = text_surf.get_rect(center=(center_x, center_y - 80))
    screen.blit(text_surf, text_rect)

    if not won:
        sub_text = fonts["small"].render("No matching words found in dictionary.", True, COLOR_TEXT)
        sub_rect = sub_text.get_rect(center=(center_x, center_y - 20))
        screen.blit(sub_text, sub_rect)

    if won:
        word_msg = f"The word was: {word}"
        word_surf = fonts["result"].render(word_msg, True, (255, 255, 255))
        word_rect = word_surf.get_rect(center=(center_x, center_y + 20))
        screen.blit(word_surf, word_rect)


def run_ai_mode(difficulty: str, word_length: int = 5) -> str:
    """
    Main loop for the AI Solver Mode.
    """
    pygame.init()
    screen = pygame.display.get_surface()
    fonts = get_fonts()

    # Load Words
    try:
        possible_words = load_valid_words("Files/valid-wordle-words.txt", length=word_length)
    except FileNotFoundError:
        possible_words = ["ERROR"]

    # Extreme Mode Setup
    extreme_candidates: Dict[str, int] = {}
    if difficulty == "EXTREME":
        extreme_candidates = init_extreme_candidates(possible_words)

    if not possible_words:
        possible_words = ["ERROR"]

    # Game State
    guessed_history: List[Tuple[str, str]] = []
    current_suggestion = random.choice(possible_words)
    input_pattern: List[str] = []
    attempts = 1
    message = "Click boxes or type G/Y/X"
    game_state = "PLAYING"

    clock = pygame.time.Clock()
    running = True

    # Layout Rects
    history_rect = pygame.Rect(20, 20, 400, HEIGHT - 40)
    input_rect = pygame.Rect(440, 20, 740, 400)
    stats_rect = pygame.Rect(440, 440, 740, HEIGHT - 460)

    # Buttons
    btn_w, btn_h = 240, 50
    submit_btn = Button(
        input_rect.centerx - btn_w // 2,
        input_rect.bottom - 60,
        btn_w, btn_h,
        "SUBMIT PATTERN",
        (80, 80, 90)
    )

    end_btn_w, end_btn_h = 120, 50
    gap = 20
    restart_x = input_rect.centerx - end_btn_w - (gap // 2)
    home_x = input_rect.centerx + (gap // 2)
    btn_y = input_rect.centery + 100

    restart_btn = Button(restart_x, btn_y, end_btn_w, end_btn_h, "RESTART", (60, 60, 70))
    home_btn = Button(home_x, btn_y, end_btn_w, end_btn_h, "HOME", (60, 60, 70))

    while running:
        # --- Logic Helper ---
        def execute_turn() -> None:
            nonlocal game_state, current_suggestion, attempts, message, possible_words, extreme_candidates

            pat_str = "".join(input_pattern)

            if pat_str == ("g" * word_length):
                game_state = "WON"
                guessed_history.append((current_suggestion, pat_str))
            else:
                guessed_history.append((current_suggestion, pat_str))
                attempts += 1
                message = "CALCULATING..."

                # Render loading state immediately
                screen.fill(COLOR_BG)
                draw_history_panel(screen, history_rect, guessed_history, fonts)
                draw_input_panel(screen, input_rect, current_suggestion, pat_str, message, word_length, fonts)
                draw_stats_panel(screen, stats_rect, len(possible_words), attempts, fonts)
                pygame.display.flip()

                # Filter Logic
                if difficulty == "EXTREME":
                    extreme_candidates = lie_detector(pat_str, current_suggestion, extreme_candidates)
                    possible_words = list(extreme_candidates.keys())
                else:
                    possible_words = filter_words(pat_str, current_suggestion, possible_words)

                # Determine Next Step
                if not possible_words:
                    game_state = "LOST"
                elif len(possible_words) == 1:
                    current_suggestion = possible_words[0]
                    message = "SOLVED! Word found."
                    game_state = "WON"
                else:
                    if pat_str == ("x" * word_length) or len(extreme_candidates) > 10000:
                        current_suggestion = random.choice(possible_words)
                    else:
                        current_suggestion = get_best_word(possible_words)
                    message = "Type pattern for new word"

                input_pattern.clear()

        # --- Event Loop ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if game_state == "PLAYING":
                    # Tile Click Logic
                    tile_size = 80
                    gap = 10
                    total_width = (word_length * tile_size) + ((word_length - 1) * gap)
                    start_x = input_rect.x + (input_rect.width - total_width) // 2
                    tile_y = input_rect.y + 170

                    for i in range(word_length):
                        t_rect = pygame.Rect(start_x + i * (tile_size + gap), tile_y, tile_size, tile_size)
                        if t_rect.collidepoint(event.pos):
                            while len(input_pattern) <= i:
                                input_pattern.append('x')
                            curr = input_pattern[i]
                            # Cycle colors: x -> y -> g -> x
                            if curr == 'x':
                                input_pattern[i] = 'y'
                            elif curr == 'y':
                                input_pattern[i] = 'g'
                            else:
                                input_pattern[i] = 'x'

                    if submit_btn.is_clicked(event.pos) and len(input_pattern) == word_length:
                        execute_turn()

                else:
                    # Game Over Buttons
                    if restart_btn.is_clicked(event.pos):
                        # Reset
                        if difficulty == "EXTREME":
                            extreme_candidates = init_extreme_candidates(
                                load_valid_words("Files/valid-wordle-words.txt", length=word_length))
                            possible_words = list(extreme_candidates.keys())
                        else:
                            possible_words = load_valid_words("Files/valid-wordle-words.txt", length=word_length)

                        guessed_history = []
                        current_suggestion = random.choice(possible_words)
                        input_pattern = []
                        attempts = 1
                        message = "Click boxes or type G/Y/X"
                        game_state = "PLAYING"

                    elif home_btn.is_clicked(event.pos):
                        return "HOME"

            if event.type == pygame.KEYDOWN and game_state == "PLAYING":
                if event.key == pygame.K_g:
                    if len(input_pattern) < word_length: input_pattern.append('g')
                elif event.key == pygame.K_y:
                    if len(input_pattern) < word_length: input_pattern.append('y')
                elif event.key == pygame.K_x:
                    if len(input_pattern) < word_length: input_pattern.append('x')
                elif event.key == pygame.K_BACKSPACE:
                    if len(input_pattern) > 0: input_pattern.pop()
                elif event.key == pygame.K_RETURN:
                    if len(input_pattern) == word_length:
                        execute_turn()

        # --- Draw ---
        screen.fill(COLOR_BG)
        draw_history_panel(screen, history_rect, guessed_history, fonts)
        draw_input_panel(screen, input_rect, current_suggestion, "".join(input_pattern), message, word_length, fonts)
        draw_stats_panel(screen, stats_rect, len(possible_words), attempts, fonts)

        if game_state == "PLAYING":
            submit_btn.draw(screen)
        else:
            draw_end_message(screen, input_rect, game_state == "WON", current_suggestion, fonts)
            restart_btn.draw(screen)
            home_btn.draw(screen)

        pygame.display.flip()
        clock.tick(30)

    return "HOME"