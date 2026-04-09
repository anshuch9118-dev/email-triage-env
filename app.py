from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import uvicorn

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

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/reset")
def reset():
    global task_count, total_reward
    task_count = 0
    total_reward = 0.0
    task = TASKS[0]
    return {
        "task_name": task["name"],
        "task_description": f"Process {task['name']}",
        "email_subject": task["subject"],
        "email_body": task["body"]
    }

@app.post("/step")
def step(action: Action):
    global task_count, total_reward
    task_count += 1
    
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
