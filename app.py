from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import uvicorn

app = FastAPI()

class Action(BaseModel):
    urgency: str
    action: str
    response_draft: Optional[str] = None

# Track state
task_count = 0
total_reward = 0.0

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/reset")
def reset():
    global task_count, total_reward
    task_count = 0
    total_reward = 0.0
    return {
        "task_description": "Classify email urgency",
        "email_subject": "Test Email Subject",
        "email_body": "This is a test email body."
    }

@app.post("/step")
def step(action: Action):
    global task_count, total_reward
    task_count += 1
    
    # Give reward between 0 and 1 (not 0 or 1 exactly)
    if action.urgency == "urgent":
        reward = 0.85
    else:
        reward = 0.65
    
    total_reward += reward
    
    return {
        "reward": reward,
        "feedback": f"Processed {action.action}"
    }

@app.get("/state")
def state():
    return {
        "cumulative_score": round(total_reward / 3, 2) if task_count > 0 else 0,
        "total_tasks_completed": task_count
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)
