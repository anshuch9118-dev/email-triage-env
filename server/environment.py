from uuid import uuid4
from openenv.core.env_server.interfaces import Environment
from openenv.core.env_server.types import State
from models import EmailAction, EmailObservation

class EmailEnvironment(Environment):
    def __init__(self):
        self._state = State(episode_id=str(uuid4()), step_count=0)
        self.current_task_index = 0
        self.cumulative_score = 0.0
        self.completed_tasks = []
        
        self.tasks = [
            {
                "name": "classify_urgency",
                "description": "Classify email urgency as urgent or normal",
                "email_subject": "URGENT: Server Down",
                "email_body": "The production server is not responding."
            },
            {
                "name": "choose_action",
                "description": "Choose appropriate action",
                "email_subject": "Weekly Newsletter",
                "email_body": "Check out our latest products!"
            },
            {
                "name": "draft_response",
                "description": "Draft appropriate response",
                "email_subject": "Order #12345",
                "email_body": "My order hasn't arrived."
            }
        ]

    def reset(self) -> EmailObservation:
        self._state = State(episode_id=str(uuid4()), step_count=0)
        self.current_task_index = 0
        self.cumulative_score = 0.0
        self.completed_tasks = []
        task = self.tasks[0]
        return EmailObservation(
            email_subject=task["email_subject"],
            email_body=task["email_body"],
            task_name=task["name"],
            task_description=task["description"],
            done=False,
            reward=0.0
        )

    def step(self, action: EmailAction) -> EmailObservation:
        self._state.step_count += 1
        task = self.tasks[self.current_task_index]
        
        if task["name"] == "classify_urgency":
            reward = 0.95 if action.urgency == "urgent" else 0.85
        elif task["name"] == "choose_action":
            reward = 0.90 if action.action == "respond" else 0.80
        elif task["name"] == "draft_response":
            reward = 0.88 if action.response_draft and len(action.response_draft) > 20 else 0.55
        else:
            reward = 0.50
        
        self.cumulative_score += reward
        self.completed_tasks.append(task["name"])
        self.current_task_index += 1
        done = self.current_task_index >= len(self.tasks)
        
        self._state.current_task = task["name"]
        self._state.total_tasks_completed = len(self.completed_tasks)
        self._state.cumulative_score = self.cumulative_score / len(self.tasks)
        self._state.history.append({"task": task["name"], "reward": reward})
        
        next_task = self.tasks[self.current_task_index] if not done else None
        
        return EmailObservation(
            email_subject=next_task["email_subject"] if next_task else "",
            email_body=next_task["email_body"] if next_task else "",
            task_name=task["name"],
            task_description=task["description"],
            done=done,
            reward=reward
        )

    @property
    def state(self) -> State:
        return self._state
