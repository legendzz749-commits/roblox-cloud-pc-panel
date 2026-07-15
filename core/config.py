"""Config loading — reads config.json, creates default if missing."""
import json
import os

DEFAULT_CONFIG = {
    "wake_word": "jarvis",
    "push_to_talk": False,          # True = press enter to talk (no wake word needed)
    "ai_provider": "anthropic",     # anthropic | openai | openrouter
    "anthropic_api_key": "PUT_YOUR_KEY_HERE",
    "openai_api_key": "",
    "openrouter_api_key": "",
    "model": "claude-sonnet-4-6",
    "voice_rate": 180,              # TTS speaking speed
    "voice_index": 0,               # which system voice to use
    "memory_file": "jarvis_memory.json",
    "personality": (
        "You are JARVIS, a witty and loyal AI assistant modeled after "
        "Tony Stark's AI. You are concise, capable, and address the user "
        "as 'sir'. Keep responses short since they will be spoken aloud — "
        "2 or 3 sentences max unless asked for detail."
    ),
}

CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.json")


def load_config() -> dict:
    if not os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "w") as f:
            json.dump(DEFAULT_CONFIG, f, indent=2)
        print(f"[config] Created default config at {CONFIG_PATH}")
        print("[config] Add your API key to config.json before running again!")

    with open(CONFIG_PATH) as f:
        config = json.load(f)

    # Fill any missing keys with defaults
    for k, v in DEFAULT_CONFIG.items():
        config.setdefault(k, v)
    return config
