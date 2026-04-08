from uuid import uuid4
from openenv.core.env_server.interfaces import Environment
from openenv.core.env_server.types import State
from ..models import EmailAction, EmailObservation

class EmailEnvironment(Environment):
    def __init__(self):
        self._state = State(episode_id=str(uuid4()), step_count=0)
        self.current_task_index = 0
        self.cumulative_score = 0.0
        self.completed_tasks = []
        
        self.tasks = [
            {
                "id": "task1",
                "name": "classify_urgency",
                "description": "Classify email urgency as urgent or normal",
                "email_subject": "URGENT: Server Down",
                "email_body": "The production server is not responding."
            },
            {
                "id": "task2",
                "name": "choose_action",
                "description": "Choose appropriate action",
                "email_subject": "Weekly Newsletter",
                "email_body": "Check out our latest products!"
            },
            {
                "id": "task3",
                "name": "draft_response",
                "description": "Draft appropriate response",
                "email_subject": "Order #12345",
                "email_body": "My order hasn't arrived. Please help."
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
            task_id=task["id"],
            task_description=task["description"],
            attempts_remaining=3,
            feedback="Task started",
            done=False,
            reward=0.0
        )

    def step(self, action: EmailAction) -> EmailObservation:
        self._state.step_count += 1
        task = self.tasks[self.current_task_index]
        
        # Calculate reward based on task
        reward = 0.5
        feedback = ""
        
        if task["name"] == "classify_urgency":
            if action.urgency == "urgent":
                reward = 0.95
                feedback = "Correctly identified urgent email"
            else:
                reward = 0.85
                feedback = "Identified as normal email"
                
        elif task["name"] == "choose_action":
            if action.action == "respond":
                reward = 0.90
                feedback = "Chose to respond"
            else:
                reward = 0.80
                feedback = "Chose to archive"
                
        elif task["name"] == "draft_response":
            if action.response_draft and len(action.response_draft) > 20:
                reward = 0.88
                feedback = "Good response draft"
            else:
                reward = 0.55
                feedback = "Response draft too short"
        
        self.cumulative_score += reward
        self.completed_tasks.append(task["id"])
        self.current_task_index += 1
        
        done = self.current_task_index >= len(self.tasks)
        
        # Update state
        self._state.current_task = task["id"]
        self._state.total_tasks_completed = len(self.completed_tasks)
        self._state.cumulative_score = self.cumulative_score / len(self.tasks) if self.completed_tasks else 0
        self._state.history.append({"task": task["id"], "reward": reward})
        
        next_task = self.tasks[self.current_task_index] if not done else None
        
        return EmailObservation(
            email_subject=next_task["email_subject"] if next_task else "",
            email_body=next_task["email_body"] if next_task else "",
            task_id=task["id"],
            task_description=task["description"],
            attempts_remaining=3 if not done else 0,
            feedback=feedback,
            done=done,
            reward=reward
        )

    @property
    def state(self):
        return self._state
