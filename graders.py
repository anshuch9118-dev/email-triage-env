def classify_urgency_grader(output, expected=None):
    if isinstance(output, dict):
        urgency = output.get("urgency", "")
    elif hasattr(output, "urgency"):
        urgency = output.urgency
    else:
        urgency = str(output)
    return 1.0 if str(urgency).lower() in ["urgent", "normal"] else 0.0

def choose_action_grader(output, expected=None):
    if isinstance(output, dict):
        action = output.get("action", "")
    elif hasattr(output, "action"):
        action = output.action
    else:
        action = str(output)
    return 1.0 if str(action).lower() in ["respond", "archive", "escalate", "delete"] else 0.0

def draft_response_grader(output, expected=None):
    if isinstance(output, dict):
        draft = output.get("response_draft", "") or output.get("answer", "")
    elif hasattr(output, "response_draft"):
        draft = output.response_draft
    else:
        draft = str(output)
    return 1.0 if draft and len(str(draft)) > 10 else 0.0

GRADERS = {
    "classify_urgency": classify_urgency_grader,
    "choose_action": choose_action_grader,
    "draft_response": draft_response_grader,
}

TASK_GRADERS = [
    {"task_id": "classify_urgency", "grader": classify_urgency_grader},
    {"task_id": "choose_action", "grader": choose_action_grader},
    {"task_id": "draft_response", "grader": draft_response_grader},
]

def get_grader(task_id: str):
    return GRADERS.get(task_id)
