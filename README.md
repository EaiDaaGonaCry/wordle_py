# 🧠 Wordle: Extreme & Reverse Edition

A Python-based evolution of the classic word game, built with Pygame. This project goes beyond standard Wordle by introducing an **"Extreme" difficulty** where the game (or player) can lie, and a **Reverse Mode** where the computer tries to guess *your* word.

## 🌟 Unique Features

### 1. Game Modes
* **👤 Singleplayer (Classic):** You guess the computer's secret word.
* **🤖 AI Solver (Reverse Mode):** *Like Akinator for words.* You think of a secret word, and the computer tries to guess it. You provide the feedback (Green/Yellow/Grey).
* **⚔️ PvE (Race Mode):** Race against a bot to see who can solve the same word first.

### 2. Difficulty Levels
* **Normal:** Standard Wordle rules. Feedback is always 100% accurate.
* **🔥 Extreme ( The "Lie" Mechanic):**
    * **In Singleplayer:** The computer provides feedback, but **one of the color hints might be a lie** (e.g., marking a letter Green when it should be Yellow). You must use logic to deduce which hint is false.
    * **In AI Solver:** You (the player) are allowed to give **one fake feedback** to try and trick the computer. The AI includes a "Lie Detector" logic to try and filter out your deception.

### 3. Core Mechanics
* **Dynamic Scoring:** Points awarded based on speed, accuracy, and difficulty setting.
* **Infinite Play:** "Endless" mode that continues until a loss.
* **Leaderboard:** Local top 10 high scores saved to JSON.
* **Word Editor:** Built-in GUI to add or remove valid words from `valid-wordle-words.txt`.

## 🛠️ Technical Implementation

### Algorithms
* **Entropy & Filtering:** The AI Solver uses information theory (reduction of search space) to pick the statistically best next guess.
* **Lie Detection:** In Extreme AI Mode, the logic engine cross-references inconsistent feedback to identify which previous clue was likely false.
* **Levenshtein Distance:** Used in PvE bots to calculate word similarity for "human-like" guessing patterns.

### Tech Stack
* **Engine:** Python 3.10+ & `pygame`
* **Data:** JSON (Stats), Text Files (Dictionary)
* **APIs:** Google Gemini (Optional for advanced PvE bot logic)

## 📂 Project Structure

```text
├── Modes/
│   ├── AiMode.py          # Reverse Mode (Computer guesses YOUR word)
│   ├── PlayerMode.py      # Classic Mode (You guess the word)
│   └── PveMode.py         # Race Mode (You vs Bot)
├── Settings/
│   ├── Logic.py           # Core algorithms (Lie detector, Solver logic)
│   ├── DifficultyMenu.py  # Select Normal vs Extreme
│   └── ...
├── tests/                 # Unit tests for logic and UI
└── wordle.py              # Main entry point
