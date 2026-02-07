"""
Single Player Mode.
"""
import random
from typing import Dict, List, Any, Tuple
import pygame

from settings import JsonStats
from settings.Logic import colour_set, load_valid_words, get_best_lie, Button
from settings.Constants import (
    WIDTH, HEIGHT, FONT_NAME, FONT_SIZE_GUESS, COLOR_PANEL_BG,
    COLOR_BORDER, COLOR_ABSENT, COLOR_TEXT, COLOR_ABSENT_BORDER,
    COLOR_CORRECT, COLOR_CORRECT_BORDER, COLOR_PRESENT,
    COLOR_PRESENT_BORDER, COLOR_RED, COLOR_ACCENT, COLOR_BG
)

pygame.init()


def calculate_score(word_length: int, max_attempts: int, attempts_taken: int, difficulty: str) -> int:
    """Calculates the score based on attempts and difficulty."""
    unused_attempts = max_attempts - attempts_taken
    base_score = word_length * 50
    bonus_score = unused_attempts * 100

    total_score = base_score + bonus_score

    if difficulty == "EXTREME":
        total_score *= 2

    return total_score


def draw_alphabet(screen: pygame.Surface, alphabet_colors: Dict[str, Tuple[int, int, int]]) -> None:
    """Draws the on-screen keyboard."""
    font = pygame.font.SysFont(FONT_NAME, 24, bold=True)
    key_size = 40
    margin = 5
    start_y = HEIGHT - 200

    rows = [
        ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
        ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L'],
        ['Z', 'X', 'C', 'V', 'B', 'N', 'M']
    ]

    for i, row_keys in enumerate(rows):
        row_width = len(row_keys) * (key_size + margin) - margin
        start_x = (WIDTH - row_width) // 2
        y_pos = start_y + i * (key_size + margin)

        for j, char in enumerate(row_keys):
            x_pos = start_x + j * (key_size + margin)
            color = alphabet_colors.get(char, COLOR_PANEL_BG)
            border_c = COLOR_BORDER
            if color == COLOR_ABSENT:
                border_c = COLOR_ABSENT

            rect = pygame.Rect(x_pos, y_pos, key_size, key_size)
            pygame.draw.rect(screen, color, rect, border_radius=4)
            if color == COLOR_PANEL_BG:
                pygame.draw.rect(screen, border_c, rect, 1, border_radius=4)

            text_surface = font.render(char, True, COLOR_TEXT)
            text_rect = text_surface.get_rect(center=rect.center)
            screen.blit(text_surface, text_rect)


def draw_grid(screen: pygame.Surface, guesses: List[List[Tuple[str, int, str]]],
              current_guess_string: str, error_timer: int,
              word_length: int, max_attempts: int) -> None:
    """Draws the main game grid."""
    max_grid_w = 800
    max_grid_h = 450
    margin = 5

    box_w = (max_grid_w - ((word_length - 1) * margin)) // word_length
    box_h = (max_grid_h - ((max_attempts - 1) * margin)) // max_attempts
    box_size = min(box_w, box_h, 80)

    total_w = word_length * box_size + (word_length - 1) * margin
    start_x = (WIDTH - total_w) // 2
    start_y = 100

    for row in range(max_attempts):
        for col in range(word_length):
            x_pos = start_x + col * (box_size + margin)
            y_pos = start_y + row * (box_size + margin)

            color = COLOR_PANEL_BG
            letter = ""
            border_color = COLOR_ABSENT_BORDER
            text_color = COLOR_TEXT

            # Filled Row
            if row < len(guesses):
                triplet = guesses[row][col]
                letter = triplet[0]
                color_code = triplet[2]

                if color_code == "g":
                    color = COLOR_CORRECT
                    border_color = COLOR_CORRECT_BORDER
                elif color_code == "y":
                    color = COLOR_PRESENT
                    border_color = COLOR_PRESENT_BORDER
                else:
                    color = COLOR_ABSENT
                    border_color = COLOR_ABSENT_BORDER

            # Active Row (Typing)
            elif row == len(guesses):
                if col < len(current_guess_string):
                    letter = current_guess_string[col]
                    border_color = (180, 180, 180)

                if error_timer > 0:
                    border_color = COLOR_RED
                    shake = 5 if (error_timer // 2) % 2 == 0 else -5
                    x_pos += shake

            rect = pygame.Rect(x_pos, y_pos, box_size, box_size)
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, border_color, rect, 2)

            if letter != "":
                dynamic_font = pygame.font.SysFont(FONT_NAME, int(box_size * 0.6), bold=True)
                text_surf = dynamic_font.render(letter, True, text_color)
                text_rect = text_surf.get_rect(center=rect.center)
                screen.blit(text_surf, text_rect)


