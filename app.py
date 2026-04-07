from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import uvicorn

app = FastAPI()

class Action(BaseModel):
    urgency: str
    action: str
    response_draft: Optional[str] = None

# Store state for 3 tasks
task_index = 0
scores = []
current_task = None

# Define 3 tasks
TASKS = [
    {
        "name": "classify_urgency",
        "description": "Classify email urgency as urgent or normal",
        "email_subject": "URGENT: Server Down",
        "email_body": "The production server is not responding. Please fix immediately."
    },
    {
        "name": "choose_action", 
        "description": "Choose appropriate action (respond or archive)",
        "email_subject": "Weekly Newsletter",
        "email_body": "Check out our latest products and deals!"
    },
    {
        "name": "draft_response",
        "description": "Draft appropriate response for urgent emails",
        "email_subject": "Order #12345 - Delayed Shipping",
        "email_body": "My order hasn't arrived. Please help."
    }
]

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/reset")
def reset():
    global task_index, scores, current_task
    task_index = 0
    scores = []
    current_task = TASKS[0]
    return {
        "task_description": current_task["description"],
        "email_subject": current_task["email_subject"],
        "email_body": current_task["email_body"]
    }

@app.post("/step")
def step(action: Action):
    global task_index, scores, current_task
    
    # Calculate reward based on task type
    reward = 0.0
    task_name = TASKS[task_index]["name"]
    
    if task_name == "classify_urgency":
        if action.urgency == "urgent":
            reward = 0.95  # Between 0 and 1
        else:
            reward = 0.05
            
    elif task_name == "choose_action":
        if action.action == "respond":
            reward = 0.9
        else:
            reward = 0.1
            
    elif task_name == "draft_response":
        if action.response_draft and len(action.response_draft) > 20:
            reward = 0.85
        else:
            reward = 0.15
    
    scores.append(reward)
    
    # Move to next task
    task_index += 1
    if task_index < len(TASKS):
        current_task = TASKS[task_index]
    else:
        current_task = None
    
    return {
        "reward": reward,
        "feedback": f"Task {task_name} completed with reward {reward}"
    }

@app.get("/state")
def state():
    total_score = sum(scores) / len(TASKS) if scores else 0
    return {
        "cumulative_score": round(total_score, 2),
        "total_tasks_completed": len(scores)
    }

def main():
    uvicorn.run(app, host="0.0.0.0", port=7860)

if __name__ == "__main__":
    main()
