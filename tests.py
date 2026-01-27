from WORDLE.GameLogic import colour_set

# --- Running the code ---
triplets_list = colour_set("world", "wrong", 5)

for char, pos, colour in triplets_list:
    # Using pos (position) instead of length, which is a clearer name
    print(f"Letter: {char} | Position: {pos} | Colour: {colour}")