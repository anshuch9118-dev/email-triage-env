from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import uvicorn
import os

app = FastAPI()

class Action(BaseModel):
    urgency: Optional[str] = ""
    action: Optional[str] = ""
    response_draft: Optional[str] = None

class ResetRequest(BaseModel):
    task_id: Optional[str] = "classify_urgency"

TASKS = {
    "classify_urgency": {"subject": "URGENT: Server Down",   "body": "Server not responding"},
    "choose_action":    {"subject": "Weekly Newsletter",      "body": "Check our products"},
    "draft_response":   {"subject": "Order #12345",           "body": "My order hasn't arrived"},
}

current_task_id = "classify_urgency"

@app.get("/")
@app.get("/health")
def health():
    return {"status": "healthy", "tasks_found": 3}

@app.post("/reset")
def reset(req: ResetRequest = None):
    global current_task_id
    task_id = req.task_id if req and req.task_id in TASKS else "classify_urgency"
    current_task_id = task_id
    task = TASKS[task_id]
    return {
        "task_id":       task_id,
        "task_name":     task_id,
        "email_subject": task["subject"],
        "email_body":    task["body"],
    }

@app.post("/step")
def step(action: Action):
    global current_task_id
    reward = 0.0

    if current_task_id == "classify_urgency":
        reward = 0.95 if action.urgency in ["urgent", "normal"] else 0.1

    elif current_task_id == "choose_action":
        reward = 0.92 if action.action in ["respond", "archive"] else 0.1

    elif current_task_id == "draft_response":
        reward = 0.95 if action.response_draft and len(action.response_draft) > 10 else 0.1

    return {"reward": round(reward, 3), "done": True, "feedback": "Processed"}

@app.get("/state")
def state():
    return {"status": "active", "current_task": current_task_id}

@app.get("/tasks")
def list_tasks():
    # Some validators call this endpoint to discover tasks
    return {
        "tasks": [
            {"id": "classify_urgency", "name": "Classify Email Urgency"},
            {"id": "choose_action",    "name": "Choose Email Action"},
            {"id": "draft_response",   "name": "Draft Email Response"},
        ]
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    uvicorn.run(app, host="0.0.0.0", port=port)
