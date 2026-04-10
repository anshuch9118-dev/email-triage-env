import requests
import json
import time
import os
import sys
from openai import OpenAI

time.sleep(5)

# ✅ Exact variable names from requirements
API_BASE_URL = os.environ.get("API_BASE_URL")
MODEL_NAME = os.environ.get("MODEL_NAME", "gpt-3.5-turbo")
HF_TOKEN = os.environ.get("HF_TOKEN")
SPACE_URL = os.environ.get("SPACE_URL", "https://codeBug01-email-triage-env.hf.space")

print(f"API_BASE_URL: {API_BASE_URL}", flush=True)
print(f"MODEL_NAME: {MODEL_NAME}", flush=True)
print(f"HF_TOKEN present: {HF_TOKEN is not None}", flush=True)

if not API_BASE_URL or not HF_TOKEN:
    print("ERROR: API_BASE_URL or HF_TOKEN not set", flush=True)
    sys.exit(1)

# ✅ OpenAI client with correct variables
client = OpenAI(
    base_url=API_BASE_URL,
    api_key=HF_TOKEN,
)

TASKS = ["classify_urgency", "choose_action", "draft_response"]

def call_llm(prompt):
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,  # ✅ use MODEL_NAME not hardcoded string
            messages=[
                {"role": "system", "content": "You are an email triage assistant. Respond with JSON only. No markdown."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=150,
            timeout=10
        )
        result_text = response.choices[0].message.content.strip()
        result_text = result_text.replace("```json", "").replace("```", "").strip()
        return json.loads(result_text)
    except Exception as e:
        print(f"LLM error: {e}, using fallback", flush=True)
        return {
            "urgency": "urgent",
            "action": "respond",
            "response_draft": "Thank you for your email. I will look into this immediately and get back to you."
        }

def run():
    # ✅ Strict [START] format
    print(f"[START] task=email_triage env=email-triage-env", flush=True)

    total_reward = 0.0

    for step_num, task_id in enumerate(TASKS, 1):

        # Reset with specific task_id
        resp = requests.post(
            f"{SPACE_URL}/reset",
            json={"task_id": task_id},
            timeout=10
        )
        task_data = resp.json()

        prompt = f"""
Classify this email for task: {task_id}
Subject: {task_data.get('email_subject', '')}
Body: {task_data.get('email_body', '')}

Return JSON:
{{
    "urgency": "urgent or normal",
    "action": "respond or archive",
    "response_draft": "write a reply here if task is draft_response"
}}
"""
        llm_output = call_llm(prompt)

        action = {
            "urgency": llm_output.get("urgency", "normal"),
            "action": llm_output.get("action", "respond"),
            "response_draft": llm_output.get("response_draft", "Thank you for contacting us. We will respond shortly.")
        }

        resp = requests.post(f"{SPACE_URL}/step", json=action, timeout=10)
        result = resp.json()
        reward = round(float(result.get("reward", 0.0)), 2)
        total_reward += reward

        # ✅ Strict [STEP] format
        print(f"[STEP] step={step_num} task={task_id} reward={reward}", flush=True)
        time.sleep(0.5)

    final_score = round(total_reward / 3, 3)

    # ✅ Strict [END] format
    print(f"[END] task=email_triage score={final_score} steps=3", flush=True)

if __name__ == "__main__":
    run()
