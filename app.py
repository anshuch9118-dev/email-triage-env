from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from typing import Optional
import uvicorn
import os

app = FastAPI()

# --- Models ---
class Action(BaseModel):
    urgency: Optional[str] = ""
    action: Optional[str] = ""
    response_draft: Optional[str] = None

class ResetRequest(BaseModel):
    task_id: Optional[str] = "classify_urgency"

class GraderRequest(BaseModel):
    task_id: Optional[str] = None
    episode_id: Optional[str] = None
    answer: Optional[str] = None
    urgency: Optional[str] = None
    action: Optional[str] = None
    response_draft: Optional[str] = None

# --- Task definitions ---
TASKS = {
    "classify_urgency": {
        "name": "Classify Email Urgency",
        "description": "Easy: Classify email as urgent or normal",
        "subject": "URGENT: Server Down",
        "body": "The production server is not responding.",
        "difficulty": "easy"
    },
    "choose_action": {
        "name": "Choose Email Action",
        "description": "Medium: Choose correct action for email",
        "subject": "Weekly Newsletter",
        "body": "Check out our latest products!",
        "difficulty": "medium"
    },
    "draft_response": {
        "name": "Draft Email Response",
        "description": "Hard: Draft a response to a customer email",
        "subject": "Order #12345",
        "body": "My order hasn't arrived. Please help.",
        "difficulty": "hard"
    },
}

current_task_id = "classify_urgency"

# --- Grader functions ---
def grade_classify_urgency(data: dict) -> float:
    urgency = data.get("urgency", "")
    if isinstance(urgency, str) and urgency.lower() in ["urgent", "normal"]:
        return 0.95
    return 0.1

def grade_choose_action(data: dict) -> float:
    action = data.get("action", "")
    if isinstance(action, str) and action.lower() in ["respond", "archive", "escalate", "delete"]:
        return 0.92
    return 0.1

def grade_draft_response(data: dict) -> float:
    draft = data.get("response_draft", "") or data.get("answer", "")
    if draft and len(str(draft)) > 10:
        return 0.95
    return 0.1

GRADERS = {
    "classify_urgency": grade_classify_urgency,
    "choose_action": grade_choose_action,
    "draft_response": grade_draft_response,
}

# --- Endpoints ---
@app.get("/")
@app.get("/health")
def health():
    return {"status": "healthy", "service": "email-triage-env"}

@app.get("/tasks")
def list_tasks():
    return {
        "tasks": [
            {
                "id": "classify_urgency",
                "name": "Classify Email Urgency",
                "description": "Easy: Classify email as urgent or normal",
                "difficulty": "easy",
                "grader": {"type": "function", "endpoint": "/grader"}
            },
            {
                "id": "choose_action",
                "name": "Choose Email Action",
                "description": "Medium: Choose correct action for email",
                "difficulty": "medium",
                "grader": {"type": "function", "endpoint": "/grader"}
            },
            {
                "id": "draft_response",
                "name": "Draft Email Response",
                "description": "Hard: Draft a response to customer email",
                "difficulty": "hard",
                "grader": {"type": "function", "endpoint": "/grader"}
            },
        ]
    }

@app.post("/reset")
def reset(req: ResetRequest = None):
    global current_task_id
    task_id = req.task_id if req and req.task_id in TASKS else "classify_urgency"
    current_task_id = task_id
    task = TASKS[task_id]
    return {
        "task_id": task_id,
        "task_name": task["name"],
        "task_description": task["description"],
        "email_subject": task["subject"],
        "email_body": task["body"],
        "done": False,
        "reward": 0.0,
    }

@app.post("/step")
def step(action: Action):
    global current_task_id
    data = {
        "urgency": action.urgency,
        "action": action.action,
        "response_draft": action.response_draft,
    }
    grader = GRADERS.get(current_task_id)
    reward = grader(data) if grader else 0.1
    return {
        "reward": round(reward, 3),
        "done": True,
        "feedback": "Processed",
        "score": round(reward, 3),
    }

@app.get("/state")
def state():
    return {
        "status": "active",
        "current_task": current_task_id,
        "tasks_available": list(TASKS.keys()),
    }

@app.post("/grader")
def grader(req: GraderRequest):
    task_id = req.task_id or current_task_id
    if task_id not in GRADERS:
        return {"score": 0.0, "error": f"Unknown task: {task_id}"}
    data = {
        "urgency": req.urgency or "",
        "action": req.action or "",
        "response_draft": req.response_draft or req.answer or "",
        "answer": req.answer or "",
    }
    score = GRADERS[task_id](data)
    return {
        "task_id": task_id,
        "score": round(score, 3),
        "reward": round(score, 3),
        "graded": True,
    }

@app.get("/openenv.yaml", response_class=PlainTextResponse)
def serve_yaml():
    return """id: email-triage-env-v1
name: Email Triage Environment
version: 1.0.0
type: environment
sdk: openenv
description: Real-world email triage RL environment with 3 tasks.
entrypoint: app:app
author: codeBug01
"""

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    uvicorn.run(app, host="0.0.0.0", port=port)
