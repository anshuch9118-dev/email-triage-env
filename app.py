import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from server.environment import EmailTriageEnvironment
from models import EmailTriageAction, EmailTriageObservation

app = FastAPI(title="Email Triage Environment")

# Create a single environment instance
env = EmailTriageEnvironment()

@app.get("/")
def root():
    return {"message": "Email Triage Environment", "status": "running"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/reset")
def reset():
    obs = env.reset()
    return {
        "done": obs.done,
        "reward": obs.reward,
        "email_subject": obs.email_subject,
        "email_body": obs.email_body,
        "task_id": obs.task_id,
        "task_description": obs.task_description,
        "attempts_remaining": obs.attempts_remaining,
        "feedback": obs.feedback
    }

@app.post("/step")
def step(request: dict):
    action = EmailTriageAction(
        urgency=request.get("urgency", "normal"),
        action=request.get("action", "archive"),
        response_draft=request.get("response_draft")
    )
    obs = env.step(action)
    return {
        "done": obs.done,
        "reward": obs.reward,
        "email_subject": obs.email_subject,
        "email_body": obs.email_body,
        "task_id": obs.task_id,
        "task_description": obs.task_description,
        "attempts_remaining": obs.attempts_remaining,
        "feedback": obs.feedback
    }

@app.get("/state")
def get_state():
    state = env.state
    return {
        "episode_id": state.episode_id,
        "step_count": state.step_count,
        "current_task": state.current_task,
        "total_tasks_completed": state.total_tasks_completed,
        "cumulative_score": state.cumulative_score,
        "history": state.history
    }