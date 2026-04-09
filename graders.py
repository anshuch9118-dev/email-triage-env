from openenv.core.env_server.interfaces import register_grader

@register_grader("triage_critical_outage")
def triage_critical_grader(output, expected=None):
    val = str(output).upper()
    # Using 0.99 instead of 1.0 and 0.01 instead of 0.0
    return 0.99 if "P0_URGENT" in val else 0.01

@register_grader("triage_customer_query")
def triage_support_grader(output, expected=None):
    val = str(output).upper()
    return 0.99 if "ROUTE_TO_SUPPORT" in val else 0.01

@register_grader("triage_spam_filter")
def triage_spam_grader(output, expected=None):
    val = str(output).upper()
    return 0.99 if "ARCHIVE" in val else 0.01
