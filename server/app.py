from openenv.core.env_server import create_app
from models import EmailAction, EmailObservation
from server.environment import EmailEnvironment

app = create_app(EmailEnvironment, EmailAction, EmailObservation, env_name="email_triage_env")
