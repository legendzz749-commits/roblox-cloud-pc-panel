"""Everyday tools — reminders, system status."""
import json
import os
import threading
import time
import re
from datetime import datetime

REMINDERS_FILE = "reminders.json"


def set_reminder(command: str) -> str:
    """
    Parses 'remind me to X in N minutes' style commands.
    Runs a background timer + persists to file.
    """
    match = re.search(r"remind me (?:to )?(.+?) in (\d+) (minute|minutes|hour|hours|second|seconds)", command.lower())
    if not match:
        return "Say it like: remind me to check the oven in 10 minutes."

    task, amount, unit = match.group(1), int(match.group(2)), match.group(3)
    seconds = amount * (3600 if "hour" in unit else 60 if "minute" in unit else 1)

    # Persist
    reminders = []
    if os.path.exists(REMINDERS_FILE):
        try:
            with open(REMINDERS_FILE) as f:
                reminders = json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    reminders.append({"task": task, "set_at": datetime.now().isoformat(), "seconds": seconds})
    with open(REMINDERS_FILE, "w") as f:
        json.dump(reminders, f, indent=2)

    # Background timer
    def fire():
        time.sleep(seconds)
        print(f"\n🔔 REMINDER: {task}")
        try:
            import pyttsx3
            engine = pyttsx3.init()
            engine.say(f"Sir, reminding you to {task}")
            engine.runAndWait()
        except Exception:
            pass

    threading.Thread(target=fire, daemon=True).start()
    return f"Reminder set: {task} in {amount} {unit}."


def system_status() -> str:
    try:
        import psutil
        cpu = psutil.cpu_percent(interval=0.5)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        battery = psutil.sensors_battery()
        parts = [
            f"CPU at {cpu} percent",
            f"memory at {mem.percent} percent",
            f"disk at {disk.percent} percent",
        ]
        if battery:
            parts.append(f"battery at {battery.percent} percent")
        return "System status: " + ", ".join(parts) + "."
    except ImportError:
        return "Install psutil for system status: pip install psutil"
