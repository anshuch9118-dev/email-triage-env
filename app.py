from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uvicorn
import os
import json

app = FastAPI()

class Action(BaseModel):
    urgency: str
    action: str
    response_draft: Optional[str] = None

class TaskState:
    def __init__(self):
        self.current_task = 0
        self.scores = []
        self.completed_tasks = []
        
    def reset(self):
        self.current_task = 0
        self.scores = []
        self.completed_tasks = []

state = TaskState()

TASKS = [
    {
        "id": "task1",
        "name": "classify_urgency",
        "description": "Classify email urgency",
        "email": {
            "subject": "URGENT: Server Down - Immediate Action Required",
            "body": "The production server is not responding. Customers cannot access the website. Please investigate immediately."
        }
    },
    {
        "id": "task2",
        "name": "choose_action",
        "description": "Choose appropriate action",
        "email": {
            "subject": "Weekly Product Newsletter",
            "body": "Check out our latest products and exclusive deals for this week only!"
        }
    },
    {
        "id": "task3",
        "name": "draft_response",
        "description": "Draft professional response",
        "email": {
            "subject": "Order #ORD-12345 - Shipping Delay Complaint",
            "body": "I ordered 2 weeks ago and still haven't received my package. The tracking number doesn't work. Please help me resolve this."
        }
    }
]

@app.get("/health")
async def health():
    return {"status": "healthy", "tasks_available": len(TASKS)}

@app.post("/reset")
async def reset():
    state.reset()
    task = TASKS[state.current_task]
    return {
        "task_id": task["id"],
        "task_name": task["name"],
        "task_description": task["description"],
        "email_subject": task["email"]["subject"],
        "email_body": task["email"]["body"]
    }

@app.post("/step")
async def step(action: Action):
    if state.current_task >= len(TASKS):
        raise HTTPException(status_code=400, detail="All tasks completed")
    
    task = TASKS[state.current_task]
    task_id = task["id"]
    
    # Calculate reward based on task type
    if task_id == "task1":
        if action.urgency == "urgent":
            reward = 0.95
        elif action.urgency == "normal":
            reward = 0.85
        else:
            reward = 0.3
            
    elif task_id == "task2":
        if action.action == "respond" and action.urgency == "urgent":
            reward = 0.9
        elif action.action == "archive" and action.urgency == "normal":
            reward = 0.8
        else:
            reward = 0.2
            
    elif task_id == "task3":
        if action.response_draft and len(action.response_draft) > 50:
            reward = 0.88
        elif action.response_draft and len(action.response_draft) > 20:
            reward = 0.55
        else:
            reward = 0.15
    
    state.scores.append(reward)
    state.completed_tasks.append(task_id)
    state.current_task += 1
    
    return {
        "reward": reward,
        "feedback": f"Task {task_id} completed with reward {reward}",
        "task_completed": task_id,
        "remaining_tasks": len(TASKS) - state.current_task
    }

@app.get("/state")
async def get_state():
    if state.scores:
        cumulative_score = sum(state.scores) / len(TASKS)
    else:
        cumulative_score = 0.0
    
    return {
        "cumulative_score": round(cumulative_score, 2),
        "total_tasks_completed": len(state.completed_tasks),
        "completed_task_ids": state.completed_tasks,
        "scores_per_task": state.scores
    }

def main():
    uvicorn.run(app, host="0.0.0.0", port=7860)

if __name__ == "__main__":
    main()
