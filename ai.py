import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

MODEL_NAME = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
SYSTEM_MESSAGE = {
    "role": "system",
    "content": (
        "You are Jarvis, a helpful desktop voice assistant. "
        "Answer clearly and concisely because your responses may be spoken aloud. "
        "Do not claim that you performed computer actions unless the application did so."
    ),
}

conversation = [SYSTEM_MESSAGE]

_api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=_api_key, timeout=20.0) if _api_key else None


def aiprocess(command):
    """Send a user command to Groq and keep a bounded conversation history."""
    if client is None:
        return (
            "The Groq API key is missing. Add GROQ_API_KEY to your .env file "
            "and restart Jarvis."
        )

    conversation.append({"role": "user", "content": command})

    try:
        result = client.chat.completions.create(
            messages=conversation,
            model=MODEL_NAME,
            temperature=0.5,
            max_tokens=350,
        )

        response = result.choices[0].message.content
        response = response.strip() if response else "I couldn't generate a response."

        conversation.append({"role": "assistant", "content": response})

        # Keep the system message and the latest 10 conversation messages.
        # This limits request size while preserving some recent context.
        conversation[:] = [SYSTEM_MESSAGE] + conversation[-10:]
        return response

    except Exception as exc:
        print(f"Groq API error: {exc}")
        # Remove the user message that did not receive an assistant response.
        if conversation and conversation[-1].get("role") == "user":
            conversation.pop()
        return "Sorry, I couldn't reach the AI service. Please try again."


def reset_conversation():
    """Reset Jarvis's conversational context."""
    conversation[:] = [SYSTEM_MESSAGE]
