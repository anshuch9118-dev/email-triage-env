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

if not API_BASE_URL or not API_KEY:
    print("ERROR: API_BASE_URL or API_KEY not set", flush=True)
    sys.exit(1)

client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)

def call_llm(prompt):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        max_tokens=100,
        timeout=10
    )
    return json.loads(response.choices[0].message.content)

def test_environment():
    print(f"[START] task=email_triage", flush=True)
    
    resp = requests.post(f"{SPACE_URL}/reset", timeout=10)
    task_data = resp.json()
    total_reward = 0
    
    for step_num in range(1, 4):
        prompt = f"Classify this email: Subject: {task_data.get('email_subject', '')} Body: {task_data.get('email_body', '')}. Return JSON: {{'urgency': 'urgent or normal', 'action': 'respond or archive'}}"
        
        llm_output = call_llm(prompt)
        action = {
            "urgency": llm_output.get("urgency", "normal"),
            "action": llm_output.get("action", "archive"),
            "response_draft": f"Response for {task_data.get('task_name', 'task')}"
        }
        
        resp = requests.post(f"{SPACE_URL}/step", json=action, timeout=10)
        reward = resp.json().get('reward', 0.5)
        total_reward += reward
        print(f"[STEP] step={step_num} reward={reward}", flush=True)
        
        if step_num < 3:
            resp = requests.post(f"{SPACE_URL}/reset", timeout=10)
            task_data = resp.json()
        time.sleep(0.5)
    
    resp = requests.get(f"{SPACE_URL}/state", timeout=10)
    final_score = resp.json().get('cumulative_score', total_reward / 3)
    print(f"[END] task=email_triage score={final_score:.2f} steps=3", flush=True)

if __name__ == "__main__":
    test_environment()
