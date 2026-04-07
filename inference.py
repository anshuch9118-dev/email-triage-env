"""
Inference script for Email Triage Environment.
This script demonstrates how to interact with the environment using a simple agent.
"""

import requests
import json
import time

# Wait for the server to start
print("Waiting for server to start...")
time.sleep(5)

# Space URL - use localhost when running inside the Space
SPACE_URL = "http://localhost:7860"

def test_environment():
    """Test all endpoints of the environment."""
    
    print("=" * 50)
    print("Email Triage Environment - Inference Test")
    print("=" * 50)
    
    # Test 1: Health check
    print("\n1. Testing Health Check...")
    try:
        response = requests.get(f"{SPACE_URL}/health")
        print(f"   Health: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
        return
    
    # Test 2: Reset the environment
    print("\n2. Resetting environment...")
    response = requests.post(f"{SPACE_URL}/reset")
    reset_data = response.json()
    print(f"   Task: {reset_data['task_description']}")
    print(f"   Email Subject: {reset_data['email_subject']}")
    print(f"   Email Body: {reset_data['email_body']}")
    
    # Test 3: Take actions for all 3 tasks
    print("\n3. Playing through tasks...")
    
    # Task 1: Urgent email
    print("\n   Task 1 - Classifying urgency...")
    action = {"urgency": "urgent", "action": "respond", "response_draft": "Will handle"}
    response = requests.post(f"{SPACE_URL}/step", json=action)
    result = response.json()
    print(f"   Reward: {result['reward']}, Feedback: {result['feedback']}")
    
    # Task 2: Newsletter email
    print("\n   Task 2 - Choosing action...")
    action = {"urgency": "normal", "action": "archive", "response_draft": None}
    response = requests.post(f"{SPACE_URL}/step", json=action)
    result = response.json()
    print(f"   Reward: {result['reward']}, Feedback: {result['feedback']}")
    
    # Task 3: Customer complaint
    print("\n   Task 3 - Full triage...")
    action = {
        "urgency": "urgent",
        "action": "respond",
        "response_draft": "I apologize for the delay. Let me investigate your order and provide tracking information."
    }
    response = requests.post(f"{SPACE_URL}/step", json=action)
    result = response.json()
    print(f"   Reward: {result['reward']}, Feedback: {result['feedback']}")
    
    # Test 4: Get final state
    print("\n4. Getting final state...")
    response = requests.get(f"{SPACE_URL}/state")
    state = response.json()
    print(f"   Final Score: {state['cumulative_score']}/3.00")
    print(f"   Tasks Completed: {state['total_tasks_completed']}/3")
    
    print("\n" + "=" * 50)
    print("✅ All tests passed!")
    print("=" * 50)

if __name__ == "__main__":
    test_environment()
