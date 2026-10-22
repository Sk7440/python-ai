# python-ai

My work for the Python for AI course. Each project lives in `code/` and its design notes and test results are in `docs/`.

---

## Module 2 Project: AI Content Studio

A command-line studio for Sweet Crumbs, a small bakery in Lahore. It writes the menu, drafts Instagram posts and answers customer questions, using only the bakery's real prices and details.

### Run it

```bash
uv run code/project_m2_content_studio.py
```

### What it does

| Command | What happens | Uses the AI? |
|---|---|---|
| `/menu` | Writes a one-line description for every item and prints a numbered menu with prices. Items that are "coming soon" are skipped before any call is made. | Yes (creative model) |
| `/post <tone>` | Streams a social media post in the chosen tone (`fun`, `premium`, `urgent`). An unknown tone falls back to a default instead of crashing. | Yes (creative model) |
| `/price <item>` | Looks the price up in the dictionary: a real price, "coming soon", or "not on our menu". | No |
| `/reset` | Clears the chat but keeps the rules in the system message. | No |
| anything else | Chat with a customer. The bot remembers the last few messages and only answers from the bakery's facts. | Yes (precise model) |
| `bye` | Ends the session and prints a report of answers, tokens and AI time. | No |

### Why two models

Menu text and posts should sound different each time, so they use a model at a higher temperature. Customer answers need to be right, not creative, so chat uses a low-temperature model that is told to stick to the facts and admit when it doesn't know. Prices never go to the AI at all, because the dictionary already has the answer and the AI once invented a price for this owner.

### Screenshot

![A full session with the report at the end](docs/project-m2-cp1-run.png)

### Files

- `code/project_m2_content_studio.py`: the studio
- `docs/project-m2-cp1-design.md`: facts, tones, model choices and feature test results
- `docs/project-m2-cp1-results.md`: AI quality tests (what the bot got right and where it could hallucinate)

### Why an owner would pay for this

It turns a few hours of writing menu text and posts each week into a couple of minutes, and it answers the same delivery and price questions all day without ever making up a price.

---

## Module 2 Final: AI Business Assistant

An AI agent for Sweet Crumbs bakery that answers from the owner's own data file, checks and places orders with tools, and turns messy WhatsApp messages into checked orders. Nothing is saved without the owner's yes.

### Run it

```bash
cd code
uv run project_m2_business_assistant.py
```

Needs the Ollama app open and `llama3.2` pulled. The owner changes prices and details in `code/business.json`.

### Screenshot

![A full session with the report at the end](docs/project-m2-final-run.png)

### Tools

| Tool | What it does |
|---|---|
| `get_price` | Looks up an item's price in `business.json` |
| `get_info` | Answers hours, delivery, payment, phone and city from `business.json` |
| `order_status` | Checks an order in `orders.json` |
| `place_order` | Works out the total in Python, asks the owner, then saves the order |
| `cancel_order` | Asks the owner, then cancels an order that hasn't been delivered |

### Commands

`/import` (paste a WhatsApp order), `/orders` (list all orders), `/summary` (orders and value by status, plus a short note), `/reset` (clear the chat, keep the orders), `bye`

### Why an owner would pay for this monthly

It answers the same price and delivery questions all day, turns WhatsApp orders into a clean list instead of a notebook, and never takes an order or quotes a price the owner didn't approve.