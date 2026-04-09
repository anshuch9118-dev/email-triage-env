FROM python:3.10-slim

WORKDIR /app

# Disable python buffering so logs show up instantly
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose HF default port
EXPOSE 7860

# We start uvicorn in the background, run inference, 
# and then use 'wait' to keep the container alive.
CMD uvicorn app:app --host 0.0.0.0 --port 7860 & sleep 5 && python inference.py && wait
