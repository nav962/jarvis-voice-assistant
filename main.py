import re
import speech_recognition as sr
import pyttsx3

from commands import process_command


WAKE_WORDS = ("jarvis", "hello")


def speak(engine, text):
    """Speak text safely and also print it for debugging."""
    text = str(text).strip()
    if not text:
        return

    print(f"Jarvis: {text}")
    try:
        engine.say(text)
        engine.runAndWait()
    except Exception as exc:
        print(f"Text-to-speech error: {exc}")


def extract_wake_command(text):
    """
    Returns (activated, command).
    Supports:
      'Jarvis'
      'Jarvis, what time is it?'
      'Hello, open YouTube'
    """
    cleaned = text.strip()
    match = re.match(
        r"^(?:hey\s+)?(jarvis|hello)\b[\s,.:;!?-]*(.*)$",
        cleaned,
        flags=re.IGNORECASE,
    )
    if not match:
        return False, ""

    return True, match.group(2).strip()


def listen_once(recognizer, engine, timeout=4, phrase_time_limit=6):
    """Listen once and return recognized text, or None on recoverable errors."""
    try:
        with sr.Microphone() as source:
            print("Listening...")
            audio = recognizer.listen(
                source,
                timeout=timeout,
                phrase_time_limit=phrase_time_limit,
            )

        text = recognizer.recognize_google(audio).strip()
        print(f"You: {text}")
        return text

    except sr.WaitTimeoutError:
        return None
    except sr.UnknownValueError:
        print("Speech was not clear enough to understand.")
        return None
    except sr.RequestError as exc:
        print(f"Speech recognition service error: {exc}")
        speak(engine, "Speech recognition is unavailable. Please check your internet connection.")
        return None
    except OSError as exc:
        print(f"Microphone error: {exc}")
        speak(engine, "I cannot access the microphone. Please check your microphone settings.")
        return None


def main():
    recognizer = sr.Recognizer()
    engine = pyttsx3.init()
    engine.setProperty("rate", 175)

    speak(engine, "Initializing Jarvis.")

    # Calibrate once to account for background noise.
    try:
        with sr.Microphone() as source:
            print("Calibrating microphone. Please stay quiet briefly...")
            recognizer.adjust_for_ambient_noise(source, duration=0.8)
    except OSError as exc:
        print(f"Microphone initialization failed: {exc}")
        speak(engine, "Microphone initialization failed.")
        return

    speak(engine, "Jarvis is ready. Say Jarvis followed by a command.")

    running = True
    while running:
        heard_text = listen_once(
            recognizer,
            engine,
            timeout=4,
            phrase_time_limit=5,
        )

        if not heard_text:
            continue

        activated, command = extract_wake_command(heard_text)
        if not activated:
            continue

        # If the user said only "Jarvis", ask for the command separately.
        if not command:
            speak(engine, "Yes, how can I help?")
            command = listen_once(
                recognizer,
                engine,
                timeout=5,
                phrase_time_limit=8,
            )

        if not command:
            continue

        running = process_command(command, engine)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nJarvis stopped by keyboard.")
