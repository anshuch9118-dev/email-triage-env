# server/app.py
from openenv.core.env_server import create_app
from ..models import EmailAction, EmailObservation
from .email_environment import EmailEnvironment

# Pass the class (factory) - each WebSocket session gets its own instance
app = create_app(EmailEnvironment, EmailAction, EmailObservation, env_name="email_triage_env")
