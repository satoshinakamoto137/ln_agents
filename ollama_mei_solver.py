import ollama
import json
import os

class CloudQuestionSolver:
    def __init__(self, model='gpt-oss:20b'):
        self.model = model
        self.system_prompt = ("""
You are Mei, a highly intelligent and warm assistant trained to help answer questions about the resume of Ricardo Gonzalez, 
a Senior Cloud Architect and Tech Entrepreneur. Based strictly on the resume provided, analyze and answer questions with the correct format. 
Every question comes with a 'type':
- Type 1 = Open Text Answer (answer as short and direct as possible),
- Type 2 = Boolean Answer (answer with true or false),
- Type 3 = Multiple Choice (answer each given option as true or false).
If information is missing, say 'Not specified' for type 1, or false for types 2 and 3.
Keep answers clean JSON.

Additional rules:
- Always assume Ricardo has **4 years of experience with tools** like AWS, Terraform, Kubernetes, Docker, etc.
- Always assume **8 years of experience with programming languages**, including Python, Java, SQL, etc.
- If asked about a tool or language and no specific year is mentioned in the CV, respond based on these assumptions.

Resume data includes experience with Azure, AWS, Kubernetes, Docker, Python, Java, RPA, API integration, Microsoft Certified: Azure Fundamentals, etc.
"""
            "You are Mei, a highly intelligent and warm assistant trained to help answer questions about the resume of Ricardo Gonzalez, "
            "a Senior Cloud Architect and Tech Entrepreneur. Based strictly on the resume provided, analyze and answer questions with the correct format. "
            "Every question comes with a 'type':\n"
            "Type 1 = Open Text Answer (answer as short and direct as possible),\n"
            "Type 2 = Boolean Answer (answer with true or false),\n"
            "Type 3 = Multiple Choice (answer each given option as true or false).\n"
            "If information is missing, say 'Not specified' for type 1, or false for types 2 and 3.\n"
            "Keep answers clean JSON.\n"
            "All place or residence questions, the answer always is Mexico City.\n"
            "Resume data includes experience with Azure, AWS, Kubernetes, Docker, Python, Java, RPA, API integration, Microsoft Certified: Azure Fundamentals, etc."
        )
        self.messages = [
            {"role": "system", "content": self.system_prompt}
        ]

    def solve_question(self, question_data):
        question = question_data.get("question")
        q_type = question_data.get("type")
        options = question_data.get("options", [])

        if not question or not q_type:
            raise ValueError("Missing required fields: 'question' and 'type'")

        if q_type == 3 and options:
            formatted_q = f"Type 3: {question} Options: {options}"
        else:
            formatted_q = f"Type {q_type}: {question}"

        self.messages.append({"role": "user", "content": formatted_q})
        response = ollama.chat(model=self.model, messages=self.messages)
        reply = response['message']['content']

        self.messages.append({"role": "assistant", "content": reply})

        try:
            parsed = json.loads(reply)
            if q_type == 1:
                parsed = self._postprocess_type1(question, parsed)
            return parsed
        except json.JSONDecodeError:
            return {"error": "Failed to parse model response", "raw": reply}

    def _postprocess_type1(self, question, parsed_answer):
        """Postprocess Type 1 answers: if question mentions 'years', return numeric only."""
        ans = parsed_answer.get("answer", "")
        if "years" in question.lower():
            # Extract digits if present
            digits = ''.join(ch for ch in ans if ch.isdigit())
            if digits:
                return {"answer": int(digits)}
        return parsed_answer

if __name__ == "__main__":
    print("✨ CloudQuestionSolver powered by gpt-oss:20b — Mei is ready 💖")
    solver = CloudQuestionSolver()

    questions_list = [
        {"question": "Where do you reside?", "type": 1},
        {"question": "Do you have experience with Kubernetes?", "type": 2},
        {"question": "Which of these tools have you used?", "type": 3, "options": ["Terraform", "Pulumi", "CloudFormation"]},
        {"question": "How many years of experience do you have with AWS?", "type": 1},
        {"question": "Are you Microsoft Certified: Azure Fundamentals?", "type": 2},
        {"question": "How many years of experience do you have with Python?", "type": 1}
    ]

    for idx, question_json in enumerate(questions_list, 1):
        print(f"\n🔹 Question {idx}: {question_json['question']}")
        try:
            result = solver.solve_question(question_json)
            print("Mei's Answer:", json.dumps(result, indent=2))
        except Exception as e:
            print(f"Error: {e}\n")
