import requests
import time
import sys

SPACE_URL = "https://codeBug01-email-triage-env.hf.space"

def test_environment():
    print(f"[START] task=email_triage", flush=True)
    
    try:
        # Reset environment
        resp = requests.post(f"{SPACE_URL}/reset", timeout=10)
        resp.raise_for_status()
        
        total_reward = 0
        
        # Process 3 tasks
        for step_num in range(1, 4):
            action = {
                "urgency": "urgent",
                "action": "respond",
                "response_draft": f"Response for step {step_num}"
            }
            
            resp = requests.post(f"{SPACE_URL}/step", json=action, timeout=10)
            result = resp.json()
            reward = result.get('reward', 0.5)
            total_reward += reward
            
            print(f"[STEP] step={step_num} reward={reward}", flush=True)
            time.sleep(0.5)
        
        print(f"[END] task=email_triage score={total_reward/3:.2f} steps=3", flush=True)
        
    except Exception as e:
        print(f"Error: {e}", flush=True)
        sys.exit(1)

if __name__ == "__main__":
    test_environment()
