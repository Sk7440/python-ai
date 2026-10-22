"""
Sweet Crumbs AI Business Assistant (Module 2 Final)

An AI agent for Sweet Crumbs, a home bakery in Lahore. It answers from the
owner's business.json, uses tools to look up prices and shop info, check and
cancel orders, and place new ones. It also turns pasted WhatsApp messages into
checked orders. Every order needs the owner's "yes" before it is saved, all
money is calculated in Python, and the chat and orders survive restarts.

Run:  cd code  then  uv run project_m2_business_assistant.py
Files it writes (all in .gitignore): orders.json, transcript.json, errors.log
"""

import json
import sys
from datetime import datetime

import httpx
import ollama
from langchain.chat_models import init_chat_model
from langchain.tools import tool
from pydantic import ValidationError

MODEL = "llama3.2"
BUSINESS_FILE = "business.json"
ORDERS_FILE = "orders.json"
TRANSCRIPT_FILE = "transcript.json"
ERROR_LOG = "errors.log"
MAX_STEPS = 5
MEMORY_SIZE = 8
LINE = "=" * 60

# Newer versions of the ollama library turn httpx.ConnectError into Python's
# ConnectionError, so all three are caught everywhere the AI is called.
AI_ERRORS = (httpx.ConnectError, ConnectionError, ollama.ResponseError)

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


# ---------------------------------------------------------------- helpers

def load_business(path: str) -> dict:
    """Load the owner's business file, or stop with a clear message."""
    try:
        with open(path, encoding="utf-8") as file:
            business = json.load(file)
    except FileNotFoundError:
        print(f"Cannot start: {path} is missing. Create it in the code folder and run from there.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Cannot start: {path} has a typo in it. Check the commas and quotes.")
        sys.exit(1)

    prices = business.get("prices") if isinstance(business, dict) else None
    if not isinstance(prices, dict) or not prices:
        print(f"Cannot start: {path} needs a \"prices\" section with your items.")
        sys.exit(1)
    for item, price in prices.items():
        if not isinstance(price, int) or price < 0:
            print(f"Cannot start: the price of '{item}' in {path} must be a whole number of PKR.")
            sys.exit(1)
    return business


