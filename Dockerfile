FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY inference.py .
COPY graders.py .
COPY models.py .
COPY openenv.yaml .

RUN mkdir -p server
COPY server/ ./server/

EXPOSE 7860

CMD ["python", "-m", "server.app"]
