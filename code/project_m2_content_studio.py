"""
Module 2 Checkpoint 1 Project: AI Content Studio
A content studio for FK Shopify Studio, a Shopify development service in Lahore.
It writes service descriptions, streams social posts in different tones,
answers prices from real data, and chats with customers using memory.
"""

from langchain.chat_models import init_chat_model

config = {
    "model": "gemma4:31b-cloud",
    "max_messages": 8,
    "precise_temperature": 0.2,
    "creative_temperature": 0.8,
    "cloud_price_per_1k": 0.01,  # example USD price, for the cost bonus
}

facts = {
    "name": "FK Shopify Studio",
    "city": "Lahore",
    "services": "Shopify store setup, theme customization, custom sections, speed optimization",
    "hours": "Monday to Saturday, 10 am to 7 pm",
    "delivery": "Small tasks in 2-3 days, full stores in 2-3 weeks",
    "contact": "faizankhaliddev.com",
    "prices": {
        "store setup": 85000,
        "theme customization": 55000,
        "custom section": 15000,
        "speed optimization": 40000,
        "headless store": 0,
    },
}

tones = {
    "friendly": "warm and simple, like talking to a small shop owner",
    "professional": "confident and clear, focused on results",
    "urgent": "short and punchy, limited-time feeling",
}

# why: answers about prices need accuracy, but marketing text needs variety, so each job gets its own model
precise = init_chat_model(config["model"], model_provider="ollama", temperature=config["precise_temperature"])
creative = init_chat_model(config["model"], model_provider="ollama", temperature=config["creative_temperature"])

price_lines = ""
for item, price in facts["prices"].items():
    if price == 0:
        price_lines += f"- {item}: coming soon\n"
    else:
        price_lines += f"- {item}: {price:,} PKR\n"

# why: the owner's main fear is invented prices, so the AI gets the real facts and is told to use nothing else
system_message = (
    f"You are the customer assistant for {facts['name']} in {facts['city']}.\n"
    f"Services: {facts['services']}\n"
    f"Hours: {facts['hours']}\n"
    f"Delivery time: {facts['delivery']}\n"
    f"Contact: {facts['contact']}\n"
    f"Prices:\n{price_lines}"
    "Only use these facts. If the answer is not in these facts, say you don't know "
    "and suggest contacting us. Answer in 2 short sentences."
)

messages = [{"role": "system", "content": system_message}]

# why: counters start at 0 before the loop so they add up across the whole session
chat_count = 0
menu_count = 0
post_count = 0
price_count = 0
total_tokens = 0
total_seconds = 0

print("=" * 50)
print(f"   {facts['name']} AI Content Studio")
print("=" * 50)
print("Commands: /menu, /post friendly|professional|urgent, /price <item>, /reset, bye")

while True:
    user_input = input("You: ").strip()
    command = user_input.lower()

    if not user_input:
        continue

    if command == "bye":
        print("Studio: Goodbye!")
        break

    elif command == "/reset":
        # why: wiping the whole list would lose the facts and rules, so keep messages[0]
        messages = [messages[0]]
        print("Studio: Chat memory cleared.")

    elif command.startswith("/price"):
        item = command[len("/price"):].strip()
        if not item:
            print("Studio: Use it like this: /price custom section")
            continue
        # why: prices are fixed data, so the dictionary answers instantly and spends zero tokens
        price = facts["prices"].get(item)
        price_count += 1
        if price is None:
            print(f"Studio: Sorry, {item} is not on our menu.")
        elif price == 0:
            print(f"Studio: {item.title()} is coming soon.")
        else:
            print(f"Studio: {item.title()} costs {price:,} PKR.")

    elif command == "/menu":
        results = []
        menu_tokens = 0
        for item, price in facts["prices"].items():
            if price == 0:
                # why: skipping before the AI call means unreleased services cost nothing
                print(f"Studio: Skipping {item} (coming soon)")
                continue
            response = creative.invoke([
                {"role": "system", "content": f"You write menu descriptions for {facts['name']}. Reply with one short, catchy sentence only."},
                {"role": "user", "content": f"Describe this service: {item}"},
            ])
            results.append({"item": item, "price": price, "text": response.text.strip()})
            menu_tokens += response.usage_metadata["total_tokens"]
            total_seconds += response.response_metadata["total_duration"] / 1_000_000_000
            menu_count += 1

        total_tokens += menu_tokens
        print("-" * 50)
        for number, row in enumerate(results, start=1):
            print(f"{number}. {row['item'].title()} ({row['price']:,} PKR)")
            print(f"   {row['text']}")
        print("-" * 50)

        # bonus: what this run would cost on a paid cloud model
        cost = menu_tokens / 1000 * config["cloud_price_per_1k"]
        print(f"Studio: On a cloud model, {menu_tokens:,} tokens would cost about ${cost:.2f}")

    elif command.startswith("/post"):
        tone_name = command[len("/post"):].strip()
        tone = tones.get(tone_name, tones["friendly"])
        print(f"Studio ({tone}):")

        post_text = ""
        for chunk in creative.stream([
            {"role": "system", "content": f"You write short Instagram posts for {facts['name']}, {facts['city']}. "
                                          f"Tone: {tone}. Only use these prices:\n{price_lines}"
                                          "Keep it under 4 lines."},
            {"role": "user", "content": "Write a post promoting one of our services."},
        ]):
            print(chunk.text, end="", flush=True)
            post_text += chunk.text
            # why: token counts and time only arrive on the last chunk, so check every chunk for them
            if chunk.usage_metadata:
                total_tokens += chunk.usage_metadata["total_tokens"]
            if "total_duration" in chunk.response_metadata:
                total_seconds += chunk.response_metadata["total_duration"] / 1_000_000_000
        print()
        post_count += 1

        # bonus: Roman Urdu version, using the precise model and the English post
        urdu = precise.invoke([
            {"role": "system", "content": "Translate this post into Roman Urdu (Urdu written in English letters). Reply with the translation only."},
            {"role": "user", "content": post_text},
        ])
        print("Roman Urdu:")
        print(urdu.text)
        total_tokens += urdu.usage_metadata["total_tokens"]
        total_seconds += urdu.response_metadata["total_duration"] / 1_000_000_000

    else:
        messages.append({"role": "user", "content": user_input})
        # why: trimming before the call keeps the cost capped while messages[0] keeps the rules
        messages = [messages[0]] + messages[1:][-config["max_messages"]:]
        response = precise.invoke(messages)
        messages.append({"role": "assistant", "content": response.text})

        chat_count += 1
        total_tokens += response.usage_metadata["total_tokens"]
        total_seconds += response.response_metadata["total_duration"] / 1_000_000_000

        print(f"Studio: {response.text}")
        print(f"        (memory: {len(messages)} messages, {response.usage_metadata['input_tokens']} tokens sent)")

print("=" * 50)
print("Session report")
print(f"Chat answers: {chat_count} | Menu descriptions: {menu_count} | Posts: {post_count} | Price answers: {price_count}")
print(f"AI usage: {total_tokens:,} tokens in {total_seconds:.1f} seconds")
print("=" * 50)