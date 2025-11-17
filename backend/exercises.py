import random
from typing import List, Tuple, Dict, Any


def generate_nback_sequence(length: int, n: int, symbols=None) -> Tuple[List[str], List[bool]]:
    if symbols is None:
        symbols = ["A", "B", "C", "D"]
    seq = []
    targets = []
    for i in range(length):
        if i >= n and random.random() < 0.3:
            # repeat n-back
            seq.append(seq[i-n])
            targets.append(True)
        else:
            choices = [s for s in symbols if not (i >= n and s == seq[i-n])]
            c = random.choice(choices)
            seq.append(c)
            targets.append(False)
    return seq, targets


def build_nback_config(level: int = 1) -> Dict[str, Any]:
    n = max(1, min(level, 3))
    length = 20
    seq, targets = generate_nback_sequence(length, n)
    return {
        "type": "nback",
        "n": n,
        "sequence": seq,
        "targets": targets,
        "duration_sec": 60,
        "description": f"{n}-back working memory game",
    }


def build_breathing_config() -> Dict[str, Any]:
    return {
        "type": "breathing",
        "pattern": "4-4-6",
        "duration_sec": 60,
        "description": "Inhale 4s, hold 4s, exhale 6s",
    }


def build_gratitude_config() -> Dict[str, Any]:
    return {
        "type": "gratitude",
        "prompts": [
            "Name one small thing today that made you smile.",
            "Who is one person you’re grateful for, and why?",
            "What’s something about yourself you appreciate?"
        ],
        "duration_sec": 60,
        "description": "Guided gratitude journaling",
    }
