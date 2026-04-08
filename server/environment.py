from uuid import uuid4
from openenv.core.env_server.interfaces import Environment
from openenv.core.env_server.types import State, StepResult
from .models import EmailAction, EmailObservation 

class EmailEnvironment(Environment):
    def __init__(self):
        # Explicitly define the 3 tasks for the validator
        self.task_definitions = {
            "classify_urgency": {"subject": "URGENT: Server Down", "body": "The production server is not responding."},
            "choose_action": {"subject": "Weekly Newsletter", "body": "Check out our latest products!"},
            "draft_response": {"subject": "Order #12345", "body": "My order hasn't arrived. Please help."}
        }
        
        self._state = State(
            episode_id=str(uuid4()), 
            step_count=0,
            current_task="classify_urgency"
        )

    def get_task_ids(self):
        # Some Phase 2 validators call this directly
        return list(self.task_definitions.keys())

    def reset(self, task_id: str = "classify_urgency") -> EmailObservation:
        # If validator requests a specific task, use it
        if task_id not in self.task_definitions:
            task_id = "classify_urgency"
            
        self._state = State(episode_id=str(uuid4()), step_count=0, current_task=task_id)
        task = self.task_definitions[task_id]
        
        return EmailObservation(
            email_subject=task["subject"],
            email_body=task["body"],
            task_id=task_id,
            done=False,
            reward=0.0
        )

    def step(self, action: EmailAction) -> EmailObservation:
        task_id = self._state.current_task
        self._state.step_count += 1
        
        # Grading Logic
        reward = 0.0
        if task_id == "classify_urgency":
            reward = 1.0 if action.urgency in ["urgent", "normal"] else 0.0
        elif task_id == "choose_action":
            reward = 1.0 if action.action in ["respond", "archive"] else 0.0
        elif task_id == "draft_response":
            reward = 1.0 if action.response_draft and len(action.response_draft) > 10 else 0.0

        # In Phase 2, usually 1 step = 1 task done
        done = True 
        
        return EmailObservation(
            email_subject="",
            email_body="",
            task_id=task_id,
            done=done,
            reward=reward
        )

    @property
    def state(self):
        return self._state
