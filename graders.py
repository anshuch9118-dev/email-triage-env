from openenv.core.env_server.interfaces import register_grader

@register_grader("triage_critical_outage")
def triage_critical_grader(output, expected=None):
    # Check if the agent correctly identified the P0 status
    val = str(output).upper()
    return 1.0 if "P0_URGENT" in val else 0.1

@register_grader("triage_customer_query")
def triage_support_grader(output, expected=None):
    # Check if the agent routed to the correct department
    val = str(output).upper()
    return 1.0 if "ROUTE_TO_SUPPORT" in val else 0.1

@register_grader("triage_spam_filter")
def triage_spam_grader(output, expected=None):
    # Check if the agent successfully archived junk
    val = str(output).upper()
    return 1.0 if "ARCHIVE" in val else 0.1
