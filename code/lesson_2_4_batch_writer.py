"""Task 2.4: Batch Product Writer
Write sentence description for every service in my price list
in a single run, skips anything without a price, and reports the
total tokens and seconds spent.
"""

from langchain.chat_models import init_chat_model

products = {
    "Store Setup": 300,
    "Theme Customization": 200,
    "Custom Section": 50,
    "Speed Optimization": 150,
    "Logo Design": 0,
    "App Replacement": 120,
}

llm = init_chat_model("gemma4:31b-cloud", model_provider="ollama", temperature=0.7)

results = []
total_tokens = 0
total_seconds = 0

for name, price in products.items():
    if price == 0:
        print(f"Skipping {name} (no price)")
        continue

    response = llm.invoke([
        {
            "role": "system",
            "content": "You write menu descriptions for a Shopify development studio. "
                       "Reply with exactly one short, catchy sentence and nothing else.",
        },
        {"role": "user", "content": f"Describe this service: {name}"},
    ])

    results.append({"item": name, "price": price, "text": response.text.strip()})
    total_tokens += response.usage_metadata["total_tokens"]
    total_seconds += response.response_metadata["total_duration"] / 1_000_000_000

print("=" * 50)
for number, row in enumerate(results, start=1):
    print(f"{number}. {row['item']} (${row['price']})")
    print(f"   {row['text']}")
print("=" * 50)
print(f"{len(results)} descriptions, {total_tokens} tokens, {total_seconds:.1f} seconds")