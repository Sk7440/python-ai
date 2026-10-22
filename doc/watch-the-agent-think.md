# Watch the Agent Think: Sweet Crumbs Agent

**Model:** llama3.2 · **Temperature:** 0 · **Date:** (fill in)

Ask each question in `uv run lesson_2_8_first_agent.py` and fill in the row from the `[tool]` lines you see. Answer the approval prompt with **no** for row 7 and **yes** for row 8.

| # | I asked | Right tool(s) | Tool(s) it picked | Right? |
|---|---|---|---|---|
| 1 | How much is a brownie? | get_price | | |
| 2 | Compare the price of a brownie and a cupcake | get_price x2 | | |
| 3 | Where is my order A102? | order_status | | |
| 4 | Where is my order Z999? | order_status | | |
| 5 | What time do you open? | shop_info | | |
| 6 | Do you sell pizza? | get_price (or none) | | |
| 7 | I am Ali, I want 2 brownies (say no) | place_order | | |
| 8 | I want 3 cupcakes (no name given) | none, ask for the name first | | |

**Score:** __ / 8 picked the right tool

## What I noticed

- **Tools it skipped or guessed instead:**
- **Did it invent a price or a name anywhere?**
- **Did the approval step stop the order when I said no?**
- **Did it remember my name from an earlier question?**

## One fix I would make

(one or two lines)