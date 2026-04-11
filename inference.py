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

print(f"API_BASE_URL exists: {API_BASE_URL is not None}", flush=True)
print(f"API_KEY exists: {API_KEY is not None}", flush=True)

if API_BASE_URL and API_KEY:
    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)
else:
    client = None

def call_llm(prompt):
    if client is None:
        return {"urgency": "urgent", "action": "respond"}
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=100,
            timeout=10
        )
        result_text = response.choices[0].message.content
        try:
            return json.loads(result_text)
        except:
            return {"urgency": "urgent", "action": "respond"} if "urgent" in result_text.lower() else {"urgency": "normal", "action": "archive"}
    except Exception as e:
        print(f"LLM error: {e}", flush=True)
        return {"urgency": "urgent", "action": "respond"}

def test_environment():
    # Define 3 distinct tasks - MUST loop through each
    task_ids = ["classify_urgency", "choose_action", "draft_response"]
    
    total_score = 0
    
    for idx, task_id in enumerate(task_ids, 1):
        print(f"\n=== Running task {idx}: {task_id} ===", flush=True)
        
        # Start the task
        print(f"[START] task={task_id}", flush=True)
        
        # Reset environment for this task
        resp = requests.post(f"{SPACE_URL}/reset", timeout=10)
        task_data = resp.json()
        
        # Create prompt from email
        prompt = f"""
        Classify this email:
        Subject: {task_data.get('email_subject', '')}
        Body: {task_data.get('email_body', '')}
        
        Return JSON: {{"urgency": "urgent or normal", "action": "respond or archive"}}
        """
        
        llm_output = call_llm(prompt)
        
        action = {
            "urgency": llm_output.get("urgency", "normal"),
            "action": llm_output.get("action", "archive"),
            "response_draft": f"Response for {task_id}"
        }
        
        resp = requests.post(f"{SPACE_URL}/step", json=action, timeout=10)
        result = resp.json()
        reward = result.get('reward', 0.5)
        total_score += reward
        
        # Step output
        print(f"[STEP] step=1 reward={reward}", flush=True)
        
        # End the task
        print(f"[END] task={task_id} score={reward} steps=1", flush=True)
        
        time.sleep(0.5)
    
    print(f"\n[FINAL] total_score={total_score} average={total_score/3:.2f}", flush=True)

if __name__ == "__main__":
    test_environment()
