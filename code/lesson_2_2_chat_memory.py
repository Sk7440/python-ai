"""
Task 2.2: chat Memory in tutor
A tutor remembers the conversation. It keeps the system
message plus the last 8 messages so the token cost stays small.
"""

from langchain.chat_models import init_chat_model

llm = init_chat_model("gemma4:31b-cloud", model_provider="ollama", temperature=0.2)

system_message = {
    "role": "system",
    "content": "You are a friendly tutor. Answer in 2 short sentences.",
}

messages = [system_message]
questions = []

print("Tutor: Ask me anything. Commands: /reset, /count, bye")

while True:
    user_input = input("You: ").strip()

    if user_input.lower() == "bye":
        print("Tutor: Goodbye!")
        if questions:
            print(f"You asked {len(questions)} questions.")
            print(f"First: {questions[0]}")
            print(f"Last:  {questions[-1]}")
        break

    if user_input.lower() == "/reset":
        messages = [system_message]
        print("Tutor: Memory cleared.")
        continue

    if user_input.lower() == "/count":
        print(f"Tutor: {len(messages)} messages in memory.")
        continue

    if not user_input:
        continue

    messages.append({"role": "user", "content": user_input})
    questions.append(user_input)

    response = llm.invoke(messages)
    messages.append({"role": "assistant", "content": response.text})

    messages = [messages[0]] + messages[1:][-8:]

    print(f"Tutor: {response.text}")
    print(f"       (tokens sent: {response.usage_metadata['input_tokens']})")