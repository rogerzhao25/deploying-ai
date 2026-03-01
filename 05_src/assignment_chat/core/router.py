# 05_src/assignment_chat/core/router.py
"""
Intent router for the Toronto City Tour Assistant.

This decides which service should handle the user request:
- weather  -> Service 1 (Open-Meteo API)
- semantic -> Service 2 (Chroma semantic search)
- plan     -> Service 3 (Function calling: plan_day_trip)
- chitchat -> fallback conversational response
"""

from __future__ import annotations

from typing import Literal

Intent = Literal["weather", "semantic", "plan", "chitchat"]


def route_intent(user_text: str) -> Intent:
    """Return the detected intent from user input."""
    if not user_text:
        return "chitchat"

    text = user_text.lower()

    # -------------------------
    # Weather intent (Service 1)
    # -------------------------
    WEATHER_KEYWORDS = [
        "weather",
        "temperature",
        "forecast",
        "rain",
        "snow",
        "umbrella",
        "what should i wear",
        "is it cold",
        "is it hot",
    ]
    if any(k in text for k in WEATHER_KEYWORDS):
        return "weather"

    # -------------------------
    # Semantic search intent (Service 2)
    # Attractions / transit / tips
    # -------------------------
    SEMANTIC_KEYWORDS = [
        "nearby",
        "attractions",
        "recommend",
        "things to do",
        "museum",
        "park",
        "food",
        "restaurant",
        "shopping",
        "transit",
        "subway",
        "streetcar",
        "bus",
        "ttc",
        "ticket",
        "fare",
        "tips",
        "introduction",
    ]
    if any(k in text for k in SEMANTIC_KEYWORDS):
        return "semantic"

    # -------------------------
    # Day trip / itinerary intent (Service 3)
    # -------------------------
    PLAN_KEYWORDS = [
        "plan",
        "itinerary",
        "day trip",
        "one day trip",
        "schedule",
        "trip plan",
        "plan my day",
        "plan a trip",
    ]
    if any(k in text for k in PLAN_KEYWORDS):
        return "plan"

    # -------------------------
    # Default fallback
    # -------------------------
    return "chitchat"
