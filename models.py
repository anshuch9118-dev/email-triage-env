from dataclasses import dataclass, field
from typing import Optional
from openenv.core.client_types import Action, Observation

@dataclass
class EmailAction(Action):
    """Action for Email Triage environment."""
    urgency: str  # "urgent" or "normal"
    action: str   # "respond" or "archive"
    response_draft: Optional[str] = None

@dataclass
class EmailObservation(Observation):
    """Observation returned after each step."""
    email_subject: str
    email_body: str
    task_name: str
    task_description: str
    done: bool = False
    reward: float = 0.0
