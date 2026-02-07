"""
Global Constants for the Wordle Master Game.
Contains dimensions, colors, and font configurations.
"""

# --- SCREEN DIMENSIONS ---
WIDTH = 1200
HEIGHT = 800
FPS = 30

# --- COLORS ---
# Main Palette
COLOR_BG = (19, 19, 20)           # Main Background (Dark)
COLOR_PANEL_BG = (62, 62, 66)
COLOR_TEXT = (255, 255, 255)
COLOR_ACCENT = (200, 200, 200)

# Game State Colors (Wordle Official)
COLOR_CORRECT = (83, 141, 78)     # Green
COLOR_PRESENT = (181, 159, 59)    # Yellow
COLOR_ABSENT = (106, 106, 110)    # Gray

# Border Colors
COLOR_CORRECT_BORDER = (42, 71, 39)
COLOR_PRESENT_BORDER = (115, 101, 37)
COLOR_ABSENT_BORDER = (37, 37, 38)

# UI Colors
COLOR_BORDER = (100, 100, 100)
COLOR_HOVER = (100, 100, 100)
COLOR_RED = (200, 60, 60)
COLOR_BLUE = (50, 150, 200)

# Rank list / Gold Colors
COLOR_GOLD = (218, 165, 32)
COLOR_GOLD_BORDER = (184, 134, 11)
COLOR_GOLD_HOVER = (238, 185, 52)

# --- FONT CONFIGURATION ---
FONT_NAME = "Arial"
FONT_SIZE_TITLE = 50
FONT_SIZE_GUESS = 56
FONT_SIZE_MED = 30
FONT_SIZE_SMALL = 20