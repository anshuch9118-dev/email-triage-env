from openenv.core.env_client import EnvClient
from models import EmailAction, EmailObservation


class EmailTriageEnv(EnvClient):
    action_type = EmailAction
    observation_type = EmailObservation
