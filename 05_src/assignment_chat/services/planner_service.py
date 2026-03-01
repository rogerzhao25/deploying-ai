# 05_src/assignment_chat/services/planner_service.py

"""
Service 3: Function Calling — plan_day_trip

Creates a 1-day itinerary based on:
- city
- budget (low / medium / high)
- preferences (museum / food / nature / shopping / family / date / solo)

Uses ONLY local semantic search results (no web search).
Returns structured JSON.
"""

from __future__ import annotations

from typing import Dict, List
from .semantic_service import semantic_search


def plan_day_trip(
    city: str,
    budget: str,
    preferences: List[str]
) -> Dict:
    """
    Returns structured itinerary:
    {
        "city": "...",
        "budget": "...",
        "preferences": [...],
        "itinerary": [
            {"time": "Morning", ...},
            {"time": "Afternoon", ...},
            {"time": "Evening", ...}
        ],
        "transit_advice": "..."
    }
    """

    # -----------------------------
    # 1. Build semantic search query
    # -----------------------------
    pref_text = " ".join(preferences) if preferences else "sightseeing"
    query = f"{city} {budget} {pref_text}"

    results = semantic_search(query, k=8)

    if not results:
        return {
            "city": city,
            "budget": budget,
            "preferences": preferences,
            "itinerary": [],
            "transit_advice": "No local data available to build an itinerary."
        }

    # -----------------------------
    # 2. Simple budget filtering
    # -----------------------------
    filtered = []

    for doc, meta in results:
        price_level = meta.get("price_level", "").lower()

        if budget == "low" and price_level in ["low", ""]:
            filtered.append((doc, meta))

        elif budget == "medium" and price_level in ["low", "medium", ""]:
            filtered.append((doc, meta))

        elif budget == "high":
            filtered.append((doc, meta))

    if not filtered:
        filtered = results  # fallback if filter too strict

    # -----------------------------
    # 3. Pick top 3 for morning/afternoon/evening
    # -----------------------------
    slots = ["Morning", "Afternoon", "Evening"]
    itinerary = []

    for i in range(min(3, len(filtered))):
        doc, meta = filtered[i]

        itinerary.append({
            "time": slots[i],
            "place": meta.get("name", "Unknown"),
            "category": meta.get("category", ""),
            "neighborhood": meta.get("neighborhood", ""),
            "highlights": meta.get("highlights", ""),
            "tips": meta.get("tips", ""),
            "transit": meta.get("transit", ""),
            "estimated_duration_hours": meta.get("duration_hours", "")
        })

    # -----------------------------
    # 4. Transit advice
    # -----------------------------
    transit_advice = (
        "Use TTC subway or streetcar for efficient travel between neighborhoods. "
        "Combine walking for nearby attractions."
    )

    if budget == "low":
        transit_advice += " Consider staying within the same area to reduce transit costs."

    elif budget == "high":
        transit_advice += " Ride-share can help save time in the evening."

    return {
        "city": city,
        "budget": budget,
        "preferences": preferences,
        "itinerary": itinerary,
        "transit_advice": transit_advice
    }
