# baseline_inference.py
import requests
import time

API_URL = "http://127.0.0.1:8000"

def reset_environment():
    """Reset the environment."""
    response = requests.post(f"{API_URL}/reset")
    return response.json()

def step_environment(urgency, action, response_draft=None):
    """Take an action."""
    payload = {
        "urgency": urgency,
        "action": action,
        "response_draft": response_draft
    }
    response = requests.post(f"{API_URL}/step", json=payload)
    return response.json()

def get_state():
    """Get current state."""
    response = requests.get(f"{API_URL}/state")
    return response.json()

def simple_agent(obs):
    """A simple rule-based agent (no OpenAI needed)."""
    # Simple logic based on email content
    email_lower = (obs["email_subject"] + " " + obs["email_body"]).lower()
    
    if "deadline" in email_lower or "urgent" in email_lower:
        return "urgent", "respond", "I will handle this urgently."
    elif "newsletter" in email_lower or "subscription" in email_lower:
        return "normal", "archive", None
    elif "complaint" in email_lower or "order" in email_lower:
        return "urgent", "respond", "I apologize for the delay. Let me investigate your order."
    else:
        return "normal", "archive", None

def run_episode():
    """Run one full episode."""
    print("\n" + "="*50)
    print("Starting Email Triage Episode")
    print("="*50)
    
    obs = reset_environment()
    total_reward = 0
    step_num = 0
    
    while not obs["done"]:
        step_num += 1
        print(f"\n--- Step {step_num} ---")
        print(f"Task: {obs['task_description']}")
        print(f"Subject: {obs['email_subject']}")
        print(f"Body: {obs['email_body'][:100]}...")
        print(f"Attempts left: {obs['attempts_remaining']}")
        
        # Get agent action
        urgency, action, draft = simple_agent(obs)
        print(f"Action: urgency={urgency}, action={action}")
        if draft:
            print(f"Response: {draft[:50]}...")
        
        # Take action
        obs = step_environment(urgency, action, draft)
        total_reward += obs["reward"] if obs["reward"] else 0
        print(f"Reward received: {obs['reward']}")
        print(f"Feedback: {obs['feedback']}")
        
        time.sleep(0.5)
    
    print(f"\n" + "="*50)
    print(f"Episode Complete!")
    print(f"Total Score: {total_reward:.2f}")
    print("="*50)
    
    # Show final state
    state = get_state()
    print(f"\nFinal State:")
    print(f"Tasks Completed: {state['total_tasks_completed']}/3")
    print(f"History: {len(state['history'])} steps taken")
    
    return total_reward

if __name__ == "__main__":
    print("Email Triage Environment - Baseline Agent Test")
    print("Make sure your server is running (uvicorn server.app:app)")
    
    try:
        score = run_episode()
        print(f"\n✅ Test completed! Score: {score:.2f}")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure server is running on http://localhost:8001")