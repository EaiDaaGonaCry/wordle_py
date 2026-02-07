"""
PvE Mode (Player vs Entity).
The player competes against a Bot (Edit Distance or Gemini AI) to find the word first.
"""
import os
import random
from typing import Optional, List, Any, Dict
from unittest.mock import MagicMock

import pygame
from google import genai

from settings import JsonStats
from settings.Logic import colour_set, load_valid_words, filter_words, levenshtein_distance, Button
from settings.Constants import (
    COLOR_ACCENT, COLOR_CORRECT, COLOR_PRESENT, COLOR_ABSENT,
    COLOR_ABSENT_BORDER, COLOR_TEXT, COLOR_PANEL_BG, COLOR_BG,
    COLOR_RED, WIDTH, HEIGHT
)


def get_api_key() -> Optional[str]:
    """Reads the Gemini API key from file."""
    try:
        path = os.path.join("Files", "key")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return f.read().strip()
    except OSError:
        pass
    return None


GEMINI_KEY = get_api_key()
CLIENT = None

if GEMINI_KEY:
    try:
        CLIENT = genai.Client(api_key=GEMINI_KEY)
    except Exception as e:
        print(f"Failed to init Gemini: {e}")
else:
    print("Warning: No API Key found in Files/key")


def get_edit_distance_guess(possible_words: List[str], previous_guess: str, all_words: List[str]) -> str:
    """Bot strategy: Pick word with lowest Levenshtein distance to previous guess."""
    if not possible_words:
        return random.choice(all_words)
    if not previous_guess:
        return random.choice(possible_words)

    distances = []
    for word in possible_words:
        dist = levenshtein_distance(word, previous_guess)
        distances.append((dist, word))

    min_dist = min(d for d, w in distances)
    best_candidates = [w for d, w in distances if d == min_dist]
    return random.choice(best_candidates)


def get_gemini_guess(guesses_history: List[List[Any]], word_length: int) -> Optional[str]:
    """Bot strategy: Ask Google Gemini LLM for the next guess."""
    if CLIENT is None:
        return None

    # 2. Format the History string
    history_str = ""
    for pattern_tuples in guesses_history:
        # Reconstruct word and pattern from triplets
        word = "".join([t[0] for t in pattern_tuples])
        pat_str = "".join([t[2] for t in pattern_tuples])
        history_str += f"{word} ({pat_str}), "

    prompt = (
        f"You are a Wordle expert. The secret word has {word_length} letters. "
        f"Feedback: g=correct, y=present, x=absent. "
        f"History: {history_str}. "
        f"Suggest only ONE {word_length}-letter word as your next guess. "
        f"Write ONLY the word in capital letters."
    )

    try:
        response = CLIENT.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )

        if response and response.text:
            bot_reply = response.text.strip().upper()
            # Clean up the response (remove spaces/punctuation)
            clean_word = "".join(filter(str.isalpha, bot_reply))[:word_length]
            return clean_word
        return None
    except Exception as e:
        print(f"Gemini Error: {e}")
        return None

