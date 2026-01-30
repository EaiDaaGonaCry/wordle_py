# Constants.py

# --- SCREEN DIMENSIONS ---
WIDTH, HEIGHT = 1200, 800
FPS = 30

# --- COLORS ---
# Main Palette
COLOR_BG = (19, 19, 20)           # Main Background (Dark)
COLOR_PANEL_BG = (62, 62, 66)     # Lighter Gray for panels
COLOR_TEXT = (255, 255, 255)
COLOR_ACCENT = (200, 200, 200)

# Game State Colors
COLOR_CORRECT = (83, 141, 78)     # Green (Wordle Official)
COLOR_PRESENT = (181, 159, 59)    # Yellow (Wordle Official)
COLOR_ABSENT = (106, 106, 110)
COLOR_ACCENT = (200, 200, 200)
# Gray (Wordle Official)

# Game State Colors
COLOR_CORRECT_BORDER = (42, 71, 39)     # Green (Wordle Official)
COLOR_PRESENT_BORDER = (115, 101, 37)    # Yellow (Wordle Official)
COLOR_ABSENT_BORDER  = (37, 37, 38)       # Gray (Wordle Official)

# UI Colors
COLOR_BORDER = (100, 100, 100)
COLOR_HOVER = (100, 100, 100)
COLOR_RED = (200, 60, 60)         # Error / Loss
COLOR_BLUE = (50, 150, 200)       # History / Info

# --- FONT CONFIGURATION ---
# Note: We store sizes/names here, but create the Font Objects
# in the main scripts after pygame.init() to avoid errors.
FONT_NAME = "Arial"
FONT_SIZE_TITLE = 50
FONT_SIZE_GUESS = 56
FONT_SIZE_MED = 30
FONT_SIZE_SMALL = 20