"""
Skill dispatcher — checks if a command matches a local skill
before falling back to the AI brain. Local skills are instant
and don't cost API tokens.
"""
from skills import pc_control, info, tools, files, browser


class SkillDispatcher:
    def __init__(self, config, mouth, brain=None):
        self.config = config
        self.mouth = mouth
        self.brain = brain

    def try_handle(self, command: str) -> bool:
        result = self.handle(command)
        if result is None:
            return False
        self.mouth.say(result)
        return True

    def handle(self, command: str):
        """Returns response string if a skill matched, else None."""
        cmd = command.lower()

        # --- PC control ---
        if cmd.startswith("open "):
            return pc_control.open_app(command[5:].strip())
        if cmd.startswith("close "):
            return pc_control.close_app(command[6:].strip())
        if "take a screenshot" in cmd or cmd == "screenshot":
            return pc_control.screenshot()
        if "volume up" in cmd or "volume down" in cmd or "mute" in cmd:
            return pc_control.volume(cmd)
        if cmd.startswith("search for ") or cmd.startswith("google "):
            query = command.replace("search for", "").replace("google", "").strip()
            return pc_control.web_search(query)

        # --- File management ---
        if cmd.startswith("find file") or cmd.startswith("find my"):
            keyword = command.split(" ", 2)[-1].replace("file", "").strip()
            return files.find_files(keyword)
        if "organize" in cmd and ("downloads" in cmd or "desktop" in cmd or "documents" in cmd):
            folder = "downloads" if "downloads" in cmd else "desktop" if "desktop" in cmd else "documents"
            return files.organize_folder(folder)
        if "biggest files" in cmd or "largest files" in cmd:
            return files.biggest_files()

        # --- Browser automation ---
        if cmd.startswith("research "):
            return browser.research(command[9:].strip(), self.brain)
        if cmd.startswith("read page ") or cmd.startswith("read website "):
            url = command.split(" ", 2)[-1].strip()
            if not url.startswith("http"):
                url = "https://" + url
            content = browser.read_page(url)
            if self.brain:
                return self.brain.think(f"Summarize this webpage in 3 sentences: {content[:3000]}")
            return content[:600]
        if cmd.startswith("capture page ") or cmd.startswith("screenshot page "):
            url = command.split(" ", 2)[-1].strip()
            if not url.startswith("http"):
                url = "https://" + url
            return browser.screenshot_page(url)

        # --- Info skills ---
        if "time" in cmd and ("what" in cmd or "current" in cmd):
            return info.current_time()
        if "date" in cmd and ("what" in cmd or "today" in cmd):
            return info.current_date()
        if "weather" in cmd:
            return info.weather(self.config)

        # --- Tools ---
        if cmd.startswith("remind me"):
            return tools.set_reminder(command)
        if "system status" in cmd or "system info" in cmd:
            return tools.system_status()

        return None
