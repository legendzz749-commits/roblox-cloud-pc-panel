"""PC control — open/close apps, screenshots, volume, web search. Windows-focused."""
import os
import subprocess
import webbrowser
from datetime import datetime

# Common app aliases -> executable names
APP_MAP = {
    "chrome": "chrome",
    "browser": "chrome",
    "firefox": "firefox",
    "edge": "msedge",
    "notepad": "notepad",
    "calculator": "calc",
    "word": "winword",
    "excel": "excel",
    "spotify": "spotify",
    "discord": "discord",
    "steam": "steam",
    "file explorer": "explorer",
    "explorer": "explorer",
    "task manager": "taskmgr",
    "settings": "ms-settings:",
    "cmd": "cmd",
    "terminal": "wt",
    "vs code": "code",
    "code": "code",
}


def open_app(name: str) -> str:
    key = name.lower().strip()
    exe = APP_MAP.get(key, key)
    try:
        if exe.startswith("ms-settings"):
            os.system(f"start {exe}")
        else:
            os.system(f"start {exe}")
        return f"Opening {name}, sir."
    except Exception as e:
        return f"I couldn't open {name}. {e}"


def close_app(name: str) -> str:
    key = name.lower().strip()
    exe = APP_MAP.get(key, key)
    try:
        result = subprocess.run(
            ["taskkill", "/IM", f"{exe}.exe", "/F"],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            return f"Closed {name}, sir."
        return f"{name} doesn't appear to be running."
    except Exception as e:
        return f"Couldn't close {name}. {e}"


def screenshot() -> str:
    try:
        import pyautogui
        filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        path = os.path.join(os.path.expanduser("~"), "Pictures", filename)
        pyautogui.screenshot(path)
        return f"Screenshot saved to Pictures, sir."
    except Exception as e:
        return f"Screenshot failed. {e}"


def volume(cmd: str) -> str:
    try:
        import pyautogui
        if "up" in cmd:
            for _ in range(5):
                pyautogui.press("volumeup")
            return "Volume up."
        elif "down" in cmd:
            for _ in range(5):
                pyautogui.press("volumedown")
            return "Volume down."
        elif "mute" in cmd:
            pyautogui.press("volumemute")
            return "Muted."
    except Exception as e:
        return f"Volume control failed. {e}"
    return "Volume command not understood."


def web_search(query: str) -> str:
    webbrowser.open(f"https://www.google.com/search?q={query.replace(' ', '+')}")
    return f"Searching for {query}, sir."
