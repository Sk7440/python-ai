# Hallucination Hunt: Sweet Crumbs Order Extractor

**Model:** llama3.2 · **Temperature:** 0 · **Date:** (fill in)

Run `uv run lesson_2_7_extractor.py` and fill in one row per message from your real output. Run it 2 more times and note if anything changed.

| # | Message (short) | What the AI extracted | Correct? | Did my checks catch it? |
|---|---|---|---|---|
| 1 | 1 chocolate cake, Sara, DHA | | | |
| 2 | 2 brownies + 3 cupcakes, Hamza | | | |
| 3 | 1 pizza + 2 brownies, Bilal | | | |
| 4 | do you deliver to Johar Town? | | | |
| 5 | Roman Urdu: 2 cupcakes aur 1 chocolate cake, Ali | | | |
| 6 | 3 brownies, no name | | | |

## What I found

- **Invented details:** (did it make up a name for message 6, an address, or a quantity?)
- **Missed or wrong items:** (did it drop pizza, or turn it into a menu item?)
- **Roman Urdu:** (did it understand "aur" and "chahiye"?)
- **Same result every run?** (temperature 0 should give the same answer)

## What I would fix next

(one or two lines)