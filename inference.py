import os
import json

# Optional LLM setup
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
    """Call LLM safely"""
    if client is None:
        return {
            "urgency": "normal",
            "action": "respond",
            "response": "Thank you for your email. We will get back to you shortly."
        }

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=150
        )

        text = response.choices[0].message.content
        return json.loads(text)

    except Exception:
        return {
            "urgency": "normal",
            "action": "respond",
            "response": "Thank you for your email. We will assist you shortly."
        }


def run(task_input: dict) -> dict:
    """
    REQUIRED ENTRYPOINT for OpenEnv
    """

    subject = task_input.get("email_subject", "")
    body = task_input.get("email_body", "")

    prompt = f"""
    You are an email assistant.

    Email Subject: {subject}
    Email Body: {body}

    Return ONLY JSON:
    {{
        "urgency": "urgent or normal",
        "action": "respond or archive",
        "response": "a professional reply"
    }}
    """

    result = call_llm(prompt)

    # ✅ Ensure correct structure (VERY IMPORTANT)
    return {
        "urgency": result.get("urgency", "normal"),
        "action": result.get("action", "respond"),
        "response": result.get(
            "response",
            "Thank you for your email. We will get back to you soon."
        )
    }
