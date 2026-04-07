from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import uvicorn

app = FastAPI()

class Action(BaseModel):
    urgency: str
    action: str
    response_draft: Optional[str] = None

# Store state
task_count = 0
cumulative_score = 0.0

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/reset")
def reset():
    global task_count, cumulative_score
    task_count = 0
    cumulative_score = 0.0
    return {
        "task_description": "Classify the urgency of this email and take appropriate action",
        "email_subject": "Urgent: System Down",
        "email_body": "The production server is not responding. Please investigate immediately."
    }

@app.post("/step")
def step(action: Action):
    global task_count, cumulative_score
    task_count += 1
    
    # Simple scoring logic
    reward = 0.0
    if action.urgency == "urgent":
        reward = 1.0
    elif action.urgency == "normal":
        reward = 0.5
    else:
        reward = 0.0
        
    cumulative_score += reward
    
    return {
        "reward": reward,
        "feedback": f"Action '{action.action}' processed with urgency '{action.urgency}'"
    }

@app.get("/state")
def state():
    return {
        "cumulative_score": round(cumulative_score, 2),
        "total_tasks_completed": task_count
    }

def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)

if __name__ == "__main__":
    main()
