"""
Voice I/O
Ears  = speech recognition (Google's free recognizer via speech_recognition)
Mouth = text-to-speech (pyttsx3 — offline, uses Windows voices)
"""
import speech_recognition as sr
import pyttsx3


class Ears:
    def __init__(self, config):
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True

    def listen(self, timeout=8, quiet=False) -> str | None:
        """Listen for one phrase and return transcribed text."""
        try:
            with sr.Microphone() as source:
                if not quiet:
                    print("[listening...]")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.3)
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=12)
            text = self.recognizer.recognize_google(audio)
            return text
        except sr.WaitTimeoutError:
            return None
        except sr.UnknownValueError:
            return None
        except sr.RequestError as e:
            print(f"[ears] recognition service error: {e}")
            return None


class Mouth:
    def __init__(self, config):
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", config.get("voice_rate", 180))
        voices = self.engine.getProperty("voices")
        idx = config.get("voice_index", 0)
        if voices and idx < len(voices):
            self.engine.setProperty("voice", voices[idx].id)

    def say(self, text: str):
        print(f"[JARVIS speaks] {text}")
        self.engine.say(text)
        self.engine.runAndWait()
