"""Task 1.8: Business Helper Bot (Module 1 Final).

A rule-based helper for Bright Future Tuition Centre (example business).
Answers common questions, hands complaints to a human, and counts
the questions it could not answer so the owner sees what to add next.
"""

business = "Bright Future Tuition Centre"
bot = "Bright Future Bot"

message_count = 0
unanswered_count = 0
complaint_count = 0

print(f"{bot}: Hi! Ask about timings, fees, subjects, location or admission. Type 'bye' to exit.")
# Why: ask the name once, before the loop, so we don't ask it again every message
user_name = input(f"{bot}: What is your name? ").strip().title()

while True:
    # Why: .strip().lower() makes "  FEES " and "fees" the same message
    message = input(f"{user_name}: ").strip().lower()
    message_count += 1

    if message == "bye":
        print(f"{bot}: Take care, {user_name}!")
        break

    # Why: complaints are checked FIRST, so "late fee refund" is treated as a complaint, not a fee question
    if "late" in message or "complaint" in message or "refund" in message or "bad" in message:
        complaint_count += 1
        print(f"{bot}: Sorry about that, {user_name}. The centre manager will call you today.")
    elif message == "agent" or message == "human":
        print(f"{bot}: Connecting you to a human...")
        break
    # Why: "hi" uses startswith, because "in" would match "hi" inside words like "this" or "chemistry"
    elif message.startswith("hi") or message.startswith("hello") or message == "salam":
        print(f"{bot}: Hello {user_name}! How can I help you today?")
    elif "timing" in message or "time" in message or "open" in message:
        print(f"{bot}: Classes run 3 pm to 8 pm, Monday to Saturday.")
    elif "fee" in message or "price" in message or "cost" in message:
        print(f"{bot}: Monthly fee is 5,000 PKR per subject.")
    elif "subject" in message or "math" in message or "physics" in message:
        print(f"{bot}: We teach Maths, Physics, Chemistry and English for Matric and FSc.")
    elif "location" in message or "address" in message or "where" in message:
        print(f"{bot}: We are at Main Boulevard, Johar Town, Lahore.")
    elif "admission" in message or "join" in message or "enroll" in message:
        print(f"{bot}: Admissions are open. Visit the centre with your last result card.")
    else:
        unanswered_count += 1
        ai_prompt = f"You are the friendly assistant of {business}. Answer in 2 lines: {message}"
        print(f"{bot}: I am not sure yet. In Module 2, an AI will answer: {ai_prompt}")

print("=" * 40)
print(f"Chat summary: {message_count} messages, {unanswered_count} unanswered, {complaint_count} complaints.")