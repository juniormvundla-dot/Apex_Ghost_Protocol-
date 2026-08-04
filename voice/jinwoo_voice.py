from __future__ import annotations

# This file defines the voice greeting used for Private Mode.
# The goal is to sound calm, confident, and immersive.

import sys
from pathlib import Path

# Add project root to sys.path to allow running this script directly
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from voice.tts import speak_text


PRIVATE_MODE_GREETING = (
    "Welcome back, Sir. Secure environment protocols are active. "
    "I have isolated the terminal and blocked all external notifications. "
    "Wish you a highly productive session."
)


def generate_greeting(hunter_name: str, rank: str, streak: int, north_star: str, pending_quests: int) -> str:
    """
    Construct a dynamic immersive greeting text in Jarvis AI style.
    """
    greeting = f"Welcome back, Sir. I have initiated workspace deep-work protocols. "
    greeting += f"Hunter {hunter_name}, current system reports list you at Rank {rank} with a {streak}-day active streak. "
    if north_star:
        greeting += f"Your primary yearly objective is registered as: {north_star}. "
    if pending_quests > 0:
        greeting += f"You have {pending_quests} pending objectives remaining in today's log. "
    else:
        greeting += "All daily objectives have been successfully completed. "
    greeting += "Workspace isolation is online, and distractions are locked out. Have a productive session, Sir."
    return greeting


def play_private_mode_greeting(greeting_text: str | None = None) -> None:
    """
    Speak the private mode greeting aloud.
    """
    text = greeting_text or PRIVATE_MODE_GREETING
    speak_text(text)


if __name__ == "__main__":
    play_private_mode_greeting()