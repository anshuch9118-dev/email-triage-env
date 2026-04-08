def classify_urgency_grader(output, expected=None):
    urgency = output.get("urgency", "")
    if urgency in ["urgent", "normal"]:
        return 0.9   # ✅ valid (between 0 and 1)
    return 0.1       # ❌ not zero


def choose_action_grader(output, expected=None):
    action = output.get("action", "")
    if action in ["respond", "archive"]:
        return 0.85
    return 0.2


def draft_response_grader(output, expected=None):
    response = output.get("response", "")
    if isinstance(response, str) and len(response) > 15:
        return 0.95
    return 0.3
