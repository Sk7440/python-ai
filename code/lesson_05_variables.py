"""Task 1.5: AI Model Profile Card.

Shows one AI model's details (with their data types) and estimates
how much a single chat, and a month of chats, would cost in PKR.
"""

# Model profile: one variable for each of the 4 basic types
model_name = "llama3.2"            # str
context_window = 128000            # int (tokens)
price_per_1k_tokens = 0.5          # float
runs_locally = True                # bool

print("--- AI Model Profile Card ---")
# Why: printing type() proves to the client (and teacher) each value is the type we intended
print(f"Model: {model_name} {type(model_name)}")
print(f"Context window: {context_window} tokens {type(context_window)}")
print(f"Price per 1K tokens: {price_per_1k_tokens} PKR {type(price_per_1k_tokens)}")
print(f"Runs locally: {runs_locally} {type(runs_locally)}")

# Why: input() always returns text, so we convert to int before doing maths
tokens_per_chat = int(input("Tokens per chat: "))

# Why: price is per 1,000 tokens, so divide tokens by 1000 first
cost_per_chat = tokens_per_chat / 1000 * price_per_1k_tokens
print(f"Estimated cost: {round(cost_per_chat, 2)} PKR")

# Stretch: monthly cost based on chats per day
chats_per_day = int(input("Chats per day: "))
monthly_cost = cost_per_chat * chats_per_day * 30   
print(f"Estimated monthly cost: {round(monthly_cost, 2)} PKR")