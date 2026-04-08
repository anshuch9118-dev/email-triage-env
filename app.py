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
current_task_index = 0
task_scores = []
total_reward = 0.0

# Define 3 tasks with names matching openenv.yaml
TASKS = [
    {
        "name": "classify_urgency",
        "description": "Classify email urgency as urgent or normal",
        "email_subject": "URGENT: Server Down - Immediate Action Required",
        "email_body": "The production server is not responding. Customers cannot access the website. Please investigate immediately."
    },
    {
        "name": "choose_action",
        "description": "Choose appropriate action (respond or archive)",
        "email_subject": "Weekly Product Newsletter",
        "email_body": "Check out our latest products and exclusive deals for this week only!"
    },
    {
        "name": "draft_response",
        "description": "Draft appropriate response for customer email",
        "email_subject": "Order #ORD-12345 - Shipping Delay Complaint",
        "email_body": "I ordered 2 weeks ago and still haven't received my package. The tracking number doesn't work. Please help me resolve this."
    }
]

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/reset")
def reset():
    global current_task_index, task_scores, total_reward
    current_task_index = 0
    task_scores = []
    total_reward = 0.0
    
    task = TASKS[current_task_index]
    return {
        "task_name": task["name"],  # CRITICAL: Must match openenv.yaml
        "task_description": task["description"],
        "email_subject": task["email_subject"],
        "email_body": task["email_body"]
    }

@app.post("/step")
def step(action: Action):
    global current_task_index, task_scores, total_reward
    
    if current_task_index >= len(TASKS):
        return {
            "reward": 0.0,
            "feedback": "All tasks completed"
        }
    
    task = TASKS[current_task_index]
    task_name = task["name"]
    
    # Calculate reward based on task name and action
    if task_name == "classify_urgency":
        if action.urgency == "urgent":
            reward = 0.95
        elif action.urgency == "normal":
            reward = 0.85
        else:
            reward = 0.30
            
    elif task_name == "choose_action":
        if action.action == "respond" and action.urgency == "urgent":
            reward = 0.90
        elif action.action == "archive" and action.urgency == "normal":
            reward = 0.80
        else:
            reward = 0.20
            
    elif task_name == "draft_response":
        if action.response_draft and len(action.response_draft) > 50:
            reward = 0.88
        elif action.response_draft and len(action.response_draft) > 20:
            reward = 0.55
        else:
            reward = 0.15
    else:
        reward = 0.50
    
    task_scores.append(reward)
    total_reward += reward
    
    # Move to next task
    current_task_index += 1
    
    return {
        "reward": reward,
        "feedback": f"Task '{task_name}' completed with reward {reward}",
        "task_completed": task_name,
        "remaining_tasks": len(TASKS) - current_task_index
    }

@app.get("/state")
def state():
    if task_scores:
        cumulative_score = sum(task_scores) / len(TASKS)
    else:
        cumulative_score = 0.0
    
    return {
        "cumulative_score": round(cumulative_score, 2),
        "total_tasks_completed": len(task_scores),
        "tasks_completed": task_scores
    }

def main():
    uvicorn.run(app, host="0.0.0.0", port=7860)

if __name__ == "__main__":
    main()
    
