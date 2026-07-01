FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY agent.py .

LABEL nhi-dex.agent.name="customer-support-agent"
LABEL nhi-dex.agent.type="client-facing"
LABEL nhi-dex.agent.owner="support-team"
LABEL nhi-dex.agent.scope="customer-query-response"

CMD ["python", "agent.py"]
