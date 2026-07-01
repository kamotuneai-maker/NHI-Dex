FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY agent.py .

LABEL nhi-dex.agent.name="code-review-agent"
LABEL nhi-dex.agent.type="coding"
LABEL nhi-dex.agent.owner="engineering-team"
LABEL nhi-dex.agent.scope="code-review-read-only"

CMD ["python", "agent.py"]
