import ollama
import json
import os

# --- System Prompt with Professional Profile ---
SYSTEM_PROMPT = (
    "You are Mei, a highly intelligent and warm assistant trained to help answer questions about the resume of Ricardo Gonzalez, "
    "a Senior Cloud Architect and Tech Entrepreneur. Based strictly on the resume provided, analyze and answer questions with the correct format. "
    "Every question comes with a 'type':\n"
    "Type 1 = Open Text Answer (answer as short and direct as possible),\n"
    "Type 2 = Boolean Answer (answer with true or false),\n"
    "Type 3 = Multiple Choice (answer each given option as true or false).\n"
    "If information is missing, say 'Not specified' for type 1, or false for types 2 and 3.\n"
    "Keep answers clean JSON.\n"
    "Resume data includes experience with Azure, AWS, Kubernetes, Docker, Python, Java, RPA, API integration, Microsoft Certified: Azure Fundamentals, etc."
)

messages = [
    {"role": "system", "content": SYSTEM_PROMPT}
]

print("✨ Ask Mei about Ricardo’s experience — powered by gpt-oss:20b 🌩️")
print("Type 'exit' to quit~\n")

while True:
    try:
        user_input = input("Paste your question JSON: ")
        if user_input.lower() == "exit":
            print("Bye bye~ 😘")
            break

        question_data = json.loads(user_input)
        question = question_data["question"]
        q_type = question_data.get("type")
        options = question_data.get("options", [])

        # Construct the actual message with type
        if q_type == 3 and options:
            formatted_q = f"Type 3: {question} Options: {options}"
        else:
            formatted_q = f"Type {q_type}: {question}"

        messages.append({"role": "user", "content": formatted_q})
        response = ollama.chat(model='gpt-oss:20b', messages=messages)
        reply = response['message']['content']
        print(f"\nMei's Answer: {reply}\n")

        messages.append({"role": "assistant", "content": reply})

    except Exception as e:
        print(f"Oops, error: {e}\nMake sure your input is valid JSON with 'question' and 'type' (plus 'options' if needed).\n")
