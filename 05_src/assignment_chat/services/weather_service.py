# 05_src/assignment_chat/services/weather_service.py
"""
Service 1: API Calls — Open-Meteo Weather

Requirement:
- Call a public API (Open-Meteo)
- Convert JSON output into a natural language summary:
  - temperature range
  - precipitation probability
  - clothing / outdoor activity advice

Notes:
- This implementation uses Toronto lat/lon by default (stable for demo).
- Can extend it with a city->lat/lon map if needed.
"""

from __future__ import annotations

from typing import Any, Dict, Tuple
import requests


def _toronto_lat_lon() -> Tuple[float, float]:
    # Stable default for the assignment demo
    return 43.6532, -79.3832


def _clothing_advice(avg_temp_c: float, precip_prob: float) -> str:
    tips = []

    # Temperature-based advice
    if avg_temp_c <= 0:
        tips.append("Very cold: wear a heavy coat, gloves, and a hat.")
    elif avg_temp_c <= 10:
        tips.append("Chilly: a warm jacket and long pants are recommended.")
    elif avg_temp_c <= 20:
        tips.append("Mild: a light jacket or hoodie should be fine.")
    else:
        tips.append("Warm: a t-shirt or light long-sleeve is usually enough.")

    # Rain-based advice
    if precip_prob >= 60:
        tips.append("High rain chance: bring an umbrella or waterproof jacket.")
    elif precip_prob >= 25:
        tips.append("Possible light rain: consider a small umbrella.")
    else:
        tips.append("Low rain chance: great for outdoor activities.")

    return " ".join(tips)


def get_weather_summary(city: str = "Toronto") -> str:
    """
    Returns a natural language weather summary for today.
    """
    # For this assignment, we keep it simple and stable: Toronto only.
    # If city != Toronto, we still use Toronto coordinates as a fallback.
    lat, lon = _toronto_lat_lon()

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max",
        "timezone": "America/Toronto",
        "forecast_days": 1,
    }

    r = requests.get(url, params=params, timeout=20)
    r.raise_for_status()

    data: Dict[str, Any] = r.json()
    daily = data.get("daily", {})

    tmax = daily.get("temperature_2m_max", [None])[0]
    tmin = daily.get("temperature_2m_min", [None])[0]
    pmax = daily.get("precipitation_probability_max", [None])[0]

    # Defensive defaults
    if not isinstance(tmax, (int, float)) or not isinstance(tmin, (int, float)):
        return "Weather data is unavailable right now. Please try again."

    precip = float(pmax) if isinstance(pmax, (int, float)) else 0.0
    avg_temp = (tmax + tmin) / 2.0

    advice = _clothing_advice(avg_temp, precip)

    return (
        f"📍 {city} weather today: {tmin:.0f}°C to {tmax:.0f}°C, "
        f"max precipitation probability about {precip:.0f}%. "
        f"{advice}"
    )
