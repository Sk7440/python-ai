"""
Sweet Crumbs Saved Bot (Task 2.6)

A customer chatbot for Sweet Crumbs bakery. The owner edits prices and
details in faq.json without touching the code, the chat is saved to
chat_history.json so the bot remembers customers between runs, and any
problem shows a friendly message instead of a red error.

Run from the code folder:  uv run lesson_2_6_saved_bot.py
"""

import json
import sys
from datetime import datetime

import httpx
import ollama
from langchain.chat_models import init_chat_model

FAQ_FILE = "faq.json"
HISTORY_FILE = "chat_history.json"
ERROR_LOG = "errors.log"
MAX_MESSAGES = 10


def load_facts(path: str) -> dict:
    """Read the owner's facts from a JSON file, or stop with a clear message."""
    try:
        with open(path, encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Cannot start: {path} is missing. Run this from the code folder.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Cannot start: {path} has a typo in it. Check the commas and quotes.")
        sys.exit(1)


def build_system_message(facts: dict) -> str:
    """Turn the facts into the bot's rules."""
    price_lines = ""
    for item, price in facts.get("prices", {}).items():
        if price == 0:
            price_lines += f"- {item}: coming soon, not available yet\n"
        else:
            price_lines += f"- {item}: {price:,} PKR\n"

    return (
        f"You are the customer assistant for {facts.get('name', 'our bakery')} "
        f"in {facts.get('city', 'Lahore')}.\n"
        f"Hours: {facts.get('hours', 'unknown')}\n"
        f"Phone: {facts.get('phone', 'unknown')}\n"
        f"Delivery: {facts.get('delivery', 'unknown')}\n"
        f"Payment: {facts.get('payment', 'unknown')}\n"
        f"Prices:\n{price_lines}"
        "Only use these facts. If the answer is not here, say you don't know "
        "and ask the customer to call us. Never make up a price. Keep answers short."
    )


def load_history(path: str) -> list:
    """Load the old chat, or start fresh if the file is missing or damaged."""
    try:
        with open(path, encoding="utf-8") as file:
            history = json.load(file)
    except FileNotFoundError:
        # First run: there is no history yet, and that's normal, so no message.
        return []
    except json.JSONDecodeError:
        print("History file was damaged. Starting a fresh chat.")
        return []

    # Valid JSON can still be the wrong shape (a classmate could type {} or [1, 2]),
    # and a bad message would crash the AI call later, so check every one now.
    if not isinstance(history, list):
        print("History file was damaged. Starting a fresh chat.")
        return []
    for message in history:
        if not isinstance(message, dict) or message.get("role") not in ("user", "assistant"):
            print("History file was damaged. Starting a fresh chat.")
            return []

    if history:
        print(f"Loaded {len(history)} old messages.")
    return history


def save_history(history: list) -> None:
    """Save the chat so it is still there next time."""
    with open(HISTORY_FILE, "w", encoding="utf-8") as file:
        # ensure_ascii=False keeps Urdu readable in the file instead of ا codes.
        json.dump(history, file, indent=2, ensure_ascii=False)


def log_error(error: Exception) -> None:
    """Write the real error to errors.log for me, while the customer sees a friendly message."""
    with open(ERROR_LOG, "a", encoding="utf-8") as file:
        file.write(f"{datetime.now():%Y-%m-%d %H:%M:%S} {type(error).__name__}: {error}\n")


facts = load_facts(FAQ_FILE)
system_message = build_system_message(facts)
llm = init_chat_model("llama3.2", model_provider="ollama", temperature=0.2)
history = load_history(HISTORY_FILE)

name = facts.get("name", "Our")
print(f"{name} Bot: Ask me anything. Commands: /reset, /export, bye")

while True:
    user_text = input("You: ").strip()

    if user_text == "":
        continue

    command = user_text.lower()

    if command == "bye":
        print("Bot: Goodbye! Your chat is saved.")
        break

    if command == "/reset":
        history = []
        save_history(history)
        print("Bot: Chat cleared. Let's start fresh.")
        continue

    if command == "/export":
        with open("transcript.txt", "w", encoding="utf-8") as file:
            for message in history:
                file.write(f"{message['role']}: {message['content']}\n")
        print(f"Bot: Saved {len(history)} messages to transcript.txt")
        continue

    history.append({"role": "user", "content": user_text})

    # The system message is added fresh every turn instead of being saved in the history,
    # so a price changed in faq.json is used straight away, even in an old chat.
    messages = [{"role": "system", "content": system_message}] + history[-MAX_MESSAGES:]

    try:
        response = llm.invoke(messages)
    except (httpx.ConnectError, ConnectionError) as error:
        # Newer versions of the ollama library turn httpx.ConnectError into
        # Python's ConnectionError, so catch both to cover either version.
        log_error(error)
        history.pop()
        print("Bot: I am offline right now. Please open the Ollama app and try again.")
        continue
    except ollama.ResponseError as error:
        log_error(error)
        # Remove the unanswered question, or the next turn would send two questions in a row.
        history.pop()
        print("Bot: Sorry, I can't answer right now. Please try again in a minute.")
        continue

    reply = response.text
    history.append({"role": "assistant", "content": reply})
    save_history(history)
    print(f"Bot: {reply}")