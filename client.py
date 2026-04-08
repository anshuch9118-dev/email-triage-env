from openenv.core.env_client import EnvClient
from openenv.core.client_types import StepResult
from .models import EmailAction, EmailObservation

class EmailEnv(EnvClient[EmailAction, EmailObservation]):
    """Client for Email Triage environment."""
    
    def _step_payload(self, action: EmailAction) -> dict:
        return {
            "urgency": action.urgency,
            "action": action.action,
            "response_draft": action.response_draft
        }
    
    def _parse_result(self, payload: dict) -> StepResult[EmailObservation]:
        obs_data = payload.get("observation", {})
        obs = EmailObservation(
            email_subject=obs_data.get("email_subject", ""),
            email_body=obs_data.get("email_body", ""),
            task_name=obs_data.get("task_name", ""),
            task_description=obs_data.get("task_description", ""),
            done=payload.get("done", False),
            reward=payload.get("reward", 0.0)
        )
        return StepResult(
            observation=obs,
            reward=payload.get("reward", 0.0),
            done=payload.get("done", False)
        )
