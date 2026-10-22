"""
Task 2.3:  Bot with Real Facts
A customer assistant for my Shopify development service. It answers
only from the facts dictionary, can switch personality with /persona,
and answers /price straight from the dictionary without calling the AI.
"""

from langchain.chat_models import init_chat_model

config = {
    "model": "gemma4:31b-cloud",
    "temperature": 0.3,
    "memory_size": 8,
}

facts = {
    "name": "FK Shopify Studio",
    "location": "Lahore, Pakistan (works with clients worldwide)",
    "services": "Shopify store setup, theme customization, custom sections, speed optimization",
    "hours": "Monday to Saturday, 10am to 7pm PKT",
    "delivery": "Small tasks in 2-3 days, full stores in 2-3 weeks",
    "contact": "sultankhaliddev.com",
    "prices": {
        "store setup": 300,
        "theme customization": 200,
        "custom section": 50,
        "speed optimization": 150,
    },
}

personas = {
    "friendly": "warm and cheerful, uses simple words",
    "formal": "polite and professional, short clear sentences",
    "sales": "excited, always suggests one extra service to buy",
}


def build_system_message(style):
    price_lines = "\n".join(
        f"- {item}: ${price}" for item, price in facts["prices"].items()
    )
    return (
        f"You are the customer assistant for {facts['name']}.\n"
        f"Style: {style}.\n"
        f"Location: {facts['location']}\n"
        f"Services: {facts['services']}\n"
        f"Hours: {facts['hours']}\n"
        f"Delivery: {facts['delivery']}\n"
        f"Contact: {facts['contact']}\n"
        f"Prices (USD):\n{price_lines}\n"
        "Only use these facts. If something is not listed, say you don't know "
        "and suggest contacting us. Answer in 2 short sentences."
    )


llm = init_chat_model(
    config["model"], model_provider="ollama", temperature=config["temperature"]
)

current_style = personas["friendly"]
messages = [{"role": "system", "content": build_system_message(current_style)}]

print("Bot ready. Commands: /persona friendly|formal|sales, /price <item>, /add <item> <price>, bye")

while True:
    user_input = input("You: ").strip()

    if not user_input:
        continue

    if user_input.lower() == "bye":
        print("Bot: Goodbye!")
        break

    if user_input.lower().startswith("/persona"):
        name = user_input[len("/persona"):].strip().lower()
        current_style = personas.get(name, personas["friendly"])
        messages[0]["content"] = build_system_message(current_style)
        print(f"Bot: Style changed to: {current_style}")
        continue

    if user_input.lower().startswith("/price"):
        item = user_input[len("/price"):].strip()
        price = facts["prices"].get(item.lower())
        if price is None:
            print(f"Bot: Sorry, {item} is not on our menu.")
        else:
            print(f"Bot: {item} costs ${price}.")
        continue

    if user_input.lower().startswith("/add"):
        parts = user_input[len("/add"):].strip().rsplit(" ", 1)
        if len(parts) != 2 or not parts[1].isdigit():
            print("Bot: Use it like this: /add logo design 80")
            continue
        item, price = parts[0].lower(), int(parts[1])
        facts["prices"][item] = price
        messages[0]["content"] = build_system_message(current_style)
        print(f"Bot: Added {item} at ${price}.")
        continue

    messages.append({"role": "user", "content": user_input})
    response = llm.invoke(messages)
    messages.append({"role": "assistant", "content": response.text})

    messages = [messages[0]] + messages[1:][-config["memory_size"]:]

    print(f"Bot: {response.text}")