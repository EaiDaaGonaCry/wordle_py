import random
import pygame

#=================
# LOGIC FUNCTIONS
#=================

def colour_set(guess_word, secret_word, word_length):
    triplets = []
    secret_as_list = list(secret_word)
    guess_as_list = list(guess_word)

    for position in range(word_length):
        if guess_as_list[position] == secret_as_list[position]:
            triplets.append((guess_as_list[position], position, "g"))
            secret_as_list[position] = None
            guess_as_list[position] = None

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

def load_valid_words(file_path):
    valid_words = list()
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                # Store everything as UPPERCASE to match your game logic
                valid_words.append(line.strip().upper())
    except FileNotFoundError:
        print(f"Warning: {file_path} not found. Word validation disabled.")
    return valid_words

def get_pattern_from_triplets(triplets):
    return tuple(item[2] for item in triplets)

def triplets_maker(colour_pattern, word):
    triplets = []

    word_upper = word.upper()
    colour_pattern = colour_pattern.lower()

    for i in range(len(word_upper)):
        triplets.append((word_upper[i], i, colour_pattern[i]))

    return triplets

def filter_words(colour_pattern, guess_word, word_list):
    new_word_list = []
    triplets = triplets_maker(colour_pattern, guess_word)

    confirmed_present_letters = set()
    for letter, index, colour in triplets:
        if colour in ('g', 'y'):
            confirmed_present_letters.add(letter)

    for word in word_list:
        is_valid = True
        word_as_list = list(word)

        for letter ,index ,colour in triplets:
            if colour == 'g' and word_as_list[index] != letter:
                is_valid = False
                break

            elif colour == 'y':
                if word_as_list[index] == letter:
                    is_valid = False
                    break
                if letter not in word_as_list:
                    is_valid = False
                    break

            elif colour == 'x':
                if word_as_list[index] == letter:
                    is_valid = False
                    break
                if letter not in confirmed_present_letters and letter in word:
                    is_valid = False
                    break

        if is_valid:
            new_word_list.append(word)

    return new_word_list


def get_best_word(possible_words):
    if len(possible_words) > 6000:
        return random.choice(possible_words)

    best_word = possible_words[0]
    max_score = -1
    total = len(possible_words)

    for guess_candidate in possible_words:
        pattern_counts = {}

        for secret_candidate in possible_words:
            triplets = colour_set(guess_candidate, secret_candidate, 5)
            pattern = get_pattern_from_triplets(triplets)

            if pattern in pattern_counts:
                pattern_counts[pattern] += 1
            else:
                pattern_counts[pattern] = 1

        score = 0
        for count in pattern_counts.values():
            score += count * (total - count)

        if score > max_score:
            max_score = score
            best_word = guess_candidate

    return best_word

def colour_value_helper(triplets):
    sum = 0;

    for i in triplets:
        colour = i[2]
        if colour == 'g':
            sum += 3
        if colour == 'y':
            sum += 1

    return sum

def get_best_lie(guess_word,word_pool, length):
    candidates = []

    for potential_word in word_pool:
        temp_triplets = colour_set(guess_word, potential_word, length)
        score = colour_value_helper(temp_triplets)

        if 3 <= score <= 7:
            candidates.append(potential_word)

    if len(candidates) > 0:
        lie_word = random.choice(candidates)
    else:
        lie_word = random.choice(word_pool)

    return colour_set(guess_word, lie_word, length)

#=================
#       UI
#=================

class Button:
    def __init__(self, x, y, width, height, text, color, text_color=(255, 255, 255)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.text_color = text_color
        # You can use a specific font here if you want consistency
        self.font = pygame.font.Font(None, 30)

    def draw(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        draw_color = self.color

        # Hover effect
        if self.rect.collidepoint(mouse_pos):
            draw_color = tuple(min(c + 30, 255) for c in self.color)

        pygame.draw.rect(screen, draw_color, self.rect, border_radius=5)
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

