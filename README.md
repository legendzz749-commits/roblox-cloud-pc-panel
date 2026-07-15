# J.A.R.V.I.S. — Personal AI Assistant

Voice-controlled AI assistant for Windows. Talks, listens, controls your PC, remembers things.

## Features
- 🎤 Voice input (wake word "jarvis" or push-to-talk)
- 🔊 Voice output (offline Windows TTS — no GPU needed)
- 🧠 AI brain — Claude, ChatGPT, or OpenRouter (your choice)
- 💻 PC control — open/close apps, screenshots, volume, web search
- 🌦️ Live info — time, date, weather (no API key needed)
- ⏰ Reminders with voice alerts
- 📊 System status (CPU, RAM, disk, battery)
- 💾 Long-term memory — remembers across sessions

## Setup

1. Install Python 3.10+
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
   > If pyaudio fails on Windows: `pip install pipwin && pipwin install pyaudio`
3. Run once to generate config:
   ```
   python main.py
   ```
4. Open `config.json` and add your API key (Anthropic, OpenAI, or OpenRouter)
5. Run again:
   ```
   python main.py
   ```

## Usage

Say **"jarvis"** then your command:
- "open chrome" / "close spotify"
- "what time is it" / "what's the weather"
- "take a screenshot"
- "volume up" / "mute"
- "remind me to check the oven in 10 minutes"
- "system status"
- "remember that my favorite color is blue"
- anything else → goes to the AI brain

Say **"shut down"** to exit.

## Config options (config.json)
| Key | What it does |
|-----|-------------|
| `wake_word` | Word that activates listening (default: "jarvis") |
| `push_to_talk` | `true` = press Enter instead of wake word (easier for testing) |
| `ai_provider` | `anthropic`, `openai`, or `openrouter` |
| `model` | Model name for your provider |
| `voice_rate` | Speaking speed (default 180) |
| `voice_index` | Which Windows voice (0, 1, 2...) |

## Structure
```
jarvis/
├── main.py              # entry point + wake word loop
├── config.json          # your settings (auto-generated)
├── requirements.txt
├── core/
│   ├── config.py        # config loading
│   ├── voice.py         # ears (speech-to-text) + mouth (text-to-speech)
│   ├── brain.py         # LLM integration (Claude/GPT/OpenRouter)
│   └── memory.py        # long-term memory (JSON)
└── skills/
    ├── dispatcher.py    # routes commands to skills
    ├── pc_control.py    # apps, screenshots, volume, web
    ├── info.py          # time, date, weather
    └── tools.py         # reminders, system status
```

## Extending
Add new skills in `skills/`, then wire them up in `dispatcher.py`. Local skills run instantly with no API cost.

## New in v1.1
- **Holographic UI** — run `python main.py --ui` then it opens at localhost:8765. Reactive orb (changes color: idle/listening/thinking/speaking), live system stats, type commands directly in the HUD.
- **Text mode** — `python main.py --text` to test without a mic.
- **File management** — "find file report", "organize downloads", "biggest files"
- **Browser automation** — "research quantum computing", "read page example.com", "capture page github.com" (needs: `pip install playwright && playwright install chromium`)

## Safety notes
- File organize only MOVES files, never deletes, never overwrites
- Browser automation never fills logins or makes purchases
- File search is limited to Desktop/Documents/Downloads/Pictures
