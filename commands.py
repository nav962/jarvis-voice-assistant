import os
import re
from datetime import datetime
from urllib.parse import quote_plus

import requests
import webbrowser as wb
from dotenv import load_dotenv

from ai import aiprocess, reset_conversation

load_dotenv()

NEWS_API_KEY = os.getenv("NEWS_API_KEY")

SITES = {
    "google": "https://www.google.com",
    "youtube": "https://www.youtube.com",
    "whatsapp": "https://web.whatsapp.com",
    "facebook": "https://www.facebook.com",
    "campx": "https://kgr.campx.in",
}

WEATHER_URL = "https://api.open-meteo.com/v1/forecast"


def speak(engine, message):
    message = str(message).strip()
    if not message:
        return
    print(f"Jarvis: {message}")
    try:
        engine.say(message)
        engine.runAndWait()
    except Exception as exc:
        print(f"Text-to-speech error: {exc}")


def open_site(site_name, engine):
    url = SITES.get(site_name.lower().strip())
    if not url:
        speak(
            engine,
            "I don't have that website shortcut. Try Google, YouTube, WhatsApp, Facebook, or CampX."
        )
        return

    try:
        wb.open(url)
        speak(engine, f"Opening {site_name}.")
    except Exception as exc:
        print(f"Browser error: {exc}")
        speak(engine, "I couldn't open the browser.")


def web_search(query, engine):
    query = query.strip()
    if not query:
        speak(engine, "Please tell me what you want to search for.")
        return

    url = "https://www.bing.com/search?q=" + quote_plus(query)
    try:
        wb.open(url)
        speak(engine, f"Searching the web for {query}.")
    except Exception as exc:
        print(f"Search/browser error: {exc}")
        speak(engine, "I couldn't open the search page.")


def play_song(song_name, engine):
    # Import here so the project can still start if the library needs fixing.
    try:
        import musiclibrary
        music = musiclibrary.music
    except (ImportError, AttributeError) as exc:
        print(f"Music library error: {exc}")
        speak(engine, "The music library is not configured correctly.")
        return

    key = song_name.strip().lower()
    link = music.get(key)

    if not link:
        speak(engine, f"I couldn't find {song_name} in your music library.")
        return

    try:
        wb.open(link)
        speak(engine, f"Playing {song_name}.")
    except Exception as exc:
        print(f"Music/browser error: {exc}")
        speak(engine, "I couldn't open that music link.")


