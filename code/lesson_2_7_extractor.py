"""
Sweet Crumbs Order Extractor (Task 2.7)

Turns messy WhatsApp orders (English and Roman Urdu) into clean, checked
order data. The AI only reads the message and pulls out the customer, the
address and the items. Python does every price and total, and flags anything
that looks wrong with CHECK so staff can look at it before baking.

Run from the code folder:  uv run lesson_2_7_extractor.py
Writes: orders.json and orders.csv (both in .gitignore, they hold customer data)
"""

import json

import httpx
from langchain.chat_models import init_chat_model

PRICES = {
    "chocolate cake": 1500,
    "cupcake": 250,
    "brownie": 300,
}

MESSAGES = [
    # 1. normal order
    "Assalam o alaikum, I want 1 chocolate cake for tomorrow. Sara, house 5 DHA Phase 6",
    # 2. two or more items
    "2 brownies and 3 cupcakes please. Name is Hamza, Johar Town block C",
    # 3. an item not on the menu
    "1 pizza and 2 brownies, Bilal, Model Town",
    # 4. not an order
    "hi do you deliver to Johar Town?",
    # 5. Roman Urdu
    "Salam! 2 cupcakes aur 1 chocolate cake chahiye. Ali, house 12 Gulberg",
    # 6. no name given, to catch the AI inventing one
    "3 brownies bhej dein, Faisal Town",
]

ORDER_SCHEMA = {
    "type": "object",
    "properties": {
        "is_order": {"type": "boolean"},
        "customer": {"type": "string"},
        "address": {"type": "string"},
        "items": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "item": {"type": "string"},
                    "quantity": {"type": "integer"},
                },
                "required": ["item", "quantity"],
            },
        },
    },
    "required": ["is_order", "customer", "address", "items"],
}

SYSTEM_MESSAGE = (
    "You read WhatsApp messages sent to a bakery and extract the order.\n"
    f"Menu items: {', '.join(PRICES)}.\n"
    "Rules:\n"
    "- is_order is true only if the customer asks to buy something.\n"
    "- Use the singular menu name when an item matches the menu (cupcakes -> cupcake).\n"
    "- Copy items that are not on the menu exactly as the customer wrote them.\n"
    "- customer is the name written in the message. If there is no name, use an empty string.\n"
    "- address is the address written in the message, or an empty string.\n"
    "- Never invent a name, address, item or quantity."
)

# format= forces the reply into our schema, and temperature 0 gives the same
# extraction every time, which is what you want for data, not creativity.
extractor = init_chat_model(
    "llama3.2", model_provider="ollama", temperature=0, format=ORDER_SCHEMA
)


def menu_name(raw_item: str) -> str:
    """Clean an item name so 'Brownies ' matches 'brownie' on the menu."""
    item = raw_item.lower().strip()
    if item not in PRICES and item.endswith("s") and item[:-1] in PRICES:
        item = item[:-1]
    return item


def check_order(message: str, data: dict) -> tuple[dict, list[str]]:
    """Price the items in Python and list everything that needs a human check.

    Args:
        message: The customer's original message.
        data: The order the AI extracted.
    """
    checks = []
    lines = []

    for entry in data.get("items", []):
        if not isinstance(entry, dict):
            checks.append(f"strange item in the AI reply: {entry!r}")
            continue
        item = menu_name(str(entry.get("item", "")))
        quantity = entry.get("quantity", 0)

        # Never trust the AI with money: off-menu items are flagged, never priced.
        if item not in PRICES:
            checks.append(f"'{item}' is not on the menu")
            continue
        if not isinstance(quantity, int) or quantity < 1:
            checks.append(f"quantity {quantity!r} for {item} looks wrong")
            continue

        lines.append({"item": item, "quantity": quantity, "line_total": quantity * PRICES[item]})

    customer = str(data.get("customer", "")).strip()
    # The AI sometimes fills an empty name with a made-up one, so the name
    # must actually appear in the customer's own message.
    if customer == "":
        checks.append("no customer name in the message")
    elif customer.lower() not in message.lower():
        checks.append(f"customer '{customer}' is not in the message (the AI may have invented it)")

    total = 0
    for line in lines:
        total += line["line_total"]

    order = {
        "customer": customer,
        "address": str(data.get("address", "")).strip(),
        "items": lines,
        "total": total,
        "message": message,
    }
    return order, checks


orders = []
all_checks = []
total_value = 0
offline = False

for number, message in enumerate(MESSAGES, start=1):
    print(f"Message: {message}")

    try:
        response = extractor.invoke([
            {"role": "system", "content": SYSTEM_MESSAGE},
            {"role": "user", "content": message},
        ])
    except (httpx.ConnectError, ConnectionError):
        print("  Cannot reach Ollama. Open the Ollama app and run this again.\n")
        offline = True
        break

    try:
        data = json.loads(response.text)
    except json.JSONDecodeError:
        print("  CHECK: the AI reply was not valid JSON, needs a human\n")
        all_checks.append(f"message {number}: the AI reply was not valid JSON")
        continue

    if not isinstance(data, dict) or not data.get("is_order", False):
        print("  Not an order: needs a human reply.\n")
        continue

    order, checks = check_order(message, data)

    for line in order["items"]:
        print(f"  {line['quantity']} x {line['item']} = {line['line_total']:,} PKR")
    print(f"  Customer: {order['customer'] or '(none)'}, Address: {order['address'] or '(none)'}")

    if order["items"]:
        print(f"  Total: {order['total']:,} PKR")
        orders.append(order)
        total_value += order["total"]
    else:
        print("  Nothing from our menu: needs a human reply.")

    for check in checks:
        print(f"  CHECK: {check}")
        all_checks.append(f"message {number}: {check}")
    print()

print("=" * 50)
print(f"Orders found: {len(orders)} | Total value: {total_value:,} PKR | Checks: {len(all_checks)}")
for check in all_checks:
    print(f"  CHECK {check}")

# Don't overwrite yesterday's good orders file with an empty one just because Ollama was closed.
if offline:
    print("Stopped early, so orders.json and orders.csv were not changed.")
    raise SystemExit(1)

with open("orders.json", "w", encoding="utf-8") as file:
    json.dump(orders, file, indent=2, ensure_ascii=False)
print(f"Saved {len(orders)} orders to orders.json")

with open("orders.csv", "w", encoding="utf-8") as file:
    file.write("customer,item,quantity,line_total\n")
    for order in orders:
        for line in order["items"]:
            file.write(f"{order['customer']},{line['item']},{line['quantity']},{line['line_total']}\n")
print("Saved orders.csv (open it in Excel or Google Sheets)")