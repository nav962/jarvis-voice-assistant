# Jarvis — Python Voice Assistant

A beginner-friendly desktop voice assistant with speech recognition, text-to-speech, browser shortcuts, web search, news, weather, date/time, music shortcuts, and Groq-powered AI responses.

## Features

- Wake words: `Jarvis` or `Hello`
- Open Google, YouTube, WhatsApp, Facebook, and CampX
- Search the web
- Play song searches from `musiclibrary.py`
- Read business headlines from India using NewsAPI
- Read current weather for Hyderabad using Open-Meteo
- Tell date and time
- Answer other questions using Groq
- Reset AI conversation history
- Exit command
- Timeouts and error handling for microphone and HTTP requests
- API keys stored in environment variables

## Setup

1. Install Python 3.10 or later.
2. Open a terminal in this folder.
3. Create a virtual environment:

   ```bash
   python -m venv .venv
   ```

4. Activate it on Windows:

   ```bash
   .venv\Scripts\activate
   ```

5. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

   If PyAudio installation fails on Windows, use a compatible wheel for your Python version or follow the official PyAudio installation guidance.

6. Copy `.env.example` to `.env`.
7. Put your newly generated Groq key and NewsAPI key in `.env`.
8. Run:

   ```bash
   python main.py
   ```

## Example commands

Say the wake word first, then the command:

- "Jarvis, open YouTube"
- "Jarvis, search Python DSA"
- "Jarvis, play Believer"
- "Jarvis, tell me the news"
- "Jarvis, what is the weather?"
- "Jarvis, what time is it?"
- "Jarvis, what is recursion?"
- "Jarvis, reset conversation"
- "Jarvis, stop"

You can also say only "Jarvis"; it will then listen for a second command.

## Configuration

- `GROQ_API_KEY`: Groq API key
- `NEWS_API_KEY`: NewsAPI key
- `GROQ_MODEL`: Optional model override
- Weather is configured for Hyderabad in `commands.py`; change the coordinates and timezone for another city.
- Add music titles and URLs to `musiclibrary.py`.

## Security

- Never commit `.env` to GitHub.
- Rotate any API key that has been pasted into a public or shared location.
- API services may have rate limits or require a paid plan.
- SpeechRecognition's `recognize_google` uses an online service; it is not offline speech recognition.

## Current limitations

- Wake-word detection is implemented using speech recognition, not a dedicated always-on offline wake-word engine.
- The assistant only performs explicit actions listed in `commands.py`. Other requests are sent to the LLM, which does not have unrestricted computer control.
- Weather coordinates are fixed to Hyderabad.
