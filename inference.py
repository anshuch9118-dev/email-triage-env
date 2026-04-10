import requests
import json
import time
import os
import sys
from openai import OpenAI

time.sleep(5)

API_BASE_URL = os.environ.get("API_BASE_URL")
API_KEY = os.environ.get("API_KEY")
SPACE_URL = os.environ.get("SPACE_URL", "https://codeBug01-email-triage-env.hf.space")

print(f"API_BASE_URL: {API_BASE_URL}", flush=True)
print(f"API_KEY present: {API_KEY is not None}", flush=True)

if not API_BASE_URL or not API_KEY:
    print("ERROR: API_BASE_URL or API_KEY not set", flush=True)
    sys.exit(1)

client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)

# ✅ All 3 tasks explicitly defined
TASKS = ["classify_urgency", "choose_action", "draft_response"]

def call_llm(prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an email triage assistant. Respond with JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=150,
            timeout=10
        )
        result_text = response.choices[0].message.content
        print(f"LLM response: {result_text}", flush=True)
        return json.loads(result_text)
    except Exception as e:
        print(f"LLM error: {e}, using fallback", flush=True)
        return {"urgency": "urgent", "action": "respond", "response_draft": "Thank you for your email. I will look into this immediately."}

def run():
    print(f"[START] task=email_triage", flush=True)

    total_reward = 0.0

    # ✅ Loop through each task explicitly
    for step_num, task_id in enumerate(TASKS, 1):

        # Reset with specific task_id
        resp = requests.post(
            f"{SPACE_URL}/reset",
            json={"task_id": task_id},
            timeout=10
        )
        task_data = resp.json()
        print(f"[TASK] step={step_num} task_id={task_id}", flush=True)

        # Build prompt
        prompt = f"""
        Classify this email:
        Subject: {task_data.get('email_subject', '')}
        Body: {task_data.get('email_body', '')}
        Task: {task_id}

        Return JSON with all fields:
        {{
            "urgency": "urgent or normal",
            "action": "respond or archive",
            "response_draft": "your response here if drafting"
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
        reward = result.get("reward", 0.0)
        total_reward += reward

        print(f"[STEP] step={step_num} task={task_id} reward={reward}", flush=True)
        time.sleep(0.5)

    final_score = round(total_reward / 3, 3)
    print(f"[END] task=email_triage score={final_score} steps=3", flush=True)

# ✅ Both entrypoints work
if __name__ == "__main__":
    run()
