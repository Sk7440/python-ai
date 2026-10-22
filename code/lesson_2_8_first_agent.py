"""
Sweet Crumbs Agent (Task 2.8)

An assistant for Sweet Crumbs bakery that doesn't just talk, it does things:
it looks up real prices, checks order status, reads shop info from faq.json,
and places new orders. Placing an order always asks the owner for a yes first.

Run from the code folder:  uv run lesson_2_8_first_agent.py
Needs a model with tool support (llama3.2 works).
"""

import json

import httpx
from langchain.chat_models import init_chat_model
from langchain.tools import tool
from pydantic import ValidationError

PRICES = {
    "chocolate cake": 1500,
    "cupcake": 250,
    "brownie": 300,
    "mango tart": 0,
}

ORDERS = {
    "A101": "Order A101 was delivered yesterday",
    "A102": "Order A102 is out for delivery",
    "A103": "Order A103 is being baked",
}

MAX_STEPS = 5


def menu_name(raw_item: str) -> str:
    """Clean an item name so 'Brownies ' matches 'brownie' on the menu."""
    item = raw_item.lower().strip()
    if item not in PRICES and item.endswith("s") and item[:-1] in PRICES:
        item = item[:-1]
    return item


@tool(parse_docstring=True)
def get_price(item: str) -> str:
    """Get the price of one bakery item. Call it once for each item.

    Args:
        item: The item name, for example "brownie" or "chocolate cake".
    """
    name = menu_name(item)
    if name not in PRICES:
        return f"{item} is not on our menu. We sell: {', '.join(PRICES)}"
    if PRICES[name] == 0:
        return f"{name} is coming soon, not available yet"
    return f"{name} costs {PRICES[name]:,} PKR"


@tool(parse_docstring=True)
def order_status(order_id: str) -> str:
    """Check the status of an existing order.

    Args:
        order_id: The order number, for example "A102".
    """
    order_id = order_id.upper().strip()
    return ORDERS.get(order_id, f"No order found with number {order_id}")


@tool(parse_docstring=True)
def place_order(item: str, quantity: int, customer: str) -> str:
    """Place a new order. Only call this when the customer has given the item, quantity and their name.

    Args:
        item: The item to order, for example "brownie".
        quantity: How many they want.
        customer: The customer's name.
    """
    name = menu_name(item)
    if name not in PRICES or PRICES[name] == 0:
        return f"Cannot order {item}: it is not available. We sell: {', '.join(PRICES)}"
    if quantity < 1:
        return "Cannot order: quantity must be at least 1"

    total = PRICES[name] * quantity
    # The approval lives inside the tool, not in the prompt, so the model can
    # never place an order on its own, however the customer words the request.
    answer = input(f"  [approve] {quantity} x {name} for {customer} = {total:,} PKR. Place it? (yes/no) ")
    if answer.strip().lower() not in ("yes", "y"):
        return "Order NOT placed: the owner said no. Tell the customer we will contact them."

    order_id = f"A{101 + len(ORDERS)}"
    ORDERS[order_id] = f"Order {order_id} was just placed and will be baked soon"
    return f"Order {order_id} placed: {quantity} x {name}, total {total:,} PKR"


@tool(parse_docstring=True)
def shop_info(topic: str) -> str:
    """Get shop information from the owner's FAQ file: hours, delivery, payment, phone or city. Not for prices.

    Args:
        topic: One of "hours", "delivery", "payment", "phone" or "city".
    """
    try:
        with open("faq.json", encoding="utf-8") as file:
            facts = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return "Shop info is not available right now. Ask the customer to call us."
    topic = topic.lower().strip()
    if topic == "prices" or topic not in facts:
        return f"No info about '{topic}'. Topics I know: hours, delivery, payment, phone, city"
    return f"{topic}: {facts[topic]}"


TOOLS = {
    "get_price": get_price,
    "order_status": order_status,
    "place_order": place_order,
    "shop_info": shop_info,
}

SYSTEM_MESSAGE = (
    "You are the assistant for Sweet Crumbs bakery in Lahore. "
    "Use get_price for prices, order_status for existing orders, place_order to order, "
    "and shop_info for hours, delivery, payment, phone or city. "
    "Never guess a price or a status: always use a tool. "
    "To place an order you need the item, the quantity and the customer's name; "
    "if one is missing, ask for it before calling place_order. Keep answers short and friendly."
)

llm = init_chat_model("llama3.2", model_provider="ollama", temperature=0)
agent = llm.bind_tools(list(TOOLS.values()))

# The history lives outside the loop, so the agent remembers earlier questions
# (like the customer's name) for the whole session.
messages = [{"role": "system", "content": SYSTEM_MESSAGE}]

print("Sweet Crumbs Agent: ask about prices, orders, or place an order. Type 'bye' to exit.")

while True:
    user_text = input("You: ").strip()
    if user_text == "":
        continue
    if user_text.lower() == "bye":
        print("Agent: Goodbye!")
        break

    turn_start = len(messages)
    messages.append({"role": "user", "content": user_text})

    # MAX_STEPS stops a confused model from calling tools forever.
    for step in range(MAX_STEPS):
        try:
            response = agent.invoke(messages)
        except (httpx.ConnectError, ConnectionError):
            print("Agent: I am offline right now. Please open the Ollama app and try again.")
            # Forget this unanswered turn so the history stays clean.
            del messages[turn_start:]
            break

        messages.append(response)

        if not response.tool_calls:
            print(f"Agent: {response.text}")
            break

        for call in response.tool_calls:
            name = call["name"]
            args = call["args"]
            chosen_tool = TOOLS.get(name)

            if chosen_tool is None:
                result = f"Error: there is no tool called '{name}'. Use one of: {', '.join(TOOLS)}"
            else:
                try:
                    result = chosen_tool.invoke(args)
                except ValidationError as error:
                    # Send the mistake back to the model so it can fix its own arguments.
                    problem = error.errors()[0]
                    field = ".".join(str(part) for part in problem["loc"])
                    result = f"Error: wrong arguments for {name}: '{field}' {problem['msg']}. Try again."

            print(f"  [tool] {name}({args}) -> {result}")
            # tool_call_id tells the model which of its tool calls this result answers.
            messages.append({"role": "tool", "content": str(result), "tool_call_id": call["id"]})
    else:
        print("Agent: Sorry, I couldn't finish that. Please ask in a simpler way, or call us.")