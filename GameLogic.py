
def colour_set(guess_word, secret_word, word_length):
    triplets = []
    secret_as_list = list(secret_word)
    guess_as_list = list(guess_word)

    # setting the green letters
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
    valid_words = set()
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                # Store everything as UPPERCASE to match your game logic
                valid_words.add(line.strip().upper())
    except FileNotFoundError:
        print(f"Warning: {file_path} not found. Word validation disabled.")
    return valid_words