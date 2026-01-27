
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