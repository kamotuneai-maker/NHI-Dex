import logging
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .tools.file_read import file_read
from .tools.db_query import db_query
from .tools.code_review import code_review
from .tools.shell_exec import shell_exec
from .tools.customer_query import customer_query
from .tools.cloud_status import cloud_status
from .tools.api_call import api_call
from .tools.email_send import email_send

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger("mcp-tools.server")

app = FastAPI(title="NHI-Dex MCP Tool Server", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class FileReadRequest(BaseModel):
    path: str = "/data/analytics.csv"


class DbQueryRequest(BaseModel):
    query: str = "SELECT * FROM users LIMIT 10"


class CodeReviewRequest(BaseModel):
    file_path: str = "/src/payment.py"


class ShellExecRequest(BaseModel):
    command: str = "ls -la"


class CustomerQueryRequest(BaseModel):
    inject_attack: bool = False


class CloudStatusRequest(BaseModel):
    region: str = "us-east-1"


class ApiCallRequest(BaseModel):
    url: str = "https://api.external.com/data"
    method: str = "GET"
    payload: dict = {}


class EmailSendRequest(BaseModel):
    to: str = "ops@example.com"
    subject: str = "Alert"
    body: str = ""


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "mcp-tools", "tools": 8}


@app.post("/tools/file_read")
async def tool_file_read(req: FileReadRequest):
    return file_read(req.path)


@app.post("/tools/db_query")
async def tool_db_query(req: DbQueryRequest):
    return db_query(req.query)


@app.post("/tools/code_review")
async def tool_code_review(req: CodeReviewRequest):
    return code_review(req.file_path)


@app.post("/tools/shell_exec")
async def tool_shell_exec(req: ShellExecRequest):
    return shell_exec(req.command)


@app.post("/tools/customer_query")
async def tool_customer_query(req: CustomerQueryRequest):
    return customer_query(req.inject_attack)


@app.post("/tools/cloud_status")
async def tool_cloud_status(req: CloudStatusRequest):
    return cloud_status(req.region)


@app.post("/tools/api_call")
async def tool_api_call(req: ApiCallRequest):
    return api_call(req.url, req.method, req.payload)


@app.post("/tools/email_send")
async def tool_email_send(req: EmailSendRequest):
    return email_send(req.to, req.subject, req.body)
