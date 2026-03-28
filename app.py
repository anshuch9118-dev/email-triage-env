import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from server.app import app
except ImportError:
    from server.app import app  # Just in case
    pass

# Alternative: Create a simple FastAPI app directly if server import fails
if 'app' not in dir():
    from fastapi import FastAPI
    app = FastAPI()
    
    @app.get("/")
    def root():
        return {"message": "Email Triage Environment"}
    
    @app.get("/health")
    def health():
        return {"status": "healthy"}