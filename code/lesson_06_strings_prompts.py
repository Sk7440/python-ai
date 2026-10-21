"""Task 1.6: Prompt Cleaner.

Cleans a user's messy name and question, measures the question,
and builds a safe, size-limited prompt for an AI tutor.
"""

raw_name = input("Your name: ")
raw_question = input("Your question: ")

# Why: users add stray spaces and random capitals; clean before anything else
clean_name = raw_name.strip().title()
clean_question = raw_question.strip().capitalize()

# Stretch: hide a rude word before it ever reaches the AI
clean_question = clean_question.replace("stupid", "***")

char_count = len(clean_question)
# Why: a common rule of thumb is about 4 characters per token
token_estimate = round(char_count / 4)

# Why: .lower() first, so "Python", "PYTHON" and "python" all match
mentions_python = "python" in clean_question.lower()

price_per_1k_tokens = 0.5   # example price in PKR
estimated_cost = token_estimate / 1000 * price_per_1k_tokens

print("=" * 40)
print(f"Cleaned question: {clean_question}")
print(f"Characters: {char_count}, about {token_estimate} tokens")
print(f"Mentions Python: {mentions_python}")
print(f"Estimated cost: {estimated_cost:.2f} PKR")
print("=" * 40)

# Why: [:150] caps the question so a huge paste can't blow up the prompt size or cost
prompt = f"""You are a friendly Python tutor.
Greet {clean_name} by name and answer in 3 short lines.
Question: {clean_question[:150]}"""
print(prompt)