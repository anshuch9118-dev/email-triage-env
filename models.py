from pydantic import BaseModel
from typing import Optional


class EmailAction(BaseModel):
    urgency: Optional[str] = ""
    action: Optional[str] = ""
    response_draft: Optional[str] = None


class EmailObservation(BaseModel):
    email_subject: str = ""
    email_body: str = ""
    task_id: str = ""
    done: bool = False
    reward: float = 0.0
