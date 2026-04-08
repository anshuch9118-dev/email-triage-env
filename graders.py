from openenv.core.env_server.interfaces import register_grader

@register_grader("classify_urgency")
def classify_urgency_grader(output, expected=None):
    urgency = output.get("urgency", "")
    if urgency in ["urgent", "normal"]:
        return 0.9
    return 0.1

@register_grader("choose_action")
def choose_action_grader(output, expected=None):
    action = output.get("action", "")
    if action in ["respond", "archive"]:
        return 0.85
    return 0.2

@register_grader("draft_response")
def draft_response_grader(output, expected=None):
    response = output.get("response", "")
    if isinstance(response, str) and len(response) > 15:
        return 0.95
    return 0.3
