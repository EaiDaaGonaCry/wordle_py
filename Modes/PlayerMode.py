import pygame
from Settings import JsonStats
import random
from Settings.Logic import colour_set, load_valid_words, Button
from Settings.Constants import *

pygame.init()

# KEEP: Screen setup (now uses WIDTH/HEIGHT from Constants)
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Wordle The Game")

FONT_GUESS        = pygame.font.SysFont(FONT_NAME, FONT_SIZE_GUESS)
FONT_ALPHABETICAL = pygame.font.SysFont(FONT_NAME, 24)
FONT_RESULT       = pygame.font.SysFont(FONT_NAME, 40, bold=True)
FONT_SMALL        = pygame.font.SysFont(FONT_NAME, FONT_SIZE_SMALL)

#function that draws the grid for wordle
def draw_grid(guesses, current_guess_string, error_timer):
    box_size = 88
    margin = 5

    start_x = (WIDTH - (5 * box_size + 4 * margin) - (10*40 + 9*5)) // 2
    start_y = 100

    for row in range(6):
        for col in range(5):
            x = start_x + col * (box_size + margin)
            y = start_y + row * (box_size + margin)

            color = COLOR_PANEL_BG
            letter = ""
            border_color = COLOR_ABSENT_BORDER

            if row < len(guesses):
                triplet = guesses[row][col]
                letter = triplet[0]
                color_code = triplet[2]

                if color_code   == "g":
                    color = COLOR_CORRECT
                    border_color = COLOR_CORRECT_BORDER
                elif color_code == "y":
                    color = COLOR_PRESENT
                    border_color = COLOR_PRESENT_BORDER
                else:
                    color = COLOR_ABSENT
                    border_color = COLOR_ABSENT_BORDER

            elif row == len(guesses):
                if col < len(current_guess_string):
                    letter = current_guess_string[col]
                    border_color = COLOR_ABSENT

                if error_timer > 0:
                    border_color = COLOR_RED
                    shake_offset = 5 if (error_timer // 2) % 2 == 0 else -5
                    x += shake_offset
                else:
                    border_color = COLOR_TEXT if letter != "" else COLOR_ABSENT_BORDER

            rect = pygame.Rect(x, y, box_size, box_size)

            # 1. First, draw the FILL (The background of the box)
            # This ensures the box is always Dark Gray (or Green/Yellow), not transparent Black
            pygame.draw.rect(SCREEN, color, rect)

            # 2. Then, draw the BORDER on top
            # We always draw this, regardless of the fill color
            pygame.draw.rect(SCREEN, border_color, rect, 1)

            if letter != "":
                text_surface = FONT_GUESS.render(letter, True, COLOR_TEXT)
                text_rect = text_surface.get_rect(center=rect.center)
                SCREEN.blit(text_surface, text_rect)

def draw_alphabet(alphabet_colors):
    box_size = 50
    margin = 5
    start_y = 493

    rows = [
        ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
        ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L'],
        ['Z', 'X', 'C', 'V', 'B', 'N', 'M']
    ]

    for i, row_keys in enumerate(rows):
        row_width = len(row_keys) * (box_size + margin) - margin
        start_x = (WIDTH + ( 5*88 + 4 *25 + 60) - row_width) // 2

        y = start_y + i * (box_size + margin)

        for j, char in enumerate(row_keys):
            x = start_x + j * (box_size + margin)

            color = alphabet_colors.get(char, COLOR_PANEL_BG)

            rect = pygame.Rect(x, y, box_size, box_size)
            pygame.draw.rect(SCREEN, color, rect)

            text_surface = FONT_ALPHABETICAL.render(char, True, COLOR_TEXT)
            text_rect = text_surface.get_rect(center=rect.center)
            SCREEN.blit(text_surface, text_rect)

def draw_stat_item(screen, font_val, font_label, label, value, x, y, width):
    # Draw Value (Number)
    val_surf = font_val.render(str(value), True, COLOR_TEXT)
    val_rect = val_surf.get_rect(center=(x + width // 2, y))
    screen.blit(val_surf, val_rect)

    # Draw Label (Text)
    lbl_surf = font_label.render(label, True, COLOR_CORRECT)
    lbl_rect = lbl_surf.get_rect(center=(x + width // 2, y + 35))
    screen.blit(lbl_surf, lbl_rect)


def draw_stats_panel(screen, x, y, width, height):

    rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(screen, COLOR_PANEL_BG, rect, border_radius=10)
    pygame.draw.rect(screen, COLOR_CORRECT, rect, 2, border_radius=10)

    stats = JsonStats.load_stats()

    win_pct = 0
    if stats["played"] > 0:
        win_pct = int((stats["wins"] / stats["played"]) * 100)

    font_title = pygame.font.SysFont("Arial", FONT_SIZE_TITLE, bold=True)
    font_val = pygame.font.SysFont("Arial", 40, bold=True)
    font_lbl = pygame.font.SysFont("Arial", 16)

    title_surf = font_title.render("STATISTICS", True, COLOR_TEXT)
    title_rect = title_surf.get_rect(center=(x + width // 2, y + 40))
    screen.blit(title_surf, title_rect)

    center_x = x + width // 2
    row1_y = y + 100
    row2_y = y + 200
    spacing = 60

    draw_stat_item(screen, font_val, font_lbl, "Played"    , stats["played"]     , center_x - spacing - 40, row1_y, 80)
    draw_stat_item(screen, font_val, font_lbl, "Win %"     , f"{win_pct}"  , center_x + spacing - 40, row1_y, 80)
    draw_stat_item(screen, font_val, font_lbl, "Streak"    , stats["curr_streak"], center_x - spacing - 40, row2_y, 80)
    draw_stat_item(screen, font_val, font_lbl, "Max Streak", stats["max_streak"] , center_x + spacing - 40, row2_y, 80)

def draw_end_message(won, secret_word):
    overlay_width, overlay_height = 400, 250
    overlay_x = (WIDTH - overlay_width) // 2
    overlay_y = HEIGHT // 2 - 100

    rect = pygame.Rect(overlay_x, overlay_y, overlay_width, overlay_height)
    pygame.draw.rect(SCREEN, COLOR_BG, rect)
    if won:
        pygame.draw.rect(SCREEN, COLOR_CORRECT, rect, 3)
    else:
        pygame.draw.rect(SCREEN, COLOR_RED, rect, 3)

    msg = "VICTORY!" if won else "GAME OVER"
    color = COLOR_CORRECT if won else COLOR_RED

    text_surf = FONT_RESULT.render(msg, True, color)
    text_rect = text_surf.get_rect(center=(WIDTH // 2, overlay_y + 50))
    SCREEN.blit(text_surf, text_rect)

    if not won:
        word_msg = f"Word was: {secret_word}"
        word_surf = FONT_SMALL.render(word_msg, True, COLOR_TEXT)
        word_rect = word_surf.get_rect(center=(WIDTH // 2, overlay_y + 90))
        SCREEN.blit(word_surf, word_rect)


def run_game():
    #use "../Files/valid-wordle-words.txt"
    #if you want to test only this file
    # use "Files/valid-wordle-words.txt"
    # if you want to use the program
    valid_words = load_valid_words("Files/valid-wordle-words.txt")
    guesses = []
    current_guess_string = ""
    alphabet_colors = {}
    #For testing if needed
    #secret_word = "APPLE"
    secret_word = random.choice(valid_words).upper()

    running = True
    game_over = False
    won = False
    error_timer = 0

    btn_y = (HEIGHT // 2) + 50
    center_x = WIDTH // 2

    restart_btn = Button(center_x - 130, btn_y, 120, 50, "Restart", COLOR_PANEL_BG)
    home_btn = Button(center_x + 10, btn_y, 120, 50, "Home", COLOR_PANEL_BG)

    while running:
        if error_timer > 0:
            error_timer -= 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT"

            if event.type == pygame.MOUSEBUTTONDOWN:
                if game_over:
                    if restart_btn.is_clicked(event.pos):
                        return "RESTART"
                    if home_btn.is_clicked(event.pos):
                        return "HOME"

            if event.type == pygame.KEYDOWN:
                if not game_over:
                    if event.key == pygame.K_BACKSPACE:
                        current_guess_string = current_guess_string[:-1]
                        error_timer = 0

                    elif event.key == pygame.K_RETURN:
                        if len(current_guess_string) == 5:
                            if len(valid_words) > 0 and current_guess_string not in valid_words:
                                error_timer = 20
                            else:
                                result = colour_set(current_guess_string, secret_word, 5)
                                guesses.append(result)

                                for triplet in result:
                                    letter, _, status = triplet
                                    curr_col = alphabet_colors.get(letter)
                                    if status == "g":
                                        alphabet_colors[letter] = COLOR_CORRECT
                                    elif status == "y" and curr_col != COLOR_CORRECT:
                                        alphabet_colors[letter] = COLOR_PRESENT
                                    elif status == "x" and curr_col not in [COLOR_CORRECT, COLOR_PRESENT]:
                                        alphabet_colors[letter] = COLOR_ABSENT

                                current_guess_string = ""

                                if all(t[2] == 'g' for t in result):
                                    game_over = True
                                    won = True
                                    JsonStats.update_stats(is_win=True)

                                elif len(guesses) == 6:
                                    game_over = True
                                    won = False
                                    JsonStats.update_stats(is_win=False)

                    elif len(current_guess_string) < 5 and event.unicode.isalpha():
                        current_guess_string += event.unicode.upper()

        SCREEN.fill(COLOR_BG)

        draw_grid(guesses, current_guess_string, error_timer)
        draw_alphabet(alphabet_colors)

        STATS_X = (WIDTH + (5 * 88 + 4 * 25 + 60) - 55 * 5 - 5) // 2
        draw_stats_panel(SCREEN, STATS_X, 100, 300, 300)

        if game_over:
            draw_end_message(won, secret_word)
            # Draw buttons on top of the end message
            restart_btn.draw(SCREEN)
            home_btn.draw(SCREEN)

        pygame.display.flip()


if __name__ == "__main__":
    while True:
        result = run_game()
        if result == "HOME":
            break
        if result == "QUIT":
            break
    pygame.quit()