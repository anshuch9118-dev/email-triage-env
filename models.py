from dataclasses import dataclass
from typing import Optional
from openenv.core.client_types import Action, Observation

@dataclass
class EmailAction(Action):
    urgency: str
    action: str
    response_draft: Optional[str] = None

@dataclass
class EmailObservation(Observation):
    email_subject: str = ""
    email_body: str = ""
    task_name: str = ""
    task_description: str = ""
    done: bool = False
    reward: float = 0.0
