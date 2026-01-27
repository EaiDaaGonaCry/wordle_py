import pygame
import json
import os

STATS_FILE = "Files/stats.json"

DARK_GRAY = (62, 62, 66) # A dark gray to match your theme
TEXT_WHITE = (255, 255, 255)
ACCENT_GREEN = (106, 170, 100)


def load_stats():
    if not os.path.exists(STATS_FILE):
        return {"played": 0, "wins": 0, "curr_streak": 0, "max_streak": 0}
    try:
        with open(STATS_FILE, "r") as f:
            return json.load(f)
    except:
        return {"played": 0, "wins": 0, "curr_streak": 0, "max_streak": 0}

def save_stats(stats):
    with open(STATS_FILE, "w") as f:
        json.dump(stats, f)


def update_stats(is_win):
    stats = load_stats()

    stats["played"] += 1

    if is_win:
        stats["wins"] += 1
        stats["curr_streak"] += 1
        if stats["curr_streak"] > stats["max_streak"]:
            stats["max_streak"] = stats["curr_streak"]
    else:
        stats["curr_streak"] = 0

    save_stats(stats)
    return stats

