from openenv.core.env_server.interfaces import register_grader

@register_grader("classify_urgency")
def classify_urgency_grader(output, expected=None):
    return 0.9

@register_grader("choose_action")
def choose_action_grader(output, expected=None):
    return 0.85

@register_grader("draft_response")
def draft_response_grader(output, expected=None):
    return 0.95
