"""
Sweet Crumbs AI Toolkit (Task 2.5)

Reusable AI skills for Sweet Crumbs, a bakery in Lahore. Staff can summarize
long customer messages, translate text for customers, and reply to reviews,
and every skill uses the same tested prompt every time.

Run from the code folder:  uv run lesson_2_5_ai_skills.py
"""

from langchain.chat_models import init_chat_model

# Create both models once here, so every skill reuses them instead of
# connecting to Ollama again on every call.
precise = init_chat_model("gemma4:31b-cloud", model_provider="ollama", temperature=0.1)
creative = init_chat_model("gemma4:31b-cloud", model_provider="ollama", temperature=0.8)

BUSINESS = "Sweet Crumbs, a home bakery in Lahore"


def ask_ai(prompt: str, system: str = "You are a helpful assistant.", creative_mode: bool = False) -> str:
    """Send one prompt to the AI and return its answer as text.

    Args:
        prompt: What we want the AI to do.
        system: The rules the AI should follow.
        creative_mode: True for varied marketing text, False for exact answers.
    """
    llm = creative if creative_mode else precise
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": prompt},
    ]
    response = llm.invoke(messages)
    return response.text


def summarize(text: str) -> str:
    """Summarize a long customer message in one or two sentences."""
    system = f"You work at {BUSINESS}. Summarize messages for busy staff. Keep names, items and dates."
    return ask_ai(f"Summarize this in 1-2 sentences:\n{text}", system=system)


def translate(text: str, language: str = "Urdu") -> str:
    """Translate text into another language. Urdu is the default because most customers use it."""
    system = "You are a translator. Reply with the translation only, no notes."
    return ask_ai(f"Translate into {language}:\n{text}", system=system)


def reply_to_review(review: str) -> str:
    """Write a short, polite reply to a customer review."""
    system = (
        f"You reply to reviews for {BUSINESS}. Be warm and short (2 sentences). "
        "Thank the customer, and apologise for any problem they mention. Never promise discounts."
    )
    # Creative mode, because the same reply to every review would look copy-pasted.
    return ask_ai(f"Customer review: {review}", system=system, creative_mode=True)


def estimate_tokens(text: str) -> int:
    """Roughly estimate tokens: about 1.3 tokens per English word. No AI needed."""
    return round(len(text.split()) * 1.3)


# Test the non-AI function first: if the maths is wrong, there's no point starting the menu.
assert estimate_tokens("") == 0
assert estimate_tokens("hello world") == 3
assert estimate_tokens("Cake was great but delivery was late.") == 9

usage = {"summarize": 0, "translate": 0, "reply": 0}

print("Sweet Crumbs AI Toolkit. Commands: /summarize, /translate, /reply, /batch, bye")

while True:
    command = input("Command: ").strip().lower()

    if command == "":
        continue

    if command == "bye":
        break

    elif command == "/summarize":
        text = input("Text to summarize: ").strip()
        print("AI:", summarize(text))
        usage["summarize"] += 1

    elif command == "/translate":
        text = input("Text to translate: ").strip()
        language = input("Language (Enter for Urdu): ").strip()
        # Only pass a language if the user typed one, so the default stays in one place: the function.
        if language:
            result = translate(text, language)
        else:
            result = translate(text)
        print("AI:", result)
        usage["translate"] += 1

    elif command == "/reply":
        review = input("Customer review: ").strip()
        print("AI:", reply_to_review(review))
        print(f"    (review was about {estimate_tokens(review)} tokens)")
        usage["reply"] += 1

    elif command == "/batch":
        reviews = [
            "Best brownies in Lahore, my kids loved them!",
            "Cupcakes were dry and the box was crushed.",
            "Good cake but a bit expensive for the size.",
        ]
        for number, review in enumerate(reviews, start=1):
            print(f"{number}. {review}")
            print("   AI:", reply_to_review(review))
            # Each batch item is a real use of the reply skill, so it counts.
            usage["reply"] += 1

    else:
        print("Unknown command. Try /summarize, /translate, /reply, /batch or bye.")

print("Skills used today:")
for skill, count in usage.items():
    print(f"  {skill}: {count}")