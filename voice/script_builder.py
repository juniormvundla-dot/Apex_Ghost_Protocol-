from __future__ import annotations

# Zero-AI Deterministic J.A.R.V.I.S. Script Builder
# Constructs dynamic, cinematic voice briefings using real-time system metrics
# (Hunter Rank, Discipline Streak, Quests, and Huberman Lab RSS feed)
# without requiring an LLM or paid API keys.

import random
from datetime import date

from quests.xp import xp_system
from quests.goal_manager import goal_manager
from quests.service import quest_service
from quests.models import QuestStatus
from scrapers.podcast_tracker import get_huberman_voice_update

MORNING_INTROS = [
    "Good morning, Sir. Awakening sequence and neural system calibration complete.",
    "Protocol awakening complete, Sir. All cognitive and productivity systems online.",
    "Welcome back to the grid, Sir. Morning awakening protocols successfully executed.",
    "Good morning, Sir. Your mindset and operational systems are fully calibrated for the day."
]

CLOSING_STATEMENTS = [
    "Workspace isolation is prepared. Let us execute with absolute discipline today, Sir.",
    "Distractions are locked down. Wishing you a powerful and high-output session today, Sir.",
    "Your execution strategy is clear. Proceeding to focused operational protocols.",
]


def build_morning_awakening_script() -> str:
    """
    Constructs a comprehensive morning voice briefing after awakening videos complete.
    Combines player ranking, streak, podcast intelligence, and daily objectives.
    """
    script_parts: list[str] = [random.choice(MORNING_INTROS)]

    # 1. Fetch Player Metrics
    try:
        summary = xp_system.get_summary()
        rank = str(summary.get("rank", "E"))
        streak = int(summary.get("streak", 0))
    except Exception:
        rank, streak = "E", 0

    try:
        goals = goal_manager.load()
        hunter_name = goals.profile.hunter_name or "Hunter"
        north_star = goals.profile.north_star or ""
    except Exception:
        hunter_name = "Hunter"
        north_star = ""

    # Player status line
    if streak > 0:
        script_parts.append(
            f"Hunter {hunter_name}, you currently stand at Rank {rank}, riding an active discipline streak of {streak} days."
        )
    else:
        script_parts.append(
            f"Hunter {hunter_name}, your current standing is Rank {rank}. Today is day one to rebuild your discipline streak."
        )

    # 2. Integrate Dr. Huberman Lab Podcast Intelligence
    try:
        podcast_notice = get_huberman_voice_update()
        if podcast_notice:
            script_parts.append(podcast_notice)
    except Exception as exc:
        print(f"[Script Builder] Podcast intelligence check bypassed: {exc}")

    # 3. Integrate Daily Quests and North Star
    try:
        today_quests = quest_service.get_today_daily_quests()
        pending_quests = [q.title for q in today_quests if q.status == QuestStatus.PENDING]
        
        if pending_quests:
            if len(pending_quests) == 1:
                quest_str = pending_quests[0]
            elif len(pending_quests) == 2:
                quest_str = f"{pending_quests[0]} and {pending_quests[1]}"
            else:
                top_two = ", ".join(pending_quests[:2])
                remainder = len(pending_quests) - 2
                quest_str = f"{top_two}, plus {remainder} other scheduled targets"
                
            script_parts.append(f"Your primary scheduled objectives for today include: {quest_str}.")
        else:
            script_parts.append("Your daily objective log is clear, with no pending quests remaining.")
    except Exception as exc:
        print(f"[Script Builder] Quests lookup bypassed: {exc}")

    if north_star:
        script_parts.append(f"Let us remain relentlessly aligned with your primary yearly goal: {north_star}.")

    # 4. Add Closing Statement
    script_parts.append(random.choice(CLOSING_STATEMENTS))

    return " ".join(script_parts)


def build_intelligence_script(trend_content: str, security_content: str) -> str:
    """
    Deterministically builds a J.A.R.V.I.S. voice briefing from scraped trend items and security logs
    without relying on an LLM.
    """
    script_parts: list[str] = [
        "Sir, I have compiled your daily intelligence report from primary global technology feeds."
    ]

    # Extract bullet points (headlines) from trend content
    headlines: list[str] = []
    for line in trend_content.splitlines():
        line_str = line.strip()
        if line_str.startswith("- ") and len(line_str) > 5:
            clean_title = line_str[2:].strip().replace('"', '').replace('|', ' ')
            if clean_title not in headlines:
                headlines.append(clean_title)

    if headlines:
        top_items = headlines[:2]
        if len(top_items) == 1:
            script_parts.append(f"A notable topic trending today is: {top_items[0]}.")
        else:
            script_parts.append(f"Key trending developments today include: {top_items[0]}, and {top_items[1]}.")
    else:
        script_parts.append("No critical tech trend items surpassed the filtering threshold today.")

    # Check security status
    if "No" in security_content or "no immediate" in security_content.lower() or not security_content.strip():
        script_parts.append("Your local system defense perimeter remains secure with zero immediate threats detected.")
    else:
        script_parts.append("Please review the terminal for active security findings and defensive protocols.")

    script_parts.append("All intelligence data has been logged to your dashboard.")
    return " ".join(script_parts)


def build_private_mode_script(
    hunter_name: str, 
    rank: str, 
    streak: int, 
    north_star: str, 
    pending_quests: int
) -> str:
    """
    Constructs a deterministic, immersive J.A.R.V.I.S. workspace initiation script.
    """
    script_parts = [
        "Welcome back, Sir. Secure deep-work isolation protocols are active.",
        f"Hunter {hunter_name}, current metrics confirm you at Rank {rank} with a {streak}-day active discipline chain."
    ]
    if north_star:
        script_parts.append(f"Focus target remains locked on: {north_star}.")
    if pending_quests > 0:
        script_parts.append(f"You have {pending_quests} active objectives remaining in today's log.")
    else:
        script_parts.append("All daily objectives are successfully finalized.")
    
    script_parts.append("External notifications are suppressed. Have a powerhouse session, Sir.")
    return " ".join(script_parts)
