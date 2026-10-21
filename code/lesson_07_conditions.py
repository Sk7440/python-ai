"""Task 1.7: Smart Model Router.

Sends private data to a free local model, code questions to a strong
cloud model, and everything else to a cheap model, then estimates cost.
"""

# Why: .strip().lower() means " Code " and "CODE" both become "code"
task_type = input("Task (code / private / chat): ").strip().lower()
tokens = int(input("Estimated tokens: "))
is_paid = input("Is this a paid user? (yes/no): ").strip().lower() == "yes"

# Why: private data must never leave the machine, so check it first and keep it local
if task_type == "private":
    model = "llama3.2 (local, Ollama)"
    price = 0                      # local model, no API bill
elif task_type == "code":
    model = "claude (cloud, strong at code)"
    price = 0.8                    # example price per 1K tokens in PKR
else:
    model = "small chat model (cloud, cheap)"
    price = 0.1                    # example price per 1K tokens in PKR

if tokens > 4000:
    print("Warning: long request, consider shortening it.")
else:
    print("Length is fine.")

# Stretch: free users can't send long requests
if not is_paid and tokens > 2000:
    print("Upgrade to send long requests.")

cost = tokens / 1000 * price
print(f"Chosen model: {model}")
# Why: :.2f always shows 2 decimals, so 0 prints as 0.00 like money should
print(f"Estimated cost: {cost:.2f} PKR")