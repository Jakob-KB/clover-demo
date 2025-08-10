# /src/utils/misc.py

from time import sleep
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict
import random

SYSTEM_PROMPT_FILEPATH: Path = Path(__file__).parent.parent / "resources" / "system_prompt.prmpt"

def pad_convo_label(convo_name: str, last_turn: str, total_width: int = 24) -> str:
    visible_len = len(convo_name) + len(last_turn)
    padding_len = total_width - visible_len
    padding_len = max(padding_len, 1)
    padding = " " * padding_len
    return f"{convo_name}{padding}:gray[{last_turn}]"

def iso_to_readable(iso_str: str) -> str:
    dt = datetime.fromisoformat(iso_str)
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def get_random_conversation_name() -> str:
    ADJECTIVES = [
        "Silent", "Golden", "Quantum", "Majestic", "Frosty", "Shy", "Bold",
        "Radiant", "Velvety", "Hidden", "Witty", "Zany", "Lively", "Eager",
        "Rapid", "Swift", "Crimson", "Cosmic", "Bouncy", "Brisk", "Cheery",
        "Gentle", "Mellow", "Chilly", "Curious", "Playful", "Mystic", "Nimble"
    ]

    NOUNS = [
        "Echo", "Pulse", "Labyrinth", "Nexus", "Odyssey", "Signal", "Summit",
        "Vertex", "Mirage", "Beacon", "Galaxy", "Whisper", "Harbor", "Fragment",
        "Crystal", "Voyager", "Orbit", "Flame", "Nova", "Dust", "Cloud", "Meadow",
        "Horizon", "Circuit", "Pattern", "Memory", "Sparkle"
    ]

    number = f"{random.randint(0, 99):02d}"
    adjective = random.choice(ADJECTIVES)
    noun = random.choice(NOUNS)

    while len(adjective) + len(noun) > 16:
        adjective = random.choice(ADJECTIVES)
        noun = random.choice(NOUNS)

    return f"{adjective}-{noun}-{number}"

def time_ago(dt_str: str | datetime):
    now = datetime.now(timezone.utc)

    if isinstance(dt_str, str):
        dt_str = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))

    then = dt_str
    delta = now - then

    seconds = int(delta.total_seconds())
    if seconds <= 15:
        return "0s"
    if seconds <= 30:
        return "15s"
    if seconds <= 45:
        return "30s"
    if seconds <= 60:
        return "45s"
    minutes = seconds // 60
    if minutes < 60:
        return f"{minutes}m"
    hours = minutes // 60
    if hours < 24:
        return f"{hours}h"
    days = hours // 24
    return f"{min(days, 99)}d"

def sort_recent_conversations(convos: List[Dict[str, str]]) -> List[Dict[str, str]]:
    def parse_datetime(val):
        if isinstance(val, datetime):
            return val
        elif isinstance(val, str):
            try:
                return datetime.fromisoformat(val.replace("Z", "+00:00"))
            except ValueError:
                return datetime.min
        return datetime.min

    return sorted(convos, key=lambda c: parse_datetime(c["updated_at"]), reverse=True)

def stream_to_ui(text: str, delay: float = 0.001):
    """
    Yields text chunks character-by-character to simulate streaming.
    """
    for char in text:
        yield char
        sleep(delay)
