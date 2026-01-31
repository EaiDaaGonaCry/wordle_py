import pygame
import sys
import random
from Settings.Logic import load_valid_words, filter_words, get_best_word, Button
from Settings.Constants import *

# =============================================================================
# --- CONSTANTS & STYLING ---
# =============================================================================

pygame.init()
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Word Guesser")
# Fonts
FONT_LARGE  = pygame.font.SysFont(FONT_NAME, FONT_SIZE_TITLE, bold=True)
FONT_MED    = pygame.font.SysFont(FONT_NAME, FONT_SIZE_MED, bold=True)
FONT_SMALL  = pygame.font.SysFont(FONT_NAME, FONT_SIZE_SMALL)
FONT_RESULT = pygame.font.SysFont(FONT_NAME, 40, bold=True)

def draw_tile(screen, x, y, size, letter, color_code):
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
        text_surf = FONT_MED.render(letter, True, COLOR_TEXT)
        text_rect = text_surf.get_rect(center=rect.center)
        screen.blit(text_surf, text_rect)

def draw_history_panel(screen, rect, history):
    pygame.draw.rect(screen, COLOR_PANEL_BG, rect, border_radius=10)
    pygame.draw.rect(screen, COLOR_BLUE, rect, 2, border_radius=10)

    title = FONT_MED.render("HISTORY", True, COLOR_BLUE)
    screen.blit(title, (rect.x + 20, rect.y + 20))

    start_y = rect.y + 70
    tile_size = 40
    padding = 5

    for i, (word, pattern) in enumerate(history):
        # Draw number
        screen.blit(FONT_SMALL.render(f"{i + 1}.", True, COLOR_ACCENT), (rect.x + 15, start_y + 10))
        # Draw tiles
        for j, char in enumerate(word):
            draw_tile(screen, rect.x + 50 + (j * (tile_size + padding)), start_y, tile_size, char, pattern[j])
        start_y += tile_size + 10


