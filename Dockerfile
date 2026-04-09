FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY . .

# Expose the port the app runs on
EXPOSE 7860

# This command starts the server in the background (&) 
# waits a few seconds for it to boot, and then runs the inference script.
CMD uvicorn app:app --host 0.0.0.0 --port 7860 & sleep 5 && python inference.py