def load_json(path: str, required_key: str) -> list:
    """Load a list of dictionaries from a file. Missing or damaged files give an empty list.

    Args:
        path: The JSON file to read.
        required_key: A key every entry must have, so a damaged entry can't crash us later.
    """
    try:
        with open(path, encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        print(f"Warning: {path} was damaged. Starting fresh.")
        return []

    if not isinstance(data, list):
        print(f"Warning: {path} was damaged. Starting fresh.")
        return []
    for entry in data:
        if not isinstance(entry, dict) or required_key not in entry:
            print(f"Warning: {path} was damaged. Starting fresh.")
            return []
    return data


def save_json(path: str, data: list) -> None:
    """Save a list to a JSON file that a person can read and edit."""
    with open(path, "w", encoding="utf-8") as file:
        # ensure_ascii=False keeps Urdu readable instead of ا codes.
        json.dump(data, file, indent=2, ensure_ascii=False)


def log_error(error: Exception) -> None:
    """Write the real error to errors.log for the developer."""
    with open(ERROR_LOG, "a", encoding="utf-8") as file:
        file.write(f"{datetime.now():%Y-%m-%d %H:%M:%S} {type(error).__name__}: {error}\n")


def friendly_error(error: Exception) -> str:
    """Log an AI error and return a message that is safe to show a customer."""
    log_error(error)
    stats["errors"] += 1
    if isinstance(error, ollama.ResponseError):
        return "Sorry, something went wrong on my side. Please try again in a minute."
    return "I am offline right now. Please open the Ollama app and try again."


def menu_name(raw_item: str) -> str:
    """Clean an item name so 'Brownies ' matches 'brownie' on the menu."""
    item = raw_item.lower().strip()
    if item not in prices and item.endswith("s") and item[:-1] in prices:
        item = item[:-1]
    return item


def calculate_total(lines: list) -> int:
    """Add up the line totals of an order. Pure Python, no AI, so the money is always right."""
    total = 0
    for line in lines:
        total += line["line_total"]
    return total


def next_order_id(existing_orders: list) -> str:
    """Return the next free order number, like A101, A102..."""
    highest = 100
    for order in existing_orders:
        number = str(order.get("id", ""))[1:]
        if number.isdigit() and int(number) > highest:
            highest = int(number)
    return f"A{highest + 1}"


def ask_approval(question: str) -> bool:
    """Ask the owner a yes/no question in the terminal."""
    answer = input(f"  [approve] {question} (yes/no) ")
    return answer.strip().lower() in ("yes", "y")


def save_new_order(customer: str, lines: list, source: str) -> dict:
    """Create an order, add it to orders.json and return it."""
    order = {
        "id": next_order_id(orders),
        "customer": customer,
        "items": lines,
        "total": calculate_total(lines),
        "status": "received",
        "source": source,
        "created": f"{datetime.now():%Y-%m-%d %H:%M}",
    }
    orders.append(order)
    save_json(ORDERS_FILE, orders)
    stats["orders_placed"] += 1
    return order


def find_order(order_id: str) -> dict | None:
    """Find an order by its number, or return None."""
    order_id = order_id.upper().strip()
    for order in orders:
        if order.get("id") == order_id:
            return order
    return None


# --------------------------------------------------------- load the data

business = load_business(BUSINESS_FILE)
prices = business["prices"]
orders = load_json(ORDERS_FILE, "id")
transcript = load_json(TRANSCRIPT_FILE, "role")

stats = {"questions": 0, "answered": 0, "errors": 0, "imports": 0, "orders_placed": 0}

# Test the money maths before anything else: if these fail, nothing should start.
assert calculate_total([]) == 0
assert calculate_total([{"line_total": 600}, {"line_total": 750}]) == 1350
assert next_order_id([]) == "A101"
assert next_order_id([{"id": "A101"}, {"id": "A105"}, {"id": "bad"}]) == "A106"


# ----------------------------------------------------------------- tools

@tool(parse_docstring=True)
def get_price(item: str) -> str:
    """Get the price of one menu item. Call it once for each item.

    Args:
        item: The item name, for example "brownie" or "chocolate cake".
    """
    name = menu_name(item)
    if name not in prices:
        return f"{item} is not on our menu. We sell: {', '.join(prices)}"
    return f"{name} costs {prices[name]:,} PKR"


@tool(parse_docstring=True)
def get_info(topic: str) -> str:
    """Get shop information: hours, delivery, payment, phone, city or type. Not for prices.

    Args:
        topic: One word, for example "hours" or "delivery".
    """
    topic = topic.lower().strip()
    if topic == "prices" or topic not in business:
        topics = [key for key in business if key != "prices"]
        return f"No info about '{topic}'. Topics I know: {', '.join(topics)}"
    return f"{topic}: {business[topic]}"


@tool(parse_docstring=True)
def order_status(order_id: str) -> str:
    """Check the status of an order that was already placed.

    Args:
        order_id: The order number, for example "A101".
    """
    order = find_order(order_id)
    if order is None:
        return f"No order found with number {order_id.upper().strip()}"
    return (f"Order {order['id']} for {order.get('customer', 'unknown')} is "
            f"{order.get('status', 'unknown')}, total {order.get('total', 0):,} PKR")


@tool(parse_docstring=True)
def place_order(item: str, quantity: int, customer: str) -> str:
    """Place a new order for one item. Only call it when you know the item, the quantity and the customer's name.

    Args:
        item: The menu item, for example "brownie".
        quantity: How many the customer wants.
        customer: The customer's name.
    """
    name = menu_name(item)
    if name not in prices:
        return f"Cannot order {item}: it is not on our menu. We sell: {', '.join(prices)}"
    if quantity < 1:
        return "Cannot order: the quantity must be at least 1"
    if customer.strip() == "":
        return "Cannot order yet: ask the customer for their name first"

    # The price comes from business.json, never from the AI, so "make it free"
    # or a made-up price can never reach an order.
    lines = [{"item": name, "quantity": quantity, "line_total": prices[name] * quantity}]
    total = calculate_total(lines)

    # The approval is inside the tool, not just in the prompt, so no wording
    # from a customer can make the agent skip it.
    if not ask_approval(f"{quantity} x {name} for {customer} = {total:,} PKR. Place it?"):
        return "Order NOT placed: the owner said no. Tell the customer we will contact them."

    order = save_new_order(customer.strip(), lines, "chat")
    return f"Order {order['id']} placed: {quantity} x {name}, total {total:,} PKR"


@tool(parse_docstring=True)
def cancel_order(order_id: str) -> str:
    """Cancel an order that has not been delivered yet.

    Args:
        order_id: The order number, for example "A101".
    """
    order = find_order(order_id)
    if order is None:
        return f"No order found with number {order_id.upper().strip()}"
    if order.get("status") == "delivered":
        return f"Order {order['id']} was already delivered, so it cannot be cancelled"
    if order.get("status") == "cancelled":
        return f"Order {order['id']} is already cancelled"
    if not ask_approval(f"Cancel order {order['id']} for {order.get('customer')} ({order.get('total', 0):,} PKR)?"):
        return f"Order {order['id']} NOT cancelled: the owner said no"

    order["status"] = "cancelled"
    save_json(ORDERS_FILE, orders)
    return f"Order {order['id']} is cancelled"


TOOLS = {
    "get_price": get_price,
    "get_info": get_info,
    "order_status": order_status,
    "place_order": place_order,
    "cancel_order": cancel_order,
}

tool_usage = {}
for tool_name in TOOLS:
    tool_usage[tool_name] = 0

SYSTEM_MESSAGE = (
    f"You are the assistant for {business.get('name', 'our shop')}, a {business.get('type', 'business')} "
    f"in {business.get('city', 'Lahore')}.\n"
    "Always use a tool for prices (get_price), shop info like hours or delivery (get_info), "
    "order status (order_status), new orders (place_order) and cancellations (cancel_order).\n"
    "Never guess a price, the hours or an order status.\n"
    "Before place_order you need the item, the quantity and the customer's name. If one is missing, ask for it. "
    "For several different items, call place_order once per item.\n"
    "Never promise discounts, free items or delivery times. Keep answers short and friendly."
)

llm = init_chat_model(MODEL, model_provider="ollama", temperature=0)
agent = llm.bind_tools(list(TOOLS.values()))
# Temperature 0 and a fixed schema: extraction should be the same every time, not creative.
extractor = init_chat_model(MODEL, model_provider="ollama", temperature=0, format=ORDER_SCHEMA)

EXTRACT_MESSAGE = (
    "You read WhatsApp messages sent to a bakery and extract the order.\n"
    f"Menu items: {', '.join(prices)}.\n"
    "- is_order is true only if the customer asks to buy something.\n"
    "- Use the singular menu name when an item matches the menu (cupcakes -> cupcake).\n"
    "- Copy items that are not on the menu exactly as written.\n"
    "- customer and address must be written in the message; otherwise use an empty string.\n"
    "- Never invent a name, address, item or quantity."
)


# -------------------------------------------------------------- commands

def run_agent(question: str) -> str | None:
    """Run the agent loop for one question. Returns the answer, or None if the AI failed."""
    turn = [{"role": "user", "content": question}]

    for step in range(MAX_STEPS):
        # Only the last few saved messages are sent: enough to remember the
        # customer, but the prompt doesn't keep growing (and slowing down) forever.
        messages = [{"role": "system", "content": SYSTEM_MESSAGE}] + transcript[-MEMORY_SIZE:] + turn
        try:
            response = agent.invoke(messages)
        except AI_ERRORS as error:
            print(f"Assistant: {friendly_error(error)}")
            return None

        if not response.tool_calls:
            return response.text

        turn.append(response)
        for call in response.tool_calls:
            name = call["name"]
            args = call["args"]
            chosen_tool = TOOLS.get(name)

            if chosen_tool is None:
                result = f"Error: there is no tool called '{name}'. Use one of: {', '.join(TOOLS)}"
            else:
                try:
                    result = chosen_tool.invoke(args)
                    tool_usage[name] += 1
                except ValidationError as error:
                    # Send the mistake back so the model can fix its own arguments.
                    problem = error.errors()[0]
                    field = ".".join(str(part) for part in problem["loc"])
                    result = f"Error: wrong arguments for {name}: '{field}' {problem['msg']}. Try again."

            print(f"  [tool] {name}({args}) -> {result}")
            # tool_call_id tells the model which of its tool calls this result answers.
            turn.append({"role": "tool", "content": str(result), "tool_call_id": call["id"]})
    else:
        return "Sorry, I couldn't finish that. Please ask in a simpler way, or call us."


def check_import(message: str, data: dict) -> dict:
    """Price the extracted items in Python and list everything a human should check.

    Args:
        message: The original WhatsApp message.
        data: The order the AI extracted from it.
    """
    lines = []
    checks = []

    for entry in data.get("items", []):
        if not isinstance(entry, dict):
            checks.append(f"strange item in the AI reply: {entry!r}")
            continue
        item = menu_name(str(entry.get("item", "")))
        quantity = entry.get("quantity", 0)
        if item not in prices:
            checks.append(f"'{item}' is not on the menu")
            continue
        if not isinstance(quantity, int) or quantity < 1:
            checks.append(f"quantity {quantity!r} for {item} looks wrong")
            continue
        lines.append({"item": item, "quantity": quantity, "line_total": prices[item] * quantity})

    customer = str(data.get("customer", "")).strip()
    # The AI sometimes fills a missing name with an invented one, so the name
    # has to appear in the customer's own words.
    name_found = customer != "" and customer.lower() in message.lower()
    if customer == "":
        checks.append("customer name is missing")
    elif not name_found:
        checks.append(f"customer '{customer}' is not in the message (invented?)")

    return {
        "lines": lines,
        "checks": checks,
        "customer": customer,
        "address": str(data.get("address", "")).strip(),
        "name_found": name_found,
    }


def run_import() -> None:
    """Turn one pasted WhatsApp message into a checked order, saved only if the owner says yes."""
    stats["imports"] += 1
    message = input("Paste the WhatsApp message: ").strip()
    if message == "":
        print("  Nothing pasted.")
        return

    try:
        response = extractor.invoke([
            {"role": "system", "content": EXTRACT_MESSAGE},
            {"role": "user", "content": message},
        ])
    except AI_ERRORS as error:
        print(f"  {friendly_error(error)}")
        return

    try:
        data = json.loads(response.text)
    except json.JSONDecodeError:
        print("  CHECK: the AI reply was not valid JSON. Needs a human.")
        return

    if not isinstance(data, dict) or not data.get("is_order", False):
        print("  Not an order: needs a human reply.")
        return

    result = check_import(message, data)
    for line in result["lines"]:
        print(f"  {line['quantity']} x {line['item']} = {line['line_total']:,} PKR")
    print(f"  Customer: {result['customer'] or '(missing)'}, Address: {result['address'] or '(missing)'}")
    if result["lines"]:
        print(f"  Total: {calculate_total(result['lines']):,} PKR")
    for check in result["checks"]:
        print(f"  CHECK: {check}")

    if not result["lines"]:
        print("  Nothing from our menu: needs a human reply.")
        return
    if not ask_approval("Save this order?"):
        print("  Not saved.")
        return

    # A name the AI invented is never saved as if it were real.
    customer = result["customer"] if result["name_found"] else "(unknown)"
    order = save_new_order(customer, result["lines"], "whatsapp")
    print(f"  Saved as order {order['id']}.")


def show_orders() -> None:
    """Print every order on file as a numbered list."""
    if not orders:
        print("  No orders yet.")
        return
    for number, order in enumerate(orders, start=1):
        print(f"  {number}. {order.get('id')} | {order.get('customer', '?')} | "
              f"{order.get('total', 0):,} PKR | {order.get('status', '?')}")


def run_summary() -> None:
    """Count orders and value per status, then ask the AI for a short note to the owner."""
    per_status = {}
    for order in orders:
        status = order.get("status", "unknown")
        if status not in per_status:
            per_status[status] = {"count": 0, "value": 0}
        per_status[status]["count"] += 1
        per_status[status]["value"] += order.get("total", 0)

    if not per_status:
        print("  No orders yet, nothing to summarise.")
        return

    numbers = ""
    for status, totals in per_status.items():
        line = f"{status}: {totals['count']} orders, {totals['value']:,} PKR"
        print(f"  {line}")
        numbers += line + "\n"

    # The AI only writes the note. The numbers above are counted in Python,
    # so a wrong sum from the AI can't reach the owner.
    try:
        response = llm.invoke([
            {"role": "system", "content": "You write a 2-line note to a bakery owner. Use only the numbers given."},
            {"role": "user", "content": f"Today's orders by status:\n{numbers}"},
        ])
    except AI_ERRORS as error:
        print(f"  (No AI note: {friendly_error(error)})")
        return
    print(f"  Note: {response.text}")


# ------------------------------------------------------------- main loop

print(LINE)
print(f"   {business.get('name', 'Our')} AI Business Assistant")
print(LINE)
if transcript or orders:
    print(f"Loaded {len(transcript)} chat messages and {len(orders)} orders.")
print("Ask anything, or use: /import, /orders, /summary, /reset, bye")

try:
    while True:
        user_text = input("You: ").strip()
        if user_text == "":
            continue
        command = user_text.lower()

        if command == "bye":
            print("Assistant: Goodbye! Everything is saved.")
            break
        if command == "/reset":
            transcript = []
            save_json(TRANSCRIPT_FILE, transcript)
            print("Assistant: Chat cleared. Your orders are kept.")
            continue
        if command == "/orders":
            show_orders()
            continue
        if command == "/import":
            run_import()
            continue
        if command == "/summary":
            run_summary()
            continue

        stats["questions"] += 1
        answer = run_agent(user_text)
        if answer is None:
            continue

        print(f"Assistant: {answer}")
        stats["answered"] += 1
        # Only plain role/content dictionaries are saved, never the model's
        # response objects, so the file always loads back with json.load.
        transcript.append({"role": "user", "content": user_text})
        transcript.append({"role": "assistant", "content": answer})
        save_json(TRANSCRIPT_FILE, transcript)
except (KeyboardInterrupt, EOFError):
    # Ctrl+C still ends politely, and the report below still prints.
    print("\nAssistant: Goodbye! Everything is saved.")

print(LINE)
print("Session report")
print(f"Questions: {stats['questions']} | Answered: {stats['answered']} | Errors: {stats['errors']}")
print(f"WhatsApp imports: {stats['imports']} | Orders placed: {stats['orders_placed']} | Orders on file: {len(orders)}")
print("Tool calls:")
for tool_name, count in tool_usage.items():
    print(f"  {tool_name}: {count}")
print(LINE)