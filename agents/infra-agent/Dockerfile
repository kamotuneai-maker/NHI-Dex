FROM python:3.11-slim

WORKDIR /app

RUN mkdir -p /app/.kube && echo '{"apiVersion":"v1","kind":"Config"}' > /app/.kube/config

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY agent.py .

LABEL nhi-dex.agent.name="cloud-ops-agent"
LABEL nhi-dex.agent.type="infrastructure"
LABEL nhi-dex.agent.owner="platform-ops"
LABEL nhi-dex.agent.scope="cloud-status-readonly"

CMD ["python", "agent.py"]
