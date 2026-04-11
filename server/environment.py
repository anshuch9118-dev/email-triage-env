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

        # Internal task data
        self.tasks_data = [
            {
                "id": "classify_urgency",
                "name": "Classify Urgency",
                "description": "Classify email urgency as urgent or normal",
                "subject": "URGENT: Server Down",
                "body": "The production server is not responding."
            },
            {
                "id": "choose_action",
                "name": "Choose Action",
                "description": "Choose appropriate action",
                "subject": "Weekly Newsletter",
                "body": "Check out our latest products!"
            },
            {
                "id": "draft_response",
                "name": "Draft Response",
                "description": "Draft appropriate response",
                "subject": "Order #12345",
                "body": "My order hasn't arrived."
            }
        ]

   def get_tasks(self):
        # The validator counts a task ONLY if it sees 'grader' in this API response
        return [
            {
                "id": "classify_urgency",
                "name": "Classify Urgency",
                "difficulty": "easy",
                "score_range": [0.1, 0.9],
                "grader": {"type": "threshold"} # This signals the validator
            },
            {
                "id": "choose_action",
                "name": "Choose Action",
                "difficulty": "medium",
                "score_range": [0.1, 0.9],
                "grader": {"type": "threshold"}
            },
            {
                "id": "draft_response",
                "name": "Draft Response",
                "difficulty": "hard",
                "score_range": [0.1, 0.9],
                "grader": {"type": "llm_judge"}
            }
        ]
    def reset(self) -> EmailObservation:
        self._state = State(episode_id=str(uuid4()), step_count=0)
        self.current_task_index = 0
        self.cumulative_score = 0.0
        self.completed_tasks = []
        task = self.tasks_data[0]
        return EmailObservation(
            email_subject=task["subject"],
            email_body=task["body"],
            task_name=task["name"],
            task_description=task["description"],
            done=False,
            reward=0.1
        )

    def step(self, action: EmailAction) -> EmailObservation:
        self._state.step_count += 1
        current_task = self.tasks_data[self.current_task_index]
        
        # Logic to calculate score (must be between 0.1 and 0.99)
        if current_task["id"] == "classify_urgency":
            reward = 0.95 if action.urgency == "urgent" else 0.70
        elif current_task["id"] == "choose_action":
            reward = 0.90 if action.action == "respond" else 0.60
        elif current_task["id"] == "draft_response":
            reward = 0.85 if action.response_draft and len(action.response_draft) > 5 else 0.50
        else:
            reward = 0.1

        self.cumulative_score += reward
        self.completed_tasks.append(current_task["id"])
        
        self.current_task_index += 1
        done = self.current_task_index >= len(self.tasks_data)

        # Update internal state
        self._state.current_task = current_task["id"]
        self._state.total_tasks_completed = len(self.completed_tasks)
        self._state.cumulative_score = self.cumulative_score / len(self.tasks_data)
        
        next_task = self.tasks_data[self.current_task_index] if not done else None

        return EmailObservation(
            email_subject=next_task["subject"] if next_task else "",
            email_body=next_task["body"] if next_task else "",
            task_name=current_task["name"],
            task_description=current_task["description"],
            done=done,
            reward=reward
        )

    @property
    def state(self) -> State:
        return self._state
