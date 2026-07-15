"""
J.A.R.V.I.S. — Personal AI Assistant
Run modes:
  python main.py          -> voice mode (wake word / push-to-talk)
  python main.py --ui     -> voice mode + holographic web UI at localhost:8765
  python main.py --text   -> text-only mode (no mic needed, good for testing)
"""
import sys
import time
import webbrowser

from core.config import load_config
from core.brain import Brain
from core.memory import Memory
from skills.dispatcher import SkillDispatcher


def handle_command(command, skills, brain):
    """One command in -> one response out. Used by voice, text, and UI."""
    result = skills.handle(command)
    if result is not None:
        return result
    return brain.think(command)


def main():
    config = load_config()
    use_ui = "--ui" in sys.argv
    text_mode = "--text" in sys.argv

    print("=" * 50)
    print("  J.A.R.V.I.S. — booting up...")
    print("=" * 50)

    memory = Memory(config["memory_file"])
    brain = Brain(config, memory)

    # Mouth: real TTS in voice mode, print-only in text mode
    if text_mode:
        class PrintMouth:
            def say(self, text): print(f"[JARVIS] {text}")
        mouth = PrintMouth()
    else:
        from core.voice import Mouth
        mouth = Mouth(config)

    skills = SkillDispatcher(config, mouth, brain)

    # Optional holographic UI
    if use_ui:
        from core import ui_server
        ui_server.COMMAND_HANDLER = lambda cmd: handle_command(cmd, skills, brain)
        ui_server.start_ui_server()
        webbrowser.open("http://localhost:8765")

    mouth.say("All systems online. At your service, sir.")

    # ---- TEXT MODE ----
    if text_mode:
        while True:
            try:
                command = input("\n[You] ").strip()
            except (KeyboardInterrupt, EOFError):
                break
            if not command:
                continue
            if command.lower() in ("exit", "quit", "shut down"):
                mouth.say("Powering down. Goodbye, sir.")
                break
            response = handle_command(command, skills, brain)
            mouth.say(response)
        return

    # ---- VOICE MODE ----
    from core.voice import Ears
    ears = Ears(config)
    wake_word = config["wake_word"].lower()
    push_to_talk = config.get("push_to_talk", False)

    if use_ui:
        from core import ui_server

    while True:
        try:
            if push_to_talk:
                input("\n[Press ENTER to talk]")
                if use_ui: ui_server.set_state(state="listening")
                command = ears.listen()
            else:
                heard = ears.listen(timeout=5, quiet=True)
                if not heard or wake_word not in heard.lower():
                    continue
                mouth.say("Yes?")
                if use_ui: ui_server.set_state(state="listening")
                command = ears.listen()

            if use_ui: ui_server.set_state(state="idle")
            if not command:
                continue

            print(f"\n[You] {command}")
            if use_ui: ui_server.set_state(state="thinking", transcript=command)

            if any(w in command.lower() for w in ["shut down", "goodbye jarvis", "exit"]):
                mouth.say("Powering down. Goodbye, sir.")
                break

            response = handle_command(command, skills, brain)
            print(f"[JARVIS] {response}")
            if use_ui: ui_server.set_state(state="speaking", transcript=response)
            mouth.say(response)
            if use_ui: ui_server.set_state(state="idle")

        except KeyboardInterrupt:
            print("\nShutting down...")
            break
        except Exception as e:
            print(f"[error] {e}")
            time.sleep(1)


if __name__ == "__main__":
    main()