def draw_input_panel(screen, rect, current_suggestion, input_pattern, message):
    pygame.draw.rect(screen, COLOR_PANEL_BG, rect, border_radius=10)
    pygame.draw.rect(screen, COLOR_CORRECT, rect, 2, border_radius=10)

    # Text
    screen.blit(FONT_SMALL.render("AI SUGGESTION:", True, COLOR_CORRECT), (rect.x + 20, rect.y + 20))
    screen.blit(FONT_LARGE.render(current_suggestion, True, COLOR_TEXT), (rect.x + 20, rect.y + 50))
    screen.blit(FONT_SMALL.render("ENTER PATTERN (Click or Type G/Y/X):", True, COLOR_ACCENT),
                (rect.x + 20, rect.y + 130))

    tile_size = 80
    gap = 10
    start_x = rect.x + (rect.width - (5 * tile_size + 4 * gap)) // 2
    tile_y = rect.y + 170

    click_rects = []
    for i in range(5):
        color_code = input_pattern[i] if i < len(input_pattern) else ''
        letter = current_suggestion[i] if i < len(current_suggestion) else ""

        draw_tile(screen, start_x + i * (tile_size + gap), tile_y, tile_size, letter, color_code)
        click_rects.append(pygame.Rect(start_x + i * (tile_size + gap), tile_y, tile_size, tile_size))

    # Message
    msg_color = COLOR_PRESENT if "Error" in message else COLOR_TEXT
    msg_surf = FONT_SMALL.render(message, True, msg_color)
    screen.blit(msg_surf, (rect.centerx - msg_surf.get_width() // 2, rect.y + 270))

    return click_rects


def draw_stats_panel(screen, rect, words_left, attempts):
    pygame.draw.rect(screen, COLOR_PANEL_BG, rect, border_radius=10)
    pygame.draw.rect(screen, COLOR_RED, rect, 2, border_radius=10)

    screen.blit(FONT_MED.render("STATISTICS", True, COLOR_RED), (rect.x + 20, rect.y + 20))
    screen.blit(FONT_MED.render(f"POSSIBLE WORDS: {words_left}", True, COLOR_TEXT), (rect.x + 40, rect.y + 80))
    screen.blit(FONT_MED.render(f"ATTEMPTS: {attempts}", True, COLOR_TEXT), (rect.x + 40, rect.y + 140))

def draw_end_message(screen, panel_rect, won):
    overlay_surf = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA)
    overlay_surf.fill((0, 0, 0, 200))
    screen.blit(overlay_surf, (panel_rect.x, panel_rect.y))

    msg = "VICTORY!" if won else "GAME OVER"
    color = COLOR_CORRECT if won else COLOR_RED

    text_surf = FONT_RESULT.render(msg, True, color)
    text_rect = text_surf.get_rect(center=(panel_rect.centerx, panel_rect.centery - 50))
    screen.blit(text_surf, text_rect)

    if not won:
        sub_text = FONT_SMALL.render("No matching words found.", True, COLOR_TEXT)
        sub_rect = sub_text.get_rect(center=(panel_rect.centerx, panel_rect.centery - 10))
        screen.blit(sub_text, sub_rect)

def run_ai_mode():
    try:
        # use "../Files/valid-wordle-words.txt"
        # if you want to test only this file
        # use "Files/valid-wordle-words.txt"
        # if you want to use the program
        possible_words = load_valid_words("Files/valid-wordle-words.txt")
    except:
        possible_words = ["ERROR"]

    guessed_history = []
    current_suggestion = random.choice(possible_words)

    input_pattern = []
    attempts = 1
    message = "Click boxes or type G/Y/X"
    game_state = "PLAYING"

    clock = pygame.time.Clock()
    running = True

    history_rect = pygame.Rect(20, 20, 400, HEIGHT - 40)
    input_rect = pygame.Rect(440, 20, 740, 400)
    stats_rect = pygame.Rect(440, 440, 740, HEIGHT - 460)

    btn_w, btn_h = 200, 50
    submit_btn = Button(
        input_rect.centerx - btn_w // 2,
        input_rect.bottom - 60,
        btn_w, btn_h,
        "SUBMIT PATTERN",
        (80, 80, 90)
    )

    # End Game Buttons
    end_btn_w, end_btn_h = 120, 50
    gap = 20
    restart_x = input_rect.centerx - end_btn_w - (gap // 2)
    home_x = input_rect.centerx + (gap // 2)
    btn_y = input_rect.centery + 40
    restart_btn = Button(restart_x, btn_y, end_btn_w, end_btn_h, "RESTART", (60, 60, 70))
    home_btn = Button(home_x, btn_y, end_btn_w, end_btn_h, "HOME", (60, 60, 70))

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if game_state == "PLAYING":
                    # Tile Clicks
                    tile_size = 80;
                    gap = 10
                    start_x = input_rect.x + (input_rect.width - (5 * tile_size + 4 * gap)) // 2
                    tile_y = input_rect.y + 170

                    for i in range(5):
                        t_rect = pygame.Rect(start_x + i * (tile_size + gap), tile_y, tile_size, tile_size)
                        if t_rect.collidepoint(event.pos):
                            while len(input_pattern) <= i: input_pattern.append('x')
                            curr = input_pattern[i]
                            input_pattern[i] = 'y' if curr == 'x' else 'g' if curr == 'y' else 'x'

                    # Submit Click
                    if submit_btn.is_clicked(event.pos) and len(input_pattern) == 5:
                        pat_str = "".join(input_pattern)

                        # --- GAME LOGIC ---
                        if pat_str == "ggggg":
                            game_state = "WON"
                            guessed_history.append((current_suggestion, pat_str))
                        else:
                            guessed_history.append((current_suggestion, pat_str))
                            attempts += 1

                            # Draw Loading Screen
                            message = "CALCULATING..."
                            SCREEN.fill(COLOR_BG)
                            draw_history_panel(SCREEN, history_rect, guessed_history)
                            draw_input_panel(SCREEN, input_rect, current_suggestion, pat_str, message)
                            draw_stats_panel(SCREEN, stats_rect, len(possible_words), attempts)
                            pygame.display.flip()

                            possible_words = filter_words(pat_str, current_suggestion, possible_words)

                            if len(possible_words) == 0:
                                game_state = "LOST"
                            elif len(possible_words) == 1:
                                current_suggestion = possible_words[0]
                                message = "SOLVED! Word found."
                                game_state = "WON"
                            else:

                                if pat_str == "xxxxx":
                                    current_suggestion = random.choice(possible_words)
                                else:
                                    current_suggestion = get_best_word(possible_words)

                                message = "Type pattern for new word"
                            input_pattern = []

                else:  # GAME OVER
                    if restart_btn.is_clicked(event.pos):
                        guessed_history = []
                        current_suggestion = random.choice(possible_words)  # Random start again
                        input_pattern = []
                        attempts = 1
                        message = "Click boxes or type G/Y/X"
                        game_state = "PLAYING"
                    elif home_btn.is_clicked(event.pos):
                        return "HOME"

            # Keyboard Input
            if event.type == pygame.KEYDOWN and game_state == "PLAYING":
                if event.key == pygame.K_g:
                    if len(input_pattern) < 5: input_pattern.append('g')
                elif event.key == pygame.K_y:
                    if len(input_pattern) < 5: input_pattern.append('y')
                elif event.key == pygame.K_x:
                    if len(input_pattern) < 5: input_pattern.append('x')
                elif event.key == pygame.K_BACKSPACE:
                    if len(input_pattern) > 0: input_pattern.pop()
                elif event.key == pygame.K_RETURN:
                    if len(input_pattern) == 5:
                        # (Duplicate Logic for Keyboard Enter)
                        pat_str = "".join(input_pattern)
                        if pat_str == "ggggg":
                            game_state = "WON"
                            guessed_history.append((current_suggestion, pat_str))
                        else:
                            guessed_history.append((current_suggestion, pat_str))
                            attempts += 1

                            message = "CALCULATING..."
                            SCREEN.fill(COLOR_BG)
                            draw_history_panel(SCREEN, history_rect, guessed_history)
                            draw_input_panel(SCREEN, input_rect, current_suggestion, pat_str, message)
                            draw_stats_panel(SCREEN, stats_rect, len(possible_words), attempts)
                            pygame.display.flip()

                            possible_words = filter_words(pat_str, current_suggestion, possible_words)

                            if len(possible_words) == 0:
                                game_state = "LOST"
                            elif len(possible_words) == 1:
                                current_suggestion = possible_words[0]
                                message = "SOLVED!"
                            else:
                                if pat_str == "xxxxx":
                                    current_suggestion = random.choice(possible_words)
                                else:
                                    current_suggestion = get_best_word(possible_words)

                                message = "Type pattern for new word"
                            input_pattern = []

        SCREEN.fill(COLOR_BG)
        draw_history_panel(SCREEN, history_rect, guessed_history)
        draw_input_panel(SCREEN, input_rect, current_suggestion, "".join(input_pattern), message)
        draw_stats_panel(SCREEN, stats_rect, len(possible_words), attempts)

        if game_state == "PLAYING":
            submit_btn.draw(SCREEN)
        else:
            draw_end_message(SCREEN, input_rect, game_state == "WON")
            restart_btn.draw(SCREEN)
            home_btn.draw(SCREEN)

        pygame.display.flip()
        clock.tick(30)


if __name__ == "__main__":
    run_ai_mode()