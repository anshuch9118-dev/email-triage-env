from fastapi import FastAPI
from .environment import EmailTriageEnvironment
from models import EmailTriageAction, EmailTriageObservation

app = FastAPI(title="Email Triage Environment")
env = EmailTriageEnvironment()

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
def step(action: dict):
    a = EmailTriageAction(
        urgency=action.get("urgency", "normal"),
        action=action.get("action", "archive"),
        response_draft=action.get("response_draft")
    )
    obs = env.step(a)
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
    s = env.state
    return {
        "episode_id": s.episode_id,
        "step_count": s.step_count,
        "current_task": s.current_task,
        "total_tasks_completed": s.total_tasks_completed,
        "cumulative_score": s.cumulative_score,
        "history": s.history
    }

def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()