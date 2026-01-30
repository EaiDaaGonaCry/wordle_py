from Settings import Logic

# --- Running the code ---
# triplets_list = colour_set("world", "wrong", 5)
#
# for char, pos, colour in triplets_list:
#     # Using pos (position) instead of length, which is a clearer name
#     print(f"Letter: {char} | Position: {pos} | Colour: {colour}")

# triplets_list = colour_set("eerie", "speed", 5)
#
# for char, pos, colour in triplets_list:
#     # Using pos (position) instead of length, which is a clearer name
#     print(f"Letter: {char} | Position: {pos} | Colour: {colour}")

# triplets_test2 = triplets_maker("ggxyx", "speed")
#
# for char, pos, colour in triplets_test2:
#     # Using pos (position) instead of length, which is a clearer name
#     print(f"Letter: {char} | Position: {pos} | Colour: {colour}")


dict = Logic.load_valid_words("Files/valid-wordle-words.txt")
print(len(dict))

print(len(Logic.filter_words("xxxgg", "power", dict)))
# for word in Logic.filter_words("gxxxx", "apple", dict):
#     print(word)

print(Logic.get_best_word(Logic.filter_words("ggxxx", "apple", dict)))