def draw_mini_grid(screen: pygame.Surface, start_x: int, start_y: int, width: int,
                   guesses: List[List[Any]], current_guess: str, word_length: int,
                   max_attempts: int, label: str, error_timer: int = 0) -> None:
    """Draws a smaller version of the game grid for split-screen."""
    font_label = pygame.font.SysFont("Arial", 25, bold=True)

    # Draw Label
    lbl_surf = font_label.render(label, True, COLOR_ACCENT)
    lbl_x = start_x + (width // 2) - (lbl_surf.get_width() // 2)
    screen.blit(lbl_surf, (lbl_x, start_y - 35))

    margin = 5
    box_size = (width - ((word_length - 1) * margin)) // word_length
    box_size = min(60, box_size)
    actual_grid_width = (word_length * box_size) + ((word_length - 1) * margin)
    offset_x = (width - actual_grid_width) // 2

    for row in range(max_attempts):
        for col in range(word_length):
            x_pos = start_x + offset_x + col * (box_size + margin)
            y_pos = start_y + row * (box_size + margin)
            color, border_color, letter = COLOR_ABSENT, COLOR_ABSENT_BORDER, ""

            # Past Guesses
            if row < len(guesses):
                triplet = guesses[row][col]
                letter, color_code = triplet[0], triplet[2]
                if color_code == "g":
                    color = COLOR_CORRECT
                elif color_code == "y":
                    color = COLOR_PRESENT

            # Current Active Row (Player Typing)
            elif row == len(guesses) and "PLAYER" in label:
                border_color = (150, 150, 150)
                if col < len(current_guess):
                    letter = current_guess[col]

                if error_timer > 0:
                    border_color = COLOR_RED
                    shake = 5 if (error_timer // 2) % 2 == 0 else -5
                    x_pos += shake

            rect = pygame.Rect(x_pos, y_pos, box_size, box_size)
            pygame.draw.rect(screen, color, rect, border_radius=4)
            pygame.draw.rect(screen, border_color, rect, 2, border_radius=4)

            if letter:
                font = pygame.font.SysFont("Arial", int(box_size * 0.65), bold=True)
                text = font.render(letter, True, COLOR_TEXT)
                screen.blit(text, text.get_rect(center=rect.center))


def select_bot_type_menu() -> str:
    """Displays a sub-menu to choose the opponent type."""
    screen = pygame.display.get_surface()
    font_guess = pygame.font.SysFont("Arial", 40, bold=True)
    font_small = pygame.font.SysFont("Arial", 20)

    center_x, center_y = WIDTH // 2, HEIGHT // 2
    btn_edit = Button(center_x - 300, center_y, 280, 80, "VS EDIT-DISTANCE", COLOR_PANEL_BG, "EDIT")
    btn_llm = Button(center_x + 20, center_y, 280, 80, "VS GEMINI AI", (46, 134, 193), "LLM")

    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT"
            if event.type == pygame.MOUSEBUTTONDOWN:
                if btn_edit.is_clicked(mouse_pos):
                    return "EDIT"
                if btn_llm.is_clicked(mouse_pos):
                    return "LLM"

        screen.fill(COLOR_BG)
        title = font_guess.render("CHOOSE OPPONENT", True, COLOR_TEXT)
        screen.blit(title, (center_x - title.get_width() // 2, center_y - 100))
        btn_edit.draw(screen)
        btn_llm.draw(screen)

        if CLIENT is None:
            warn = font_small.render("(Gemini Key missing in Files/key)", True, COLOR_RED)
            screen.blit(warn, (center_x + 60, center_y + 90))
        pygame.display.flip()
    return "QUIT"


def run_pve(settings: Dict[str, Any]) -> str:
    """Main loop for PvE Mode."""
    pygame.init()

    # Fonts
    font_label = pygame.font.SysFont("Arial", 25, bold=True)
    font_result = pygame.font.SysFont("Arial", 40, bold=True)

    bot_type = select_bot_type_menu()
    if bot_type == "QUIT":
        return "HOME"

    word_length = int(settings["word_length"])
    max_attempts = int(settings["max_attempts"])
    player_name = str(settings["player_name"])

    valid_words = load_valid_words("Files/valid-wordle-words.txt", word_length)
    if not valid_words:
        return "HOME"

    player_score, bot_score, rounds_played = 0, 0, 0
    session_running = True

    while session_running:
        rounds_played += 1
        secret_word = random.choice(valid_words).upper()

        # Player State
        p_guesses, p_current_str = [], ""
        p_won, p_lost = False, False

        # Bot State
        b_guesses, b_last_guess = [], ""
        b_possible = list(valid_words)
        b_won, b_lost = False, False

        round_over, status_msg = False, ""
        error_timer = 0

        # Layout
        p_grid_x, p_grid_w = 100, 400
        b_grid_x, b_grid_w = WIDTH - 500, 400
        grid_start_y = 120

        btn_next = Button(WIDTH // 2 - 100, HEIGHT - 140, 200, 60, "NEXT ROUND", COLOR_CORRECT)
        btn_exit = Button(WIDTH // 2 - 100, HEIGHT - 70, 200, 60, "EXIT", COLOR_PANEL_BG)

        def play_bot_turn() -> None:
            nonlocal b_last_guess, b_won, b_lost, bot_score, b_possible
            if b_won or b_lost:
                return

            if bot_type == "EDIT":
                bot_word = get_edit_distance_guess(b_possible, b_last_guess, valid_words)
            else:
                gemini_word = get_gemini_guess(b_guesses, word_length)
                bot_word = gemini_word if gemini_word else random.choice(b_possible)

            if bot_word:
                b_last_guess = bot_word
                b_res = colour_set(bot_word, secret_word, word_length)
                b_guesses.append(b_res)

                # Filter bot's logic
                pat_str = "".join([t[2] for t in b_res])
                b_possible = filter_words(pat_str, bot_word, b_possible)

                if bot_word == secret_word:
                    b_won = True
                    bot_score += (word_length * 10) + (max_attempts - len(b_guesses)) * 20
                elif len(b_guesses) >= max_attempts:
                    b_lost = True

        while True:
            if error_timer > 0:
                error_timer -= 1

            # Bot plays if player is done but bot isn't
            if (p_won or p_lost) and not (b_won or b_lost):
                pygame.time.delay(700)
                play_bot_turn()

            # End Round Condition
            if (p_won or p_lost) and (b_won or b_lost):
                round_over = True
                status_msg = "YOU LOST!" if p_lost else "ROUND COMPLETE"
                if p_lost:
                    btn_next.text = "FINISH"

            # Events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    if player_score > 0:
                        JsonStats.save_score(player_name, player_score)
                    return "QUIT"

                if event.type == pygame.MOUSEBUTTONDOWN and round_over:
                    if btn_next.is_clicked(event.pos):
                        if p_lost:
                            if player_score > 0:
                                JsonStats.save_score(player_name, player_score)
                            return "HOME"
                        break
                    if btn_exit.is_clicked(event.pos):
                        if player_score > 0:
                            JsonStats.save_score(player_name, player_score)
                        return "HOME"

                if event.type == pygame.KEYDOWN and not round_over:
                    if not p_won and not p_lost:
                        if event.key == pygame.K_BACKSPACE:
                            p_current_str = p_current_str[:-1]

                        elif event.key == pygame.K_RETURN:
                            if len(p_current_str) == word_length:
                                if p_current_str not in valid_words:
                                    error_timer = 20
                                else:
                                    res = colour_set(p_current_str, secret_word, word_length)
                                    p_guesses.append(res)
                                    if p_current_str == secret_word:
                                        p_won = True
                                        player_score += (word_length * 10) + (max_attempts - len(p_guesses)) * 20
                                    elif len(p_guesses) >= max_attempts:
                                        p_lost = True
                                    p_current_str = ""

                                    # Bot plays after player
                                    play_bot_turn()

                        elif len(p_current_str) < word_length and event.unicode.isalpha():
                            p_current_str += event.unicode.upper()

            # Draw
            screen = pygame.display.get_surface()
            screen.fill(COLOR_BG)

            p_name = "YOU"
            b_name = "GEMINI AI" if bot_type == "LLM" else "EDIT BOT"

            p_score_surf = font_label.render(f"{p_name}: {player_score}", True, COLOR_CORRECT)
            p_score_x = p_grid_x + (p_grid_w // 2) - (p_score_surf.get_width() // 2)
            screen.blit(p_score_surf, (p_score_x, 40))

            b_score_surf = font_label.render(f"{b_name}: {bot_score}", True, (230, 126, 34))
            b_score_x = b_grid_x + (b_grid_w // 2) - (b_score_surf.get_width() // 2)
            screen.blit(b_score_surf, (b_score_x, 40))

            draw_mini_grid(screen, p_grid_x, grid_start_y, p_grid_w, p_guesses,
                           p_current_str, word_length, max_attempts, "PLAYER", error_timer)
            draw_mini_grid(screen, b_grid_x, grid_start_y, b_grid_w, b_guesses,
                           "", word_length, max_attempts, "BOT")

            if round_over:
                msg_surf = font_result.render(status_msg, True, COLOR_CORRECT if not p_lost else COLOR_RED)
                msg_rect = msg_surf.get_rect(center=(WIDTH // 2, HEIGHT - 240))

                bg_rect = msg_rect.inflate(40, 20)
                pygame.draw.rect(screen, COLOR_BG, bg_rect, border_radius=10)
                pygame.draw.rect(screen, COLOR_ABSENT, bg_rect, 2, border_radius=10)

                screen.blit(msg_surf, msg_rect)

                btn_next.draw(screen)
                btn_exit.draw(screen)

            pygame.display.flip()

            if round_over and pygame.mouse.get_pressed()[0]:
                mouse_pos = pygame.mouse.get_pos()
                if btn_next.is_clicked(mouse_pos):
                    if p_lost:
                        return "HOME"
                    break
                if btn_exit.is_clicked(mouse_pos):
                    return "HOME"

        if p_lost:
            session_running = False


    return "HOME"