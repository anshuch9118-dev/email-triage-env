from openenv.core.env_server import create_app
from models import EmailAction, EmailObservation
from server.environment import EmailEnvironment

app = create_app(EmailEnvironment, EmailAction, EmailObservation, env_name="email_triage_env")

def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)

if __name__ == "__main__":
    main()
