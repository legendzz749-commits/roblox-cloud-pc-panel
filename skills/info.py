"""Live info skills — time, date, weather."""
import requests
from datetime import datetime


def current_time() -> str:
    return f"It's {datetime.now().strftime('%I:%M %p')}, sir."


def current_date() -> str:
    return f"Today is {datetime.now().strftime('%A, %B %d, %Y')}."


def weather(config) -> str:
    """Uses wttr.in — free, no API key needed."""
    try:
        city = config.get("city", "")  # empty = auto-detect by IP
        r = requests.get(
            f"https://wttr.in/{city}?format=%C,+%t,+feels+like+%f",
            timeout=10,
            headers={"User-Agent": "curl"},
        )
        if r.status_code == 200:
            return f"Current weather: {r.text.strip()}"
        return "Weather service unavailable right now, sir."
    except Exception:
        return "I couldn't reach the weather service, sir."
