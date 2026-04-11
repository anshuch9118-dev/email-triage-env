def classify_urgency_grader(action, observation):
    if action.get("urgency") == "urgent":
        return 0.95
    else:
        return 0.85

def choose_action_grader(action, observation):
    if action.get("action") == "respond":
        return 0.90
    else:
        return 0.80

def draft_response_grader(action, observation):
    draft = action.get("response_draft", "")
    if draft and len(draft) > 20:
        return 0.88
    else:
        return 0.55
