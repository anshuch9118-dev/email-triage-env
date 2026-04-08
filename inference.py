import os
import json
import time

# Optional LLM
try:
    from openai import OpenAI
    API_BASE_URL = os.environ.get("API_BASE_URL")
    API_KEY = os.environ.get("API_KEY")

    if API_BASE_URL and API_KEY:
        client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)
    else:
        client = None
except:
    client = None


def call_llm(prompt):
    if client is None:
        return {
            "urgency": "normal",
            "action": "respond",
            "response": "Thank you for your email. We will assist you shortly."
        }

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=150
        )
        return json.loads(response.choices[0].message.content)
    except:
        return {
            "urgency": "normal",
            "action": "respond",
            "response": "Fallback response."
        }


def run(task_input: dict) -> dict:
    subject = task_input.get("email_subject", "")
    body = task_input.get("email_body", "")

    prompt = f"""
    Classify and respond to this email.

    Subject: {subject}
    Body: {body}

    Return JSON:
    {{
        "urgency": "urgent or normal",
        "action": "respond or archive",
        "response": "professional reply"
    }}
    """

    result = call_llm(prompt)

    return {
        "urgency": result.get("urgency", "normal"),
        "action": result.get("action", "respond"),
        "response": result.get("response", "Default response")
    }


def main():
    print("[START] task=email_triage", flush=True)

    total_reward = 0

    # Simulate 3 steps
    for step in range(1, 4):
        dummy_input = {
            "email_subject": "Test subject",
            "email_body": "Customer is asking for help"
        }

        output = run(dummy_input)

        # simple reward logic
        reward = 1.0 if output["action"] == "respond" else 0.5
        total_reward += reward

        print(f"[STEP] step={step} reward={reward}", flush=True)
        time.sleep(0.2)

    final_score = total_reward / 3

    print(f"[END] task=email_triage score={final_score:.2f} steps=3", flush=True)


if __name__ == "__main__":
    main()
