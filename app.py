from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import uvicorn
import os

app = FastAPI()

class Action(BaseModel):
    urgency: str
    action: str
    response_draft: Optional[str] = None

# Global state for validation
current_task_index = 0
task_scores = []
total_reward = 0.0

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

# Health check endpoints for both / and /health
@app.get("/")
@app.get("/health")
def health():
    return {"status": "healthy", "tasks_count": len(TASKS)}

@app.post("/reset")
def reset():
    global current_task_index, task_scores, total_reward
    current_task_index = 0
    task_scores = []
    total_reward = 0.0
    
    task = TASKS[current_task_index]
    return {
        "task_name": task["name"],
        "task_description": task["description"],
        "email_subject": task["email_subject"],
        "email_body": task["email_body"],
        "task_id": task["name"]
    }

@app.post("/step")
def step(action: Action):
    global current_task_index, task_scores, total_reward
    
    if current_task_index >= len(TASKS):
        return {"reward": 0.01, "feedback": "Done", "all_tasks_completed": True}
    
    task = TASKS[current_task_index]
    task_name = task["name"]
    
    # CRITICAL: Rewards are strictly (0, 1) - No 1.0 or 0.0 allowed
    reward = 0.05 # Default low reward
    
    if task_name == "classify_urgency":
        reward = 0.98 if action.urgency == "urgent" else 0.85
            
    elif task_name == "choose_action":
        if action.action == "respond":
            reward = 0.92
        else:
            reward = 0.82
            
    elif task_name == "draft_response":
        if action.response_draft and len(action.response_draft) > 10:
            reward = 0.95
        else:
            reward = 0.15
    
    # Ensure reward is never exactly 0 or 1
    reward = max(0.01, min(reward, 0.99))
    
    task_scores.append(reward)
    total_reward += reward
    current_task_index += 1
    
    return {
        "reward": reward,
        "task_completed": task_name,
        "next_task": TASKS[current_task_index]["name"] if current_task_index < len(TASKS) else None
    }

@app.get("/state")
def state():
    # Strict range check for state score too
    avg_score = sum(task_scores) / len(TASKS) if task_scores else 0.01
    avg_score = max(0.01, min(avg_score, 0.99))
    
    return {
        "cumulative_score": round(avg_score, 3),
        "total_tasks_completed": len(task_scores)
    }

if __name__ == "__main__":
    # Hugging Face and the Validator use the PORT env var
    port = int(os.environ.get("PORT", 7860))
    uvicorn.run(app, host="0.0.0.0", port=port)
if __name__ == "__main__":
    main()
