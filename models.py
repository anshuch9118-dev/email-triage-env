# models.py
from typing import List, Optional
from openenv.core.env_server import Action, Observation, State


class EmailTriageAction(Action):
    urgency: str
    action: str
    response_draft: Optional[str] = None


class EmailTriageObservation(Observation):
    email_subject: str
    email_body: str
    task_id: int
    task_description: str
    attempts_remaining: int
    feedback: str


class EmailTriageState(State):
    current_task: int
    total_tasks_completed: int
    cumulative_score: float
    history: List[dict] = []