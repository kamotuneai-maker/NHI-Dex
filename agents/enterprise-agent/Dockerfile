FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY agent.py .

LABEL nhi-dex.agent.name="data-analyst-agent"
LABEL nhi-dex.agent.type="enterprise"
LABEL nhi-dex.agent.owner="platform-team"
LABEL nhi-dex.agent.scope="read-only-analytics"
LABEL nhi-dex.agent.autonomy="supervised"

CMD ["python", "agent.py"]
