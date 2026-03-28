from pydantic import BaseModel
from typing import Optional, List

class EmailTriageAction(BaseModel):
    urgency: str
    action: str
    response_draft: Optional[str] = None

class EmailTriageObservation(BaseModel):
    done: bool
    reward: Optional[float]
    email_subject: str
    email_body: str
    task_id: int
    task_description: str
    attempts_remaining: int
    feedback: str

class EmailTriageState(BaseModel):
    episode_id: Optional[str]
    step_count: int
    current_task: int
    total_tasks_completed: int
    cumulative_score: float
    history: List[dict]