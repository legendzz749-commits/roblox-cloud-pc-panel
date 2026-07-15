"""Long-term memory — simple JSON file that persists across sessions."""
import json
import os
from datetime import datetime


class Memory:
    def __init__(self, path):
        self.path = path
        self.data = {"facts": []}
        if os.path.exists(path):
            try:
                with open(path) as f:
                    self.data = json.load(f)
            except (json.JSONDecodeError, OSError):
                pass

    def store(self, fact: str):
        self.data["facts"].append({
            "fact": fact,
            "when": datetime.now().isoformat(timespec="seconds"),
        })
        self._save()

    def recall(self) -> str:
        facts = self.data.get("facts", [])[-30:]  # last 30 facts
        return "\n".join(f"- {f['fact']}" for f in facts)

    def _save(self):
        with open(self.path, "w") as f:
            json.dump(self.data, f, indent=2)
