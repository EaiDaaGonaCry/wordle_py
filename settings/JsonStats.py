"""
Handles loading and saving the leaderboard statistics to a JSON file.
"""
import json
import os
from typing import List, Dict, Union

STATS_FILE = "Files/leaderboard.json"


def load_leaderboard() -> List[Dict[str, Union[str, int]]]:
    """Loads the leaderboard from the JSON file."""
    if not os.path.exists(STATS_FILE):
        return []

    try:
        with open(STATS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            return []
    except (json.JSONDecodeError, IOError):
        return []


def save_score(name: str, score: int) -> None:
    """Saves a new score to the leaderboard."""
    leaderboard = load_leaderboard()
    leaderboard.append({"name": name, "score": score})

    leaderboard.sort(key=lambda x: int(x["score"]), reverse=True)

    leaderboard = leaderboard[:10]

    os.makedirs(os.path.dirname(STATS_FILE), exist_ok=True)

    try:
        with open(STATS_FILE, "w", encoding="utf-8") as f:
            json.dump(leaderboard, f, ensure_ascii=False, indent=4)
    except IOError as e:
        print(f"Error saving leaderboard: {e}")