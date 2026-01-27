import pygame
import JsonStats
from GameLogic import colour_set, load_valid_words

pygame.init()

WIDTH, HEIGHT = 1200, 800
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("wordle")

# setting the colours
WHITE = (255, 255, 255)
BLACK = (19, 19, 20)
DARK_GRAY = (62, 62, 66)
GRAY = (128, 128, 128)
GREEN = (39, 158, 28)
YELLOW = (176, 184, 37)
GRAY_BORDER = (62, 62, 66)
GREEN_BORDER = (19,74,14) #1c6e14
YELLOW_BORDER = (83, 87, 17) #8c1d92
RED = (200, 50, 50)
OUTLINE = (200, 200, 200)

TITLE_FONT_SIZE = 30
STAT_VAL_FONT_SIZE = 40
STAT_LABEL_FONT_SIZE = 16

#setting the font
FONT_GUESS = pygame.font.SysFont("Arial", 56)
FONT_ALPHABETICAL = pygame.font.SysFont("Arial", 24)
FONT_RESULT = pygame.font.SysFont("Arial", 40, bold=True)
FONT_SMALL = pygame.font.SysFont("Arial", 20)

SECRET_WORD = "APPLE"

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

            color = DARK_GRAY
            letter = ""
            border_color = OUTLINE

            if row < len(guesses):
                triplet = guesses[row][col]
                letter = triplet[0]
                color_code = triplet[2]

                if color_code   == "g":
                    color = GREEN
                    border_color = GREEN_BORDER
                elif color_code == "y":
                    color = YELLOW
                    border_color = YELLOW_BORDER
                else:
                    color = GRAY
                    border_color = GRAY_BORDER

            elif row == len(guesses):
                if col < len(current_guess_string):
                    letter = current_guess_string[col]
                    border_color = GRAY

                if error_timer > 0:
                    border_color = RED
                    shake_offset = 5 if (error_timer // 2) % 2 == 0 else -5
                    x += shake_offset
                else:
                    border_color = WHITE if letter != "" else OUTLINE

            rect = pygame.Rect(x, y, box_size, box_size)

            # 1. First, draw the FILL (The background of the box)
            # This ensures the box is always Dark Gray (or Green/Yellow), not transparent Black
            pygame.draw.rect(SCREEN, color, rect)

            # 2. Then, draw the BORDER on top
            # We always draw this, regardless of the fill color
            pygame.draw.rect(SCREEN, border_color, rect, 1)

            if letter != "":
                text_surface = FONT_GUESS.render(letter, True, WHITE)
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

            color = alphabet_colors.get(char, DARK_GRAY)

            rect = pygame.Rect(x, y, box_size, box_size)
            pygame.draw.rect(SCREEN, color, rect)

            text_surface = FONT_ALPHABETICAL.render(char, True, WHITE)
            text_rect = text_surface.get_rect(center=rect.center)
            SCREEN.blit(text_surface, text_rect)

def draw_stat_item(screen, font_val, font_label, label, value, x, y, width):
    # Draw Value (Number)
    val_surf = font_val.render(str(value), True, WHITE)
    val_rect = val_surf.get_rect(center=(x + width // 2, y))
    screen.blit(val_surf, val_rect)

    # Draw Label (Text)
    lbl_surf = font_label.render(label, True, GREEN)
    lbl_rect = lbl_surf.get_rect(center=(x + width // 2, y + 35))
    screen.blit(lbl_surf, lbl_rect)


def draw_stats_panel(screen, x, y, width, height):

    rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(screen, DARK_GRAY, rect, border_radius=10)
    pygame.draw.rect(screen, GREEN, rect, 2, border_radius=10)

    stats = JsonStats.load_stats()

    win_pct = 0
    if stats["played"] > 0:
        win_pct = int((stats["wins"] / stats["played"]) * 100)

    font_title = pygame.font.SysFont("Arial", TITLE_FONT_SIZE, bold=True)
    font_val = pygame.font.SysFont("Arial", STAT_VAL_FONT_SIZE, bold=True)
    font_lbl = pygame.font.SysFont("Arial", STAT_LABEL_FONT_SIZE)

    title_surf = font_title.render("STATISTICS", True, WHITE)
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
    overlay_width, overlay_height = 400, 200
    overlay_x = (WIDTH - overlay_width) // 2
    overlay_y = HEIGHT // 2 - 100

    rect = pygame.Rect(overlay_x, overlay_y, overlay_width, overlay_height)
    pygame.draw.rect(SCREEN, BLACK, rect)
    if won:
        pygame.draw.rect(SCREEN, GREEN, rect, 3)
    else:
        pygame.draw.rect(SCREEN, RED, rect, 3)

    msg = "VICTORY!" if won else "GAME OVER"
    color = GREEN if won else RED
    text_surf = FONT_RESULT.render(msg, True, color)
    text_rect = text_surf.get_rect(center=(WIDTH // 2, overlay_y + 50))
    SCREEN.blit(text_surf, text_rect)

    if not won:
        word_msg = f"Word was: {secret_word}"
        word_surf = FONT_SMALL.render(word_msg, True, WHITE)
        word_rect = word_surf.get_rect(center=(WIDTH // 2, overlay_y + 90))
        SCREEN.blit(word_surf, word_rect)

    restart_msg = "Press 'R' to Play Again"
    restart_surf = FONT_SMALL.render(restart_msg, True, GRAY)
    restart_rect = restart_surf.get_rect(center=(WIDTH // 2, overlay_y + 140))
    SCREEN.blit(restart_surf, restart_rect)

    restart_msg = "Press 'H' to go to Home screen"
    restart_surf = FONT_SMALL.render(restart_msg, True, GRAY)
    restart_rect = restart_surf.get_rect(center=(WIDTH // 2, overlay_y + 170))
    SCREEN.blit(restart_surf, restart_rect)


def run_game():
    VALID_WORDS = load_valid_words("Files/valid-wordle-words.txt")
    guesses = []
    current_guess_string = ""
    alphabet_colors = {}

    running = True
    game_over = False
    won = False
    error_timer = 0

    while running:
        if error_timer > 0:
            error_timer -= 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT"

            if event.type == pygame.KEYDOWN:
                if game_over:
                    if event.key == pygame.K_r:
                        return "RESTART"
                    elif event.key == pygame.K_h:
                        return "HOME"

                else:
                    if event.key == pygame.K_BACKSPACE:
                        current_guess_string = current_guess_string[:-1]
                        error_timer = 0

                    elif event.key == pygame.K_RETURN:
                        if len(current_guess_string) == 5:
                            if len(VALID_WORDS) > 0 and current_guess_string not in VALID_WORDS:
                                error_timer = 20
                            else:
                                result = colour_set(current_guess_string, SECRET_WORD, 5)
                                guesses.append(result)

                                for triplet in result:
                                    letter, _, status = triplet
                                    curr_col = alphabet_colors.get(letter)
                                    if status == "g":
                                        alphabet_colors[letter] = GREEN
                                    elif status == "y" and curr_col != GREEN:
                                        alphabet_colors[letter] = YELLOW
                                    elif status == "x" and curr_col not in [GREEN, YELLOW]:
                                        alphabet_colors[letter] = GRAY

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

        SCREEN.fill(BLACK)

        draw_grid(guesses, current_guess_string,error_timer)
        draw_alphabet(alphabet_colors)

        STATS_X = (WIDTH + (5 * 88 + 4 * 25 + 60) - 55 * 5 - 5) // 2
        draw_stats_panel(SCREEN, STATS_X, 100, 300, 300)

        if game_over:
            draw_end_message(won, SECRET_WORD)

        pygame.display.flip()

if __name__ == "__main__":
    # This block ONLY runs if you run "PlayerMode.py" directly.
    # It will NOT run if you import it into MainMenu.
    while True:
        result = run_game()
        if result == "HOME":
            break
    pygame.quit()
