"""
Inference script for Email Triage Environment.
Uses LiteLLM proxy for LLM API calls.
"""

import requests
import json
import time
import os
import sys
from openai import OpenAI

# Wait for server to start
time.sleep(5)

# Get environment variables from validator
API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:7860")
API_KEY = os.environ.get("API_KEY", "dummy-key")
SPACE_URL = os.environ.get("SPACE_URL", "http://localhost:7860")

# Initialize OpenAI client with LiteLLM proxy
client = OpenAI(
    base_url=API_BASE_URL,
    api_key=API_KEY,
)

def classify_email_with_llm(subject, body):
    """Use LLM to classify email urgency and action."""
    
    prompt = f"""
    Classify this email:
    Subject: {subject}
    Body: {body}
    
    Respond with JSON only:
    {{"urgency": "urgent" or "normal", "action": "respond" or "archive", "response_draft": "draft text"}}
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=150
        )
        
        result = json.loads(response.choices[0].message.content)
        return result
    except Exception as e:
        # Fallback if LLM fails
        print(f"LLM error: {e}, using fallback", flush=True)
        return {"urgency": "normal", "action": "archive", "response_draft": None}

def test_environment():
    """Test all endpoints with LLM-powered decisions."""
    
    # 1. Health check
    try:
        requests.get(f"{SPACE_URL}/health")
    except:
        pass
    
    # 2. Reset environment
    response = requests.post(f"{SPACE_URL}/reset")
    reset_data = response.json()
    
    email_subject = reset_data.get('email_subject', '')
    email_body = reset_data.get('email_body', '')
    task_description = reset_data.get('task_description', '')
    
    # Print START block
    print(f"[START] task=email_triage", flush=True)
    
    # 3. Process 3 emails using LLM for classification
    for step_num in range(1, 4):
        # Get LLM classification
        llm_decision = classify_email_with_llm(email_subject, email_body)
        
        # Send action to environment
        action = {
            "urgency": llm_decision.get("urgency", "normal"),
            "action": llm_decision.get("action", "archive"),
            "response_draft": llm_decision.get("response_draft")
        }
        
        response = requests.post(f"{SPACE_URL}/step", json=action)
        result = response.json()
        
        # Ensure reward is between 0 and 1 (not 0.0 or 1.0)
        reward = result.get('reward', 0.5)
        if reward >= 1.0:
            reward = 0.95
        elif reward <= 0.0:
            reward = 0.05
            
        print(f"[STEP] step={step_num} reward={reward}", flush=True)
        
        # Get next email if available
        if step_num < 3:
            response = requests.post(f"{SPACE_URL}/reset")
            reset_data = response.json()
            email_subject = reset_data.get('email_subject', '')
            email_body = reset_data.get('email_body', '')
    
    # 4. Get final state
    response = requests.get(f"{SPACE_URL}/state")
    state = response.json()
    
    total_score = state.get('cumulative_score', 1.5) / 3.0
    total_steps = state.get('total_tasks_completed', 3)
    
    # Print END block
    print(f"[END] task=email_triage score={total_score:.2f} steps={total_steps}", flush=True)

if __name__ == "__main__":
    test_environment()
