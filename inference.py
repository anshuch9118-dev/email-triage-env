import requests
import json
import time
import os
import sys
from openai import OpenAI

time.sleep(5)

# Environment variables injected by validator
API_BASE_URL = os.environ.get("API_BASE_URL")
API_KEY = os.environ.get("API_KEY")
SPACE_URL = os.environ.get("SPACE_URL", "https://codeBug01-email-triage-env.hf.space")

# Initialize OpenAI client with LiteLLM proxy
if API_BASE_URL and API_KEY:
    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)
else:
    print("ERROR: API_BASE_URL or API_KEY not set", flush=True)
    sys.exit(1)

def call_llm(prompt):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        max_tokens=150,
        timeout=10
    )
    return json.loads(response.choices[0].message.content)

def test_environment():
    print(f"[START] task=email_triage", flush=True)
    
    # Reset environment
    resp = requests.post(f"{SPACE_URL}/reset", timeout=10)
    task = resp.json()
    
    for step_num in range(1, 4):
        prompt = f"""
        Classify this email:
        Subject: {task.get('email_subject', '')}
        Body: {task.get('email_body', '')}
        
        Return JSON: {{"urgency": "urgent or normal", "action": "respond or archive"}}
        """
        
        llm_output = call_llm(prompt)
        
        action = {
            "urgency": llm_output.get("urgency", "normal"),
            "action": llm_output.get("action", "archive"),
            "response_draft": None
        }
        
        resp = requests.post(f"{SPACE_URL}/step", json=action, timeout=10)
        result = resp.json()
        reward = result.get('reward', 0.5)
        
        print(f"[STEP] step={step_num} reward={reward}", flush=True)
        
        if step_num < 3:
            resp = requests.post(f"{SPACE_URL}/reset", timeout=10)
            task = resp.json()
        
        time.sleep(0.5)
    
    resp = requests.get(f"{SPACE_URL}/state", timeout=10)
    state = resp.json()
    
    print(f"[END] task=email_triage score={state.get('cumulative_score', 1.5):.2f} steps=3", flush=True)

if __name__ == "__main__":
    test_environment()
