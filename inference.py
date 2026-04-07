"""
Inference script for Email Triage Environment with structured output.
"""

import requests
import json
import time
import sys

# Wait for server to start
time.sleep(5)

SPACE_URL = "http://localhost:7860"

def test_environment():
    """Test all endpoints with structured output."""
    
    # Test 1: Health check
    response = requests.get(f"{SPACE_URL}/health")
    
    # Test 2: Reset environment
    response = requests.post(f"{SPACE_URL}/reset")
    reset_data = response.json()
    
    # Print START block
    print(f"[START] task=email_triage", flush=True)
    
    # Task 1: Urgent email
    action1 = {"urgency": "urgent", "action": "respond", "response_draft": "Will handle"}
    response = requests.post(f"{SPACE_URL}/step", json=action1)
    result1 = response.json()
    print(f"[STEP] step=1 reward={result1['reward']}", flush=True)
    
    # Task 2: Newsletter email
    action2 = {"urgency": "normal", "action": "archive", "response_draft": None}
    response = requests.post(f"{SPACE_URL}/step", json=action2)
    result2 = response.json()
    print(f"[STEP] step=2 reward={result2['reward']}", flush=True)
    
    # Task 3: Customer complaint
    action3 = {
        "urgency": "urgent",
        "action": "respond",
        "response_draft": "I apologize for the delay. Let me investigate your order."
    }
    response = requests.post(f"{SPACE_URL}/step", json=action3)
    result3 = response.json()
    print(f"[STEP] step=3 reward={result3['reward']}", flush=True)
    
    # Get final state
    response = requests.get(f"{SPACE_URL}/state")
    state = response.json()
    
    # Calculate total score
    total_score = state['cumulative_score']
    total_steps = state['total_tasks_completed']
    
    # Print END block
    print(f"[END] task=email_triage score={total_score} steps={total_steps}", flush=True)

if __name__ == "__main__":
    test_environment()
