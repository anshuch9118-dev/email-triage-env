def classify_urgency_grader(action, observation):
    return 0.95 if action.get("urgency") == "urgent" else 0.85

def choose_action_grader(action, observation):
    return 0.90 if action.get("action") == "respond" else 0.80

def draft_response_grader(action, observation):
    draft = action.get("response_draft", "")
    return 0.88 if len(draft) > 20 else 0.55