def draw_hud(screen: pygame.Surface, score: int, name: str, current_round: int) -> None:
    """Draws player info and score."""
    font_score = pygame.font.SysFont(FONT_NAME, 30, bold=True)
    font_small = pygame.font.SysFont(FONT_NAME, 20)

    name_surf = font_score.render(f"Player: {name}", True, COLOR_ACCENT)
    screen.blit(name_surf, (20, 20))

    score_surf = font_score.render(f"Score: {score}", True, COLOR_CORRECT)
    score_rect = score_surf.get_rect(topright=(WIDTH - 20, 20))
    screen.blit(score_surf, score_rect)

    round_surf = font_small.render(f"Round: {current_round}", True, COLOR_TEXT)
    round_rect = round_surf.get_rect(topright=(WIDTH - 20, 55))
    screen.blit(round_surf, round_rect)


def draw_end_message(screen: pygame.Surface, won: bool, secret_word: str, round_score: int) -> None:
    """Draws the modal when a round ends."""
    font_result = pygame.font.SysFont(FONT_NAME, 40, bold=True)
    font_small = pygame.font.SysFont(FONT_NAME, 20)
    font_score = pygame.font.SysFont(FONT_NAME, 30, bold=True)

    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))

    panel_w, panel_h = 500, 480
    panel_rect = pygame.Rect((WIDTH - panel_w) // 2, (HEIGHT - panel_h) // 2, panel_w, panel_h)

    pygame.draw.rect(screen, COLOR_BG, panel_rect, border_radius=15)
    border_col = COLOR_CORRECT if won else COLOR_RED
    pygame.draw.rect(screen, border_col, panel_rect, 3, border_radius=15)

    msg = "CORRECT!" if won else "GAME OVER"
    msg_col = COLOR_CORRECT if won else COLOR_RED

    title_surf = font_result.render(msg, True, msg_col)
    title_rect = title_surf.get_rect(center=(WIDTH // 2, panel_rect.y + 50))
    screen.blit(title_surf, title_rect)

    word_text = f"The word was: {secret_word}"
    word_surf = font_small.render(word_text, True, COLOR_TEXT)
    word_rect = word_surf.get_rect(center=(WIDTH // 2, panel_rect.y + 120))
    screen.blit(word_surf, word_rect)

    if won:
        pts_surf = font_score.render(f"+ {round_score} Points", True, COLOR_ACCENT)
        pts_rect = pts_surf.get_rect(center=(WIDTH // 2, panel_rect.y + 180))
        screen.blit(pts_surf, pts_rect)


def run_game(settings: Dict[str, Any]) -> str:
    """Main Single Player Game Loop."""
    # settings Parsing
    if isinstance(settings, str):
        difficulty = settings
        word_length = 5
        max_attempts = 6
        player_name = "Player"
    else:
        difficulty = str(settings.get("difficulty", "NORMAL"))
        word_length = int(settings.get("word_length", 5))
        max_attempts = int(settings.get("max_attempts", 6))
        player_name = str(settings.get("player_name", "Player"))

    valid_words = load_valid_words("Files/valid-wordle-words.txt", word_length)

    if not valid_words or valid_words == ["ERROR"]:
        print("Error loading words! Check file path.")
        return "HOME"

    current_session_score = 0
    rounds_played = 0
    playing_session = True

    while playing_session:
        rounds_played += 1
        secret_word = random.choice(valid_words).upper()
        guesses: List[List[Tuple[str, int, str]]] = []
        current_guess_string = ""
        alphabet_colors: Dict[str, Tuple[int, int, int]] = {}

        error_timer = 0
        game_over = False
        won = False
        round_points = 0

        # UI Setup
        center_x = WIDTH // 2
        panel_h = 480
        panel_y_top = (HEIGHT - panel_h) // 2

        btn_action_y = panel_y_top + 260
        btn_home_y = btn_action_y + 80

        btn_action = Button(center_x - 110, btn_action_y, 220, 60, "NEXT WORD", COLOR_CORRECT)
        btn_home = Button(center_x - 110, btn_home_y, 220, 60, "EXIT TO MENU", COLOR_PANEL_BG)

        # Extreme Mode Lie Setup
        lie_index = -1
        if difficulty == "EXTREME":
            lie_index = random.randint(0, max_attempts - 2)

        running_round = True
        while running_round:
            if error_timer > 0:
                error_timer -= 1

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    if current_session_score > 0:
                        JsonStats.save_score(player_name, current_session_score)
                    return "QUIT"

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if game_over:
                        if btn_action.is_clicked(event.pos):
                            if won:
                                running_round = False
                            else:
                                if current_session_score > 0:
                                    JsonStats.save_score(player_name, current_session_score)
                                return "RESTART"

                        if btn_home.is_clicked(event.pos):
                            if current_session_score > 0:
                                JsonStats.save_score(player_name, current_session_score)
                            return "HOME"

                if event.type == pygame.KEYDOWN and not game_over:
                    if event.key == pygame.K_BACKSPACE:
                        current_guess_string = current_guess_string[:-1]

                    elif event.key == pygame.K_RETURN:
                        if len(current_guess_string) == word_length:
                            if current_guess_string not in valid_words:
                                error_timer = 20
                            else:
                                current_turn = len(guesses)
                                result: List[Tuple[str, int, str]] = []

                                if (difficulty == "EXTREME" and
                                        current_turn == lie_index and
                                        current_guess_string != secret_word):
                                    result = get_best_lie(current_guess_string, valid_words, word_length)
                                else:
                                    result = colour_set(current_guess_string, secret_word, word_length)

                                guesses.append(result)

                                # Update Keyboard Colors
                                for triplet in result:
                                    letter, _, status = triplet
                                    curr_col = alphabet_colors.get(letter)
                                    if status == "g":
                                        alphabet_colors[letter] = COLOR_CORRECT
                                    elif status == "y":
                                        if curr_col != COLOR_CORRECT:
                                            alphabet_colors[letter] = COLOR_PRESENT
                                    elif status == "x":
                                        if curr_col not in [COLOR_CORRECT, COLOR_PRESENT]:
                                            alphabet_colors[letter] = COLOR_ABSENT

                                current_guess_string = ""

                                # Check Win Condition
                                if all(t[2] == 'g' for t in result):
                                    won = True
                                    game_over = True
                                    round_points = calculate_score(word_length, max_attempts,
                                                                   len(guesses), difficulty)
                                    current_session_score += round_points
                                    btn_action.text = "NEXT WORD"
                                    btn_action.color = COLOR_CORRECT

                                elif len(guesses) >= max_attempts:
                                    won = False
                                    game_over = True
                                    btn_action.text = "TRY AGAIN"
                                    btn_action.color = COLOR_RED

                    elif len(current_guess_string) < word_length and event.unicode.isalpha():
                        current_guess_string += event.unicode.upper()

            # --- Drawing ---
            screen = pygame.display.get_surface()
            screen.fill(COLOR_BG)

            draw_hud(screen, current_session_score, player_name, rounds_played)
            draw_grid(screen, guesses, current_guess_string, error_timer, word_length, max_attempts)

            if not game_over:
                draw_alphabet(screen, alphabet_colors)

            if game_over:
                draw_end_message(screen, won, secret_word, round_points)
                btn_action.draw(screen)
                btn_home.draw(screen)

            pygame.display.flip()



    return "HOME"