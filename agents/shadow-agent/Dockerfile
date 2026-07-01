FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY agent.py .

# NO LABELS — this is the point. Shadow AI has no governance.

CMD ["python", "agent.py"]
