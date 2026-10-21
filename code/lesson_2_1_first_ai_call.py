"""Task 2.1: AI Tutor
Asks a topic , gets an explanation from a local
AI model, and shows how many tokens and seconds it took."""

from langchain.chat_models import init_chat_model
 
topic = input("Topic:   ").strip()
level = input("Level (beginner or expert): ").strip().lower()
 
system_message = (
    f"You are a patient tutor at a tuition centre. "
    f"Explain the topic for a {level} student. "
    f"Keep the answer to 3 short sentences."
)
 
llm = init_chat_model("gemma4:31b-cloud", model_provider="ollama", temperature=0.2)
 
response = llm.invoke([
    {"role": "system", "content": system_message},
    {"role": "user", "content": topic},
])
 
print("=" * 40)
print(response.text)
print("=" * 40)
 
tokens = response.usage_metadata["total_tokens"]
seconds = response.response_metadata["total_duration"] / 1_000_000_000
print(f"{tokens} tokens in {seconds:.1f} seconds")