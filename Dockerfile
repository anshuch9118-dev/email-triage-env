FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY graders.py .
COPY models.py .
COPY openenv.yaml .
COPY inference.py .
COPY client.py .
COPY pyproject.toml .
COPY uv.lock .

RUN mkdir -p server
COPY server/ ./server/

EXPOSE 7860

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
