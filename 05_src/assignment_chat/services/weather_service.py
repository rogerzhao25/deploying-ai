# 05_src/assignment_chat/services/weather_service.py
"""
Service 1: API Calls — Open-Meteo Weather

Requirement:
- Call a public API (Open-Meteo)
- Convert JSON output into a natural language summary:
  - temperature range
  - precipitation probability
  - clothing / outdoor activity advice

Modes:
- today    → standard daily summary (1 day)
- outfit   → clothing-focused advice (1 day)
- forecast → N-day forecast (default 3 days)

Supports:
get_weather_summary(city="Toronto", mode="forecast", days=5)

Notes:
- This implementation uses Toronto lat/lon by default (stable for demo).
- Can extend it with a city->lat/lon map if needed.
"""

from __future__ import annotations
from typing import Any, Dict, Tuple
import requests


# -----------------------------------------------------
# Helper: GEO Location
# -----------------------------------------------------
def _toronto_lat_lon() -> Tuple[float, float]:
    # Stable default for the assignment demo
    return 43.6532, -79.3832


# -----------------------------------------------------
# Helper: call Open-Meteo API
# -----------------------------------------------------
def _fetch_weather_json(lat: float, lon: float, days: int) -> Dict[str, Any]:
    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max",
        "timezone": "America/Toronto",
        "forecast_days": days,
    }

    r = requests.get(url, params=params, timeout=20)
    r.raise_for_status()
    return r.json()




# -----------------------------------------------------
# Helper: clothing advice generator
# -----------------------------------------------------
def _clothing_advice(avg_temp: float, rain_prob: float) -> str:
    # Temperature advice
    if avg_temp <= 0:
        clothing = "Very cold: wear a heavy coat, gloves, and a hat."
    elif avg_temp <= 10:
        clothing = "Chilly: wear a warm jacket."
    elif avg_temp <= 20:
        clothing = "Mild: a light jacket should be fine."
    else:
        clothing = "Warm: a t-shirt or light clothing is enough."

    # Rain advice
    if rain_prob >= 60:
        rain = "High rain chance: bring an umbrella or waterproof jacket."
    elif rain_prob >= 25:
        rain = "Possible light rain: consider a small umbrella."
    else:
        rain = "Low rain chance: great for outdoor activities."

    return f"{clothing} {rain}"


# -----------------------------------------------------
# Main public function
# -----------------------------------------------------
def get_weather_summary(city: str = "Toronto", mode: str = "today", days: int = 3) -> str:
    """
    Parameters
    ----------
    city : str
        Stable demo uses Toronto coordinates.
    mode : str
        today / outfit / forecast
    days : int
        Only used when mode == "forecast".
        Default is 3. Allowed range is clamped to 1..14.

    Returns
    -------
    Natural language weather summary.
    """
    # For this assignment, we keep it simple and stable: Toronto only.
    # If city != Toronto, we still use Toronto coordinates as a fallback.
    lat, lon = _toronto_lat_lon()

    # Clamp days to a safe Open-Meteo range (commonly up to 14/16 depending on endpoint)
    days = int(days) if isinstance(days, (int, float, str)) else 3
    if days < 1:
        days = 1
    if days > 14:
        days = 14

    # -------------------------------------------------
    # TODAY + OUTFIT MODE (1-day forecast)
    # -------------------------------------------------
    if mode in ["today", "outfit"]:
        data = _fetch_weather_json(lat, lon, days=1)
        daily = data["daily"]

        tmax = daily["temperature_2m_max"][0]
        tmin = daily["temperature_2m_min"][0]
        rain = daily["precipitation_probability_max"][0]
        avg_temp = (tmax + tmin) / 2

        advice = _clothing_advice(avg_temp, rain)

        if mode == "outfit":
            return (
                f"Today in Toronto: {tmin:.0f}°C–{tmax:.0f}°C. "
                f"{advice}"
            )

        return (
            f"📍 Toronto weather today: {tmin:.0f}°C to {tmax:.0f}°C, "
            f"max precipitation probability about {rain:.0f}%. "
            f"{advice}"
        )

    # -------------------------------------------------
    # FORECAST MODE (N-day forecast)
    # -------------------------------------------------
    if mode == "forecast":
        data = _fetch_weather_json(lat, lon, days=days)
        daily = data["daily"]

        tmax_list = daily.get("temperature_2m_max", [])
        tmin_list = daily.get("temperature_2m_min", [])
        rain_list = daily.get("precipitation_probability_max", [])

        # Determine how many days we actually received (defensive)
        n = min(days, len(tmax_list), len(tmin_list), len(rain_list))

        if n == 0:
            return "Forecast data is unavailable right now. Please try again."

        lines = []
        for i in range(n):
            lines.append(
                f"Day {i+1}: {tmin_list[i]:.0f}°C–{tmax_list[i]:.0f}°C (rain {rain_list[i]:.0f}%)"
            )

        return f"📅 Toronto {n}-day forecast:\n" + "\n".join(lines)

    # -------------------------------------------------
    # Fallback
    # -------------------------------------------------
    return "Weather mode not recognized."
