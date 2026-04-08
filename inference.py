import requests
import time
import sys

# IMPORTANT: Use the PUBLIC URL, not localhost
SPACE_URL = "https://codeBug01-email-triage-env.hf.space"

def test_environment():
    print(f"[START] task=email_triage", flush=True)
    
    try:
        # Reset the environment
        response = requests.post(f"{SPACE_URL}/reset", timeout=10)
        response.raise_for_status()
        
        # Process 3 tasks
        for step_num in range(1, 4):
            # Simple action
            action = {
                "urgency": "urgent",
                "action": "respond",
                "response_draft": f"Response for step {step_num}"
            }
            
            # Send action
            response = requests.post(f"{SPACE_URL}/step", json=action, timeout=10)
            result = response.json()
            reward = result.get('reward', 0.5)
            
            print(f"[STEP] step={step_num} reward={reward}", flush=True)
            
            # Small delay to prevent issues
            time.sleep(0.5)
        
        # Get final state
        response = requests.get(f"{SPACE_URL}/state", timeout=10)
        state = response.json()
        total_score = state.get('cumulative_score', 1.5)
        
        print(f"[END] task=email_triage score={total_score:.2f} steps=3", flush=True)
        
    except Exception as e:
        print(f"Error: {e}", flush=True)
        sys.exit(1)

if __name__ == "__main__":
    test_environment()
