from openenv.core.env_server.interfaces import register_grader

@register_grader("classify_urgency")
def classify_urgency_grader(output, expected=None):
    urgency = output.get("urgency", "") if isinstance(output, dict) else output
    return 1.0 if urgency in ["urgent", "normal"] else 0.0

@register_grader("choose_action")
def choose_action_grader(output, expected=None):
    action = output.get("action", "") if isinstance(output, dict) else output
    return 1.0 if action in ["respond", "archive"] else 0.0

@register_grader("draft_response")
def draft_response_grader(output, expected=None):
    response = output.get("response", "") if isinstance(output, dict) else output
    return 1.0 if (isinstance(response, str) and len(response) > 10) else 0.0
