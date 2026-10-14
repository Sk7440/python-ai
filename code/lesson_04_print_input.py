"""Ultimate BPB: collects business detail and builds a ready-to-use prompt which can be give to Any AI model or LLM."""


Name = input("Enter your Name: ")
Business = input("Your Business type: ")
Problem = input("Biggest problem you are facing right now: ")

# input always returns str, so convert to int with help of int() to make sure the budget is a number
Budget = int(input("Monthly budget (PKR): "))

print(f"Welcome Dear, {Name}!")

print(f"This is Your AI Prompt")


Final_prompt = (
    f"Suggest 3 AI solutions for a {Business} that struggles with {Problem}. "
    f"Budget: {Budget} PKR per month."
)

print(f"{Final_prompt}")