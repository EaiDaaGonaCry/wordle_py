"""
Contains the core logic for the Wordle game, including word validation,
coloring algorithms, and bot heuristics.
"""
import random
from functools import lru_cache
from typing import List, Tuple, Dict, Optional, Any, Set
import pygame

from settings.Constants import COLOR_CORRECT


class Button:
    """A simple UI Button class for Pygame."""

    def __init__(self, x: int, y: int, width: int, height: int, text: str,
                 color: Tuple[int, int, int], action_id: Optional[Any] = None,
                 text_color: Tuple[int, int, int] = (255, 255, 255),
                 border_color: Optional[Tuple[int, int, int]] = None,
                 font: Optional[pygame.font.Font] = None,
                 hover_color: Optional[Tuple[int, int, int]] = None) -> None:
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.text_color = text_color
        self.action_id = action_id
        self.border_color = border_color
        self.hover_color = hover_color
        self.is_selected = False
        self.font = font if font else pygame.font.SysFont("Arial", 30, bold=True)

    def draw(self, screen: pygame.Surface) -> None:
        """Draws the button on the screen."""
        mouse_pos = pygame.mouse.get_pos()
        draw_color = self.color

        if self.is_selected:
            draw_color = COLOR_CORRECT
        elif self.rect.collidepoint(mouse_pos):
            if self.hover_color:
                draw_color = self.hover_color
            else:
                draw_color = tuple(min(c + 30, 255) for c in self.color) # type: ignore

        pygame.draw.rect(screen, draw_color, self.rect, border_radius=8)

        if self.border_color:
            pygame.draw.rect(screen, self.border_color, self.rect, 3, border_radius=8)

        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def is_clicked(self, pos: Tuple[int, int]) -> bool:
        """Checks if the button was clicked."""
        return self.rect.collidepoint(pos)


def colour_set(guess_word: str, secret_word: str, word_length: int) -> List[Tuple[str, int, str]]:
    """Generates the pattern (green, yellow, gray) for a guess."""
    triplets: List[Tuple[str, int, str]] = []
    secret_as_list: List[Optional[str]] = list(secret_word) # type: ignore
    guess_as_list: List[Optional[str]] = list(guess_word)   # type: ignore

    # 1. Check for GREEN
    for position in range(word_length):
        if guess_as_list[position] == secret_as_list[position]:
            triplets.append((str(guess_as_list[position]), position, "g"))
            secret_as_list[position] = None
            guess_as_list[position] = None

    # 2. Check for YELLOW or GREY
    for position in range(word_length):
        letter = guess_as_list[position]
        if letter is not None:
            if letter in secret_as_list:
                triplets.append((letter, position, "y"))
                secret_as_list[secret_as_list.index(letter)] = None
            else:
                triplets.append((letter, position, "x"))

    triplets.sort(key=lambda x: x[1])
    return triplets


def load_valid_words(file_path: str, length: int = 5) -> List[str]:
    """Loads valid words of a specific length from a file."""
    valid_words: List[str] = []
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                clean_word = line.strip().upper()
                if len(clean_word) == length and clean_word.isalpha():
                    valid_words.append(clean_word)
    except FileNotFoundError:
        print(f"Warning: {file_path} not found.")
        return ["ERROR"]
    return valid_words


def get_pattern_from_triplets(triplets: List[Tuple[str, int, str]]) -> Tuple[str, ...]:
    """Extracts the pattern string from triplets."""
    return tuple(item[2] for item in triplets)


def triplets_maker(colour_pattern: str, word: str) -> List[Tuple[str, int, str]]:
    """Creates triplets from a pattern string and a word."""
    triplets: List[Tuple[str, int, str]] = []
    word_upper = word.upper()
    colour_pattern = colour_pattern.lower()
    for i, char in enumerate(word_upper):
        triplets.append((char, i, colour_pattern[i]))
    return triplets


