import requests
import json
import time
import os
import sys
from openai import OpenAI

# Wait for server
time.sleep(5)

# Get environment variables from validator (CRITICAL - DO NOT HARDCODE)
API_BASE_URL = os.environ.get("API_BASE_URL")
API_KEY = os.environ.get("API_KEY")
SPACE_URL = os.environ.get("SPACE_URL", "https://codeBug01-email-triage-env.hf.space")

print(f"API_BASE_URL: {API_BASE_URL}", flush=True)
print(f"API_KEY present: {API_KEY is not None}", flush=True)

# Initialize OpenAI client with LiteLLM proxy
if not API_BASE_URL or not API_KEY:
    print("ERROR: API_BASE_URL or API_KEY not set in environment", flush=True)
    sys.exit(1)

client = OpenAI(
    base_url=API_BASE_URL,
    api_key=API_KEY,
)

def call_llm(prompt):
    """Make actual API call to LLM through proxy."""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an email triage assistant. Respond with JSON only. Example: {\"urgency\": \"urgent\", \"action\": \"respond\"}"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=100,
            timeout=10
        )
        
        result_text = response.choices[0].message.content
        print(f"LLM response: {result_text}", flush=True)
        
        # Parse JSON from response
        return json.loads(result_text)
        
    except Exception as e:
        print(f"LLM error: {e}, using fallback", flush=True)
        return {"urgency": "urgent", "action": "respond"}

def test_environment():
    print(f"[START] task=email_triage", flush=True)
    
    # Reset environment
    resp = requests.post(f"{SPACE_URL}/reset", timeout=10)
    task_data = resp.json()
    
    total_reward = 0
    
    for step_num in range(1, 4):
        # Create prompt from email
        prompt = f"""
        Classify this email:
        Subject: {task_data.get('email_subject', '')}
        Body: {task_data.get('email_body', '')}
        
        Return JSON: {{"urgency": "urgent or normal", "action": "respond or archive"}}
        """
        
        # Call LLM through proxy
        llm_output = call_llm(prompt)
        
        # Send action to environment
        action = {
            "urgency": llm_output.get("urgency", "normal"),
            "action": llm_output.get("action", "archive"),
            "response_draft": f"Auto-response for {task_data.get('task_name', 'task')}"
        }
        
        resp = requests.post(f"{SPACE_URL}/step", json=action, timeout=10)
        result = resp.json()
        reward = result.get('reward', 0.5)
        total_reward += reward
        
        print(f"[STEP] step={step_num} reward={reward}", flush=True)
        
        # Get next task if not last
        if step_num < 3:
            resp = requests.post(f"{SPACE_URL}/reset", timeout=10)
            task_data = resp.json()
        
        time.sleep(0.5)
    
    # Get final state
    resp = requests.get(f"{SPACE_URL}/state", timeout=10)
    state = resp.json()
    final_score = state.get('cumulative_score', total_reward / 3)
    
    print(f"[END] task=email_triage score={final_score:.2f} steps=3", flush=True)

if __name__ == "__main__":
    test_environment()
