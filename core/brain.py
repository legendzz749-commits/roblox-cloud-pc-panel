"""
The Brain — sends conversation to an LLM and gets responses.
Supports Anthropic (Claude), OpenAI, and OpenRouter.
"""
import requests


class Brain:
    def __init__(self, config, memory):
        self.config = config
        self.memory = memory
        self.provider = config["ai_provider"]
        self.history = []  # this session's conversation

    def think(self, user_message: str) -> str:
        self.history.append({"role": "user", "content": user_message})

        # Keep history manageable (last 20 messages)
        if len(self.history) > 20:
            self.history = self.history[-20:]

        # Build system prompt with long-term memory injected
        system = self.config["personality"]
        remembered = self.memory.recall()
        if remembered:
            system += f"\n\nThings you remember about the user:\n{remembered}"

        try:
            if self.provider == "anthropic":
                reply = self._ask_claude(system)
            elif self.provider == "openai":
                reply = self._ask_openai(system)
            elif self.provider == "openrouter":
                reply = self._ask_openrouter(system)
            else:
                return "No AI provider configured, sir."
        except Exception as e:
            return f"I'm having trouble reaching my brain, sir. {e}"

        self.history.append({"role": "assistant", "content": reply})

        # Auto-save facts the user asks to remember
        if "remember" in user_message.lower():
            self.memory.store(user_message)

        return reply

    def _ask_claude(self, system: str) -> str:
        r = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": self.config["anthropic_api_key"],
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": self.config.get("model", "claude-sonnet-4-6"),
                "max_tokens": 500,
                "system": system,
                "messages": self.history,
            },
            timeout=30,
        )
        r.raise_for_status()
        return r.json()["content"][0]["text"]

    def _ask_openai(self, system: str) -> str:
        r = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {self.config['openai_api_key']}"},
            json={
                "model": self.config.get("model", "gpt-4o-mini"),
                "messages": [{"role": "system", "content": system}] + self.history,
                "max_tokens": 500,
            },
            timeout=30,
        )
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]

    def _ask_openrouter(self, system: str) -> str:
        r = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {self.config['openrouter_api_key']}"},
            json={
                "model": self.config.get("model", "anthropic/claude-sonnet-4"),
                "messages": [{"role": "system", "content": system}] + self.history,
                "max_tokens": 500,
            },
            timeout=30,
        )
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]