def filter_words(colour_pattern: str, guess_word: str, word_list: List[str]) -> List[str]:
    """Filters the possible words based on the feedback pattern."""
    new_word_list: List[str] = []
    triplets = triplets_maker(colour_pattern, guess_word)

    confirmed_present: Set[str] = set()
    for letter, _, colour in triplets:
        if colour in ('g', 'y'):
            confirmed_present.add(letter)

    for word in word_list:
        is_valid = True
        word_as_list = list(word)

        for letter, index, colour in triplets:
            if colour == 'g':
                if word_as_list[index] != letter:
                    is_valid = False
                    break
            elif colour == 'y':
                if word_as_list[index] == letter or letter not in word_as_list:
                    is_valid = False
                    break
            elif colour == 'x':
                if word_as_list[index] == letter:
                    is_valid = False
                    break
                if letter not in confirmed_present and letter in word:
                    is_valid = False
                    break

        if is_valid:
            new_word_list.append(word)

    return new_word_list


def remove_useless_words(guess_word: str, secret_word: str, word_list: List[str]) -> List[str]:
    """Filters words assuming the secret word is known (helper)."""
    pattern = get_pattern_string(colour_set(guess_word, secret_word, len(guess_word)))
    return filter_words(pattern, guess_word, word_list)


def get_pattern_string(triplets: List[Tuple[str, int, str]]) -> str:
    """Converts triplets list to a pattern string (e.g., 'gyxgg')."""
    return "".join([t[2] for t in triplets])


def get_best_word(possible_words: List[str]) -> str:
    """Calculates the best next guess using information theory heuristics."""
    if len(possible_words) > 2000:
        return random.choice(possible_words)

    best_word = possible_words[0]
    max_score = -1.0
    candidates = possible_words if len(possible_words) < 500 else possible_words[:500]

    for guess_candidate in candidates:
        pattern_counts: Dict[Tuple[str, ...], int] = {}
        for secret_candidate in possible_words:
            # Assumes standard 5-letter logic for heuristics
            triplets = colour_set(guess_candidate, secret_candidate, 5)
            pattern = get_pattern_from_triplets(triplets)
            pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1

        score = 0.0
        total_words = len(possible_words)
        for count in pattern_counts.values():
            score += count * (total_words - count)

        if score > max_score:
            max_score = score
            best_word = guess_candidate
    return best_word


def colour_value_helper(triplets: List[Tuple[str, int, str]]) -> int:
    """Calculates a score for a pattern (used in Extreme mode)."""
    score = 0
    for item in triplets:
        colour = item[2]
        if colour == 'g':
            score += 3
        if colour == 'y':
            score += 1
    return score


def get_best_lie(guess_word: str, word_pool: List[str], length: int) -> List[Tuple[str, int, str]]:
    """Generates a misleading pattern for Extreme mode."""
    candidates = []
    for potential_word in word_pool:
        temp_triplets = colour_set(guess_word, potential_word, length)
        score = colour_value_helper(temp_triplets)
        if 3 <= score <= 7:
            candidates.append(potential_word)

    lie_word = random.choice(candidates) if candidates else random.choice(word_pool)
    return colour_set(guess_word, lie_word, length)


def lie_detector(colour_pattern: str, guess_word: str, word_list: Dict[str, int]) -> Dict[str, int]:
    """Filters words in Extreme mode allowing for lies."""
    new_word_dict = {}
    for word, error_count in word_list.items():
        maybe_triplets = colour_set(guess_word, word, 5)
        maybe_pattern_str = get_pattern_string(maybe_triplets)

        current_errors = error_count
        if maybe_pattern_str != colour_pattern:
            current_errors += 1

        if current_errors <= 1:
            new_word_dict[word] = current_errors
    return new_word_dict


def init_extreme_candidates(word_list: List[str]) -> Dict[str, int]:
    """Initializes the dictionary for Extreme mode."""
    return {word: 0 for word in word_list}


@lru_cache(maxsize=None)
def levenshtein_distance(s1: str, s2: str) -> int:
    """Calculates Levenshtein distance between two strings."""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row # type: ignore
    return previous_row[-1] # type: ignore