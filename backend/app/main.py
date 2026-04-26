import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from dotenv import load_dotenv
from fastapi import BackgroundTasks, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.modules.parser import DocumentParser
from app.modules.retriever import DocumentRetriever
from app.schemas import JobResponse, JobStatusResponse
from app.workflow import build_workflow

load_dotenv()

MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "15"))
MAX_UPLOAD_BYTES = MAX_UPLOAD_MB * 1024 * 1024
ALLOWED_EXTENSIONS = DocumentParser.SUPPORTED_EXTENSIONS

STEP_PROGRESS = {
    "queued": 0,
    "parsing": 10,
    "classify": 35,
    "extract": 52,
    "analyze_risk": 68,
    "summarize": 82,
    "retrieve": 90,
    "compile": 96,
    "done": 100,
}

STEP_MESSAGE = {
    "queued": "Queued for processing",
    "parsing": "Parsing and normalizing document text",
    "classify": "Classifying document type",
    "extract": "Extracting entities and delivery details",
    "analyze_risk": "Scoring delivery and scope risks",
    "summarize": "Generating business and technical summaries",
    "retrieve": "Matching against similar project patterns",
    "compile": "Compiling final intelligence package",
    "done": "Analysis complete",
}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_origins() -> list[str]:
    configured = os.getenv("FRONTEND_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
    origins = [value.strip() for value in configured.split(",") if value.strip()]
    return origins or ["*"]


def sanitize_error_message(error: Exception) -> str:
    text = str(error).strip()
    if not text:
        return "Unexpected error while processing document."
    return text[:500]


def supported_extensions_csv() -> str:
    return ", ".join(sorted(ALLOWED_EXTENSIONS))


origins = parse_origins()
allow_credentials = os.getenv("CORS_ALLOW_CREDENTIALS", "false").strip().lower() == "true"
if "*" in origins and allow_credentials:
    allow_credentials = False

app = FastAPI(
    title="RFP / SOW Intelligence Portal API",
    description="ML Backend API for Document Analysis",
    version="1.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

workflow_app = build_workflow()
vector_store_retriever = DocumentRetriever()
jobs: Dict[str, Dict[str, Any]] = {}


def update_job(job_id: str, **updates: Any) -> None:
    job = jobs.get(job_id)
    if not job:
        return

    # Keep progress monotonic even when nodes complete out of order.
    if "progress" in updates:
        updates["progress"] = max(int(job.get("progress", 0)), int(updates["progress"]))

    job.update(updates)
    job["updated_at"] = utc_now_iso()


def update_job_step(job_id: str, step: str) -> None:
    update_job(
        job_id,
        status="processing",
        current_step=step,
        progress=STEP_PROGRESS.get(step, 0),
        message=STEP_MESSAGE.get(step, "Processing"),
    )


@app.get("/")
def read_root():
    return {"message": "Welcome to the RFP/SOW Intelligence Portal API"}


@app.get("/healthz")
def health_check():
    return {"status": "ok"}


@app.get("/api/v1/vector-store/status")
def vector_store_status():
    return {
        "enabled": True,
        "provider": "chroma",
        "collection_name": vector_store_retriever.collection_name,
        "persist_path": vector_store_retriever.persist_path,
        "project_count": vector_store_retriever.collection.count(),
        "embedding_model": "hashing_embedding_v1",
    }


async def process_document_task(job_id: str, file_bytes: bytes, filename: str):
    try:
        update_job_step(job_id, "parsing")
        text = DocumentParser.parse_document(file_bytes, filename)
        if not text.strip():
            raise ValueError("Document contains no readable text.")

        initial_state = {
            "file_name": filename,
            "text": text,
            "classification": None,
            "extracted": None,
            "risks": None,
            "summary": None,
            "similar_projects": [],
            "final_result": None,
        }

        final_result = None
        async for update in workflow_app.astream(initial_state, stream_mode="updates"):
            for node_name, payload in update.items():
                if node_name in STEP_PROGRESS:
                    update_job_step(job_id, node_name)
                if isinstance(payload, dict) and payload.get("final_result") is not None:
                    final_result = payload["final_result"]

        if final_result is None:
            raise RuntimeError("Workflow completed without generating final output.")

        update_job(
            job_id,
            status="completed",
            current_step="done",
            progress=STEP_PROGRESS["done"],
            message=STEP_MESSAGE["done"],
            result=final_result,
            error=None,
        )
    except Exception as exc:
        update_job(
            job_id,
            status="failed",
            message="Analysis failed",
            error=sanitize_error_message(exc),
        )


@app.post("/api/v1/analyze", response_model=JobResponse)
async def analyze_document(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    filename = (file.filename or "").strip()
    extension = Path(filename).suffix.lower().replace(".", "")
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format. Allowed formats: {supported_extensions_csv()}",
        )

    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")
    if len(file_bytes) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail=f"File exceeds {MAX_UPLOAD_MB} MB limit.")

    job_id = str(uuid.uuid4())
    now = utc_now_iso()
    jobs[job_id] = {
        "status": "processing",
        "current_step": "queued",
        "progress": STEP_PROGRESS["queued"],
        "message": STEP_MESSAGE["queued"],
        "result": None,
        "error": None,
        "created_at": now,
        "updated_at": now,
    }

    background_tasks.add_task(process_document_task, job_id, file_bytes, filename)
    return JobResponse(job_id=job_id, message="Document processing started")


@app.get("/api/v1/status/{job_id}", response_model=JobStatusResponse)
def get_job_status(job_id: str):
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return JobStatusResponse(
        job_id=job_id,
        status=job["status"],
        current_step=job.get("current_step"),
        progress=job.get("progress", 0),
        message=job.get("message"),
        result=job.get("result"),
        error=job.get("error"),
        created_at=job.get("created_at"),
        updated_at=job.get("updated_at"),
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
