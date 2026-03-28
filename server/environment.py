import uuid
from typing import Optional
from openenv.core.env_server import Environment
from models import EmailTriageAction, EmailTriageObservation, EmailTriageState


# Sample email dataset
EMAILS = {
    1: {
        "subject": "Project deadline tomorrow",
        "body": "Hi team, please submit your reports by EOD tomorrow. Thanks!",
        "correct_urgency": "urgent"
    },
    2: {
        "subject": "Weekly newsletter subscription",
        "body": "You're receiving this because you signed up for our weekly updates.",
        "correct_urgency": "normal",
        "correct_action": "archive"
    },
    3: {
        "subject": "Customer complaint about delayed order",
        "body": "I ordered 2 weeks ago and still haven't received my package. Order #12345.",
        "correct_urgency": "urgent",
        "correct_action": "respond",
        "ideal_response_keywords": ["apologize", "investigate", "order", "tracking"]
    }
}


def grade_task1(action, email_data):
    if action.urgency == email_data["correct_urgency"]:
        return 1.0, f"Correct! '{action.urgency}' is right."
    return 0.0, f"Wrong. Expected '{email_data['correct_urgency']}'"


def grade_task2(action, email_data):
    urgency_score = 1.0 if action.urgency == email_data["correct_urgency"] else 0.0
    action_score = 1.0 if action.action == email_data["correct_action"] else 0.0
    total = (urgency_score * 0.3) + (action_score * 0.7)
    return total, f"Urgency: {urgency_score:.0%}, Action: {action_score:.0%}"


def grade_task3(action, email_data):
    urgency_score = 1.0 if action.urgency == email_data["correct_urgency"] else 0.0
    action_score = 1.0 if action.action == email_data["correct_action"] else 0.0
    
    response_score = 0.0
    if action.action == "respond" and action.response_draft:
        keywords = email_data["ideal_response_keywords"]
        matches = sum(1 for kw in keywords if kw.lower() in action.response_draft.lower())
        response_score = matches / len(keywords)
    
    total = (urgency_score * 0.2) + (action_score * 0.3) + (response_score * 0.5)
    return total, f"Urgency: {urgency_score:.0%}, Action: {action_score:.0%}, Response: {response_score:.0%}"


class EmailTriageEnvironment(Environment):
    SUPPORTS_CONCURRENT_SESSIONS = True
    MAX_ATTEMPTS = 3
    
    def __init__(self):
        self._state = EmailTriageState(
            current_task=1,
            total_tasks_completed=0,
            cumulative_score=0.0,
            history=[]
        )
        self.current_task = 1
        self.attempts = 0
        self.email_data = EMAILS[1]
        self.history = []
    
    def reset(self, seed=None, episode_id=None, **kwargs):
        self.current_task = 1
        self.attempts = 0
        self.history = []
        self.email_data = EMAILS[1]
        
        self._state = EmailTriageState(
            episode_id=episode_id or str(uuid.uuid4()),
            step_count=0,
            current_task=1,
            total_tasks_completed=0,
            cumulative_score=0.0,
            history=[]
        )
        
        return EmailTriageObservation(
            done=False,
            reward=None,
            email_subject=self.email_data["subject"],
            email_body=self.email_data["body"],
            task_id=1,
            task_description="Task 1: Classify urgency (urgent/normal/spam)",
            attempts_remaining=self.MAX_ATTEMPTS,
            feedback="Classify the urgency of this email."
        )
    
    def step(self, action: EmailTriageAction, timeout_s=None, **kwargs):
        self._state.step_count += 1
        self.attempts += 1
        
        if self.current_task == 1:
            score, feedback = grade_task1(action, self.email_data)
        elif self.current_task == 2:
            score, feedback = grade_task2(action, self.email_data)
        else:
            score, feedback = grade_task3(action, self.email_data)
        
        self.history.append({
            "step": self._state.step_count,
            "task": self.current_task,
            "score": score,
            "feedback": feedback
        })
        self._state.history = self.history
        self._state.cumulative_score += score
        
        task_completed = score >= 0.8
        
        if task_completed and self.current_task < 3:
            self.current_task += 1
            self.attempts = 0
            self.email_data = EMAILS[self.current_task]
            self._state.current_task = self.current_task
            self._state.total_tasks_completed += 1
            
            return EmailTriageObservation(
                done=False,
                reward=score,
                email_subject=self.email_data["subject"],
                email_body=self.email_data["body"],
                task_id=self.current_task,
                task_description=f"Task {self.current_task}: {'Choose action' if self.current_task == 2 else 'Full triage with response'}",
                attempts_remaining=self.MAX_ATTEMPTS,
                feedback=f"Task {self.current_task-1} complete! Now task {self.current_task}."
            )
        
        elif task_completed and self.current_task == 3:
            self._state.total_tasks_completed += 1
            return EmailTriageObservation(
                done=True,
                reward=score,
                email_subject="",
                email_body="",
                task_id=3,
                task_description="All tasks completed!",
                attempts_remaining=0,
                feedback=f"Congratulations! Final score: {self._state.cumulative_score:.2f}"
            )
        
        elif self.attempts >= self.MAX_ATTEMPTS and self.current_task < 3:
            self.current_task += 1
            self.attempts = 0
            self.email_data = EMAILS[self.current_task]
            self._state.current_task = self.current_task
            
            return EmailTriageObservation(
                done=False,
                reward=score,
                email_subject=self.email_data["subject"],
                email_body=self.email_data["body"],
                task_id=self.current_task,
                task_description=f"Task {self.current_task}: {'Choose action' if self.current_task == 2 else 'Full triage'}",
                attempts_remaining=self.MAX_ATTEMPTS,
                feedback=f"Moving to task {self.current_task}. Previous task score: {score:.2f}"
            )
        
        elif self.attempts >= self.MAX_ATTEMPTS and self.current_task == 3:
            return EmailTriageObservation(
                done=True,
                reward=score,
                email_subject="",
                email_body="",
                task_id=3,
                task_description="Failed final task",
                attempts_remaining=0,
                feedback=f"Episode ended. Final score: {self._state.cumulative_score:.2f}"
            )
        
        else:
            return EmailTriageObservation(
                done=False,
                reward=score,
                email_subject=self.email_data["subject"],
                email_body=self.email_data["body"],
                task_id=self.current_task,
                task_description=f"Task {self.current_task}: Try again",
                attempts_remaining=self.MAX_ATTEMPTS - self.attempts,
                feedback=feedback
            )
    
    @property
    def state(self):
        return self._state