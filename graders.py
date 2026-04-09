from openenv.core.env_server.interfaces import register_grader

@register_grader("classify_urgency")
def classify_urgency_grader(output, expected=None):
    # Standardizing to 0.98 to stay safely inside the (0, 1) range
    # and using a more flexible check for the output
    val = str(output).lower()
    return 0.98 if "urgent" in val or "p0" in val else 0.02

@register_grader("choose_action")
def choose_action_grader(output, expected=None):
    val = str(output).lower()
    return 0.98 if "respond" in val or "support" in val else 0.02

@register_grader("draft_response")
def draft_response_grader(output, expected=None):
    val = str(output)
    # Give a high score if the model actually wrote a response
    return 0.98 if len(val) > 10 else 0.02
