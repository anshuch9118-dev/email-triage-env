FROM python:3.10-slim

WORKDIR /app

# Copy requirements first for layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy ALL necessary files
COPY app.py .
COPY inference.py .
COPY graders.py .
COPY openenv.yaml .
COPY models.py .
COPY baseline_inference.py .

# Copy the server package
COPY server/ ./server/

# Expose port
EXPOSE 7860

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
