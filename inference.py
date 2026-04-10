import os
import json
import time
import sys
from typing import List, Optional
from openai import OpenAI
import requests

API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
API_KEY = os.getenv("HF_TOKEN") or os.getenv("API_KEY")
SPACE_URL = os.getenv("SPACE_URL", "https://codeBug01-email-triage-env.hf.space")

TASK_NAME = "email-triage"
BENCHMARK = "email-triage-env-v1"

TASKS = ["classify_urgency", "choose_action", "draft_response"]

def log_start(task: str, env: str, model: str):
    print(f"[START] task={task} env={env} model={model}", flush=True)

def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]):
    error_val = error if error else "null"
    done_val = str(done).lower()
    print(f"[STEP] step={step} action={action} reward={reward:.2f} done={done_val} error={error_val}", flush=True)

def log_end(success: bool, steps: int, score: float, rewards: List[float]):
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] success={str(success).lower()} steps={steps} score={score:.2f} rewards={rewards_str}", flush=True)

def get_llm_decision(client, task_id, email_subject, email_body):
    try:
        prompt = f"""You are an email triage assistant.
Task: {task_id}
Subject: {email_subject}
Body: {email_body}

Respond with JSON only:
{{"urgency": "urgent or normal", "action": "respond or archive", "response_draft": "a reply if needed"}}"""

        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are an email triage assistant. Respond with JSON only, no markdown."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=150,
        )
        content = completion.choices[0].message.content.strip()
        content = content.replace("```json", "").replace("```", "").strip()
        return json.loads(content)
    except Exception as e:
        print(f"LLM error: {e}", flush=True)
        return {
            "urgency": "urgent",
            "action": "respond",
            "response_draft": "Thank you for your email. I will look into this immediately and respond shortly."
        }

def run():
    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)

    log_start(task=TASK_NAME, env=BENCHMARK, model=MODEL_NAME)

    rewards = []
    steps_taken = 0
    success = False
    score = 0.0

    try:
        for step, task_id in enumerate(TASKS, 1):
            # Reset with specific task
            resp = requests.post(f"{SPACE_URL}/reset", json={"task_id": task_id}, timeout=15)
            task_data = resp.json()

            # Get LLM decision
            decision = get_llm_decision(
                client,
                task_id,
                task_data.get("email_subject", ""),
                task_data.get("email_body", "")
            )

            action = {
                "urgency": decision.get("urgency", "normal"),
                "action": decision.get("action", "respond"),
                "response_draft": decision.get("response_draft", "Thank you for contacting us.")
            }

            # Step the environment
            resp = requests.post(f"{SPACE_URL}/step", json=action, timeout=15)
            result = resp.json()
            reward = float(result.get("reward", 0.0))
            done = result.get("done", True)

            rewards.append(reward)
            steps_taken = step

            log_step(step=step, action=task_id, reward=reward, done=done, error=None)
            time.sleep(0.5)

        score = sum(rewards) / len(rewards) if rewards else 0.0
        success = score >= 0.5

    except Exception as e:
        log_step(step=steps_taken + 1, action="error", reward=0.0, done=True, error=str(e))

    finally:
        log_end(success=success, steps=steps_taken, score=score, rewards=rewards)

if __name__ == "__main__":
    run()
