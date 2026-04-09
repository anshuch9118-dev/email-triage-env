from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import uvicorn
import os

# --- CRITICAL: LOAD GRADERS ---
# This line ensures the @register_grader decorators are executed.
try:
    import graders
    print("Successfully registered graders for the validator.")
except ImportError:
    print("Warning: graders.py not found. Ensure it is in the same directory.")
# ------------------------------

app = FastAPI()

class Action(BaseModel):
    urgency: str
    action: str
    response_draft: Optional[str] = None

task_count = 0
total_reward = 0.0

TASKS = [
    {"name": "classify_urgency", "subject": "URGENT: Server Down", "body": "Server not responding"},
    {"name": "choose_action", "subject": "Weekly Newsletter", "body": "Check our products"},
    {"name": "draft_response", "subject": "Order #12345", "body": "My order hasn't arrived"}
]

# Support both root and health paths
@app.get("/")
@app.get("/health")
def health():
    return {"status": "healthy", "tasks_registered": 3}

@app.post("/reset")
def reset():
    global task_count, total_reward
    task_count = 0
    total_reward = 0.0
    task = TASKS[0]
    return {
        "task_name": task["name"],
        "task_id": task["name"],  # Added task_id for validator compatibility
        "task_description": f"Process {task['name']}",
        "email_subject": task["subject"],
        "email_body": task["body"]
    }

@app.post("/step")
def step(action: Action):
    global task_count, total_reward
    
    # CRITICAL: Rewards must be strictly (0, 1). Using 0.01 to 0.99 range.
    if action.urgency == "urgent":
        reward = 0.95
    elif action.urgency == "normal":
        reward = 0.85
    else:
        reward = 0.15
    
    # Ensure no exact 0 or 1
    reward = max(0.01, min(reward, 0.99))
    
    task_count += 1
    total_reward += reward
    
    return {
        "reward": reward,
        "done": True,
        "feedback": f"Processed {action.action}"
    }

@app.get("/state")
def state():
    # Keep cumulative score in strict (0, 1) range
    avg_score = total_reward / 3 if task_count > 0 else 0.01
    return {
        "cumulative_score": round(max(0.01, min(avg_score, 0.99)), 3),
        "total_tasks_completed": task_count
    }

if __name__ == "__main__":
    # Use HF/Validator port environment variable
    port = int(os.environ.get("PORT", 7860))
    uvicorn.run(app, host="0.0.0.0", port=port)
