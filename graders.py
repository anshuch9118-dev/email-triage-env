def classify_urgency_grader(output, expected=None):
    return 1.0 if output.get("urgency") in ["urgent", "normal"] else 0.0

def choose_action_grader(output, expected=None):
    return 1.0 if output.get("action") in ["respond", "archive"] else 0.0

def draft_response_grader(output, expected=None):
    response = output.get("response", "")
    return 1.0 if isinstance(response, str) and len(response) > 10 else 0.0
