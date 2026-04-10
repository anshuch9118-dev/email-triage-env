import sys
import os
sys.path.insert(0, "/app")
from app import app
import uvicorn

def main():
    port = int(os.environ.get("PORT", 7860))
    uvicorn.run(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()