def tell_news(engine):
    if not NEWS_API_KEY:
        speak(engine, "The News API key is missing. Add NEWS_API_KEY to your .env file.")
        return

    try:
        response = requests.get(
            "https://newsapi.org/v2/top-headlines",
            params={
                "country": "in",
                "category": "business",
                "pageSize": 5,
                "apiKey": NEWS_API_KEY,
            },
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()

        if data.get("status") != "ok":
            speak(engine, "The news service returned an error.")
            print("News API response:", data)
            return

        articles = data.get("articles", [])
        titles = [
            article.get("title")
            for article in articles
            if article.get("title")
        ]

        if not titles:
            speak(engine, "No news headlines are available right now.")
            return

        print("\nToday's business headlines:")
        for index, title in enumerate(titles, start=1):
            print(f"{index}. {title}")

        # Speak one headline at a time to keep pauses natural.
        speak(engine, "Here are the latest business headlines from India.")
        for index, title in enumerate(titles, start=1):
            speak(engine, f"Headline {index}. {title}")

    except requests.Timeout:
        speak(engine, "The news request timed out. Please try again.")
    except requests.RequestException as exc:
        print(f"News request error: {exc}")
        speak(engine, "I couldn't fetch the news. Please check your internet connection.")
    except (ValueError, TypeError) as exc:
        print(f"News response parsing error: {exc}")
        speak(engine, "I couldn't read the news response.")


def tell_weather(engine):
    # Default coordinates are Hyderabad. Change them to your preferred city.
    try:
        response = requests.get(
            WEATHER_URL,
            params={
                "latitude": 17.3850,
                "longitude": 78.4867,
                "current": "temperature_2m,relative_humidity_2m,apparent_temperature",
                "timezone": "Asia/Kolkata",
            },
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
        current = data.get("current", {})

        temperature = current.get("temperature_2m")
        feels_like = current.get("apparent_temperature")
        humidity = current.get("relative_humidity_2m")

        if temperature is None:
            speak(engine, "Weather information is not available right now.")
            return

        message = f"In Hyderabad, the temperature is {temperature} degrees Celsius"
        if feels_like is not None:
            message += f", and it feels like {feels_like} degrees"
        if humidity is not None:
            message += f", with {humidity} percent relative humidity"
        speak(engine, message + ".")

    except requests.Timeout:
        speak(engine, "The weather request timed out. Please try again.")
    except requests.RequestException as exc:
        print(f"Weather request error: {exc}")
        speak(engine, "I couldn't fetch the weather. Please check your internet connection.")
    except (ValueError, TypeError) as exc:
        print(f"Weather response parsing error: {exc}")
        speak(engine, "I couldn't read the weather response.")


def get_date(engine):
    today = datetime.now().strftime("%A, %d %B %Y")
    speak(engine, f"Today is {today}.")


def get_time(engine):
    now = datetime.now().strftime("%I:%M %p")
    speak(engine, f"The time is {now}.")


def process_command(command, engine):
    """
    Handle supported commands.
    Returns False only when the user asks Jarvis to exit.
    """
    original = command.strip()
    normalized = re.sub(r"\s+", " ", original.lower()).strip()
    normalized = re.sub(r"[.!?]+$", "", normalized).strip()

    if not normalized:
        speak(engine, "I didn't hear a command.")
        return True

    # Exit / shutdown commands
    if normalized in {"exit", "quit", "stop", "shutdown", "goodbye", "stop jarvis", "exit jarvis"}:
        speak(engine, "Goodbye.")
        return False

    # Reset the LLM conversation
    if normalized in {"reset conversation", "clear conversation", "start new conversation"}:
        reset_conversation()
        speak(engine, "I've cleared our AI conversation history.")
        return True

    # Date and time
    if normalized in {"date", "today's date", "what is the date", "what's the date", "what is today's date"}:
        get_date(engine)
        return True

    if normalized in {"time", "what time is it", "tell me the time", "what is the time"}:
        get_time(engine)
        return True

    # Weather and news
    if normalized in {"weather", "check weather", "what is the weather", "what's the weather", "weather in hyderabad"}:
        tell_weather(engine)
        return True

    if normalized in {"news", "latest news", "business news", "read the news", "tell me the news"}:
        tell_news(engine)
        return True

    # Browser shortcuts: open google / open YouTube / etc.
    if normalized.startswith("open "):
        site = normalized[5:].strip()
        # Permit a few natural variants without opening arbitrary URLs.
        site = re.sub(r"\s+(please|for me)$", "", site)
        open_site(site, engine)
        return True

    # Search: search python tutorials / search for Python tutorials
    if normalized.startswith("search for "):
        web_search(original[11:].strip(), engine)
        return True
    if normalized.startswith("search "):
        web_search(original[7:].strip(), engine)
        return True

    # Play a song title; supports multiple words.
    if normalized.startswith("play "):
        song = original[5:].strip()
        play_song(song, engine)
        return True

    # Natural-language variants for common commands
    if "weather" in normalized and ("what" in normalized or "check" in normalized):
        tell_weather(engine)
        return True
    if "news" in normalized and any(word in normalized for word in ("latest", "read", "tell", "business")):
        tell_news(engine)
        return True
    if "time" in normalized and any(word in normalized for word in ("what", "tell", "current")):
        get_time(engine)
        return True
    if "date" in normalized and any(word in normalized for word in ("what", "today", "tell")):
        get_date(engine)
        return True

    # Unrecognized commands go to the AI assistant.
    answer = aiprocess(original)
    speak(engine, answer)
    return True
