import os
import uuid
import time
from typing import Dict, Optional
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from pipeline.runner import execute_pipeline

app = FastAPI(
    title="Sheet2Sound API",
    description="PDF Sheet Music → OMR → Audio Converter API",
    version="0.2.0"
)

# CORS configuration for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MOCK_DIR = os.path.join(BASE_DIR, "mock_assets")
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
os.makedirs(MOCK_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Mount outputs for generated job assets, fallback to mock_assets if needed
app.mount("/static", StaticFiles(directory=OUTPUT_DIR), name="static")

jobs_db: Dict[str, dict] = {}


class ConvertRequest(BaseModel):
    simulate_error: Optional[str] = None


@app.get("/")
def read_root():
    return {"message": "Sheet2Sound API is running", "docs": "/docs"}


@app.post("/upload")
@app.post("/api/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """Receives uploaded PDF file and returns job metadata."""
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    
    job_id = str(uuid.uuid4())
    saved_path = os.path.join(UPLOAD_DIR, f"{job_id}_{file.filename}")
    
    content = await file.read()
    with open(saved_path, "wb") as f:
        f.write(content)

    jobs_db[job_id] = {
        "job_id": job_id,
        "filename": file.filename,
        "pdf_path": saved_path,
        "file_size": len(content),
        "created_at": time.time(),
        "start_time": None,
        "status": "queued",
        "stage": "File uploaded, ready for conversion",
        "progress": 0,
        "error": None,
        "fail_stage": None,
        "audio_url": None,
        "midi_url": None,
        "musicxml_url": None,
        "metadata": None
    }

    return {
        "job_id": job_id,
        "filename": file.filename,
        "file_size": len(content),
        "status": "queued"
    }


@app.post("/convert/{job_id}")
@app.post("/api/convert/{job_id}")
async def start_conversion(
    job_id: str,
    background_tasks: BackgroundTasks,
    request: Optional[ConvertRequest] = None
):
    """Starts conversion pipeline asynchronously for a given job ID."""
    if job_id not in jobs_db:
        raise HTTPException(status_code=404, detail="Job ID not found.")

    job = jobs_db[job_id]
    
    if request and request.simulate_error:
        job["fail_stage"] = request.simulate_error

    # Execute pipeline in background task
    background_tasks.add_task(execute_pipeline, job, job["pdf_path"], OUTPUT_DIR)

    return {
        "job_id": job_id,
        "status": "processing",
        "message": "Conversion started"
    }


@app.get("/status/{job_id}")
@app.get("/api/status/{job_id}")
async def get_status(job_id: str):
    """Poll real-time status of conversion pipeline for a given job ID."""
    if job_id not in jobs_db:
        raise HTTPException(status_code=404, detail="Job ID not found.")

    job = jobs_db[job_id]

    return {
        "job_id": job_id,
        "status": job["status"],
        "stage": job["stage"],
        "progress": job["progress"],
        "error": job["error"]
    }


@app.get("/result/{job_id}")
@app.get("/api/result/{job_id}")
async def get_result(job_id: str):
    """Retrieve result links and score metadata upon successful conversion."""
    if job_id not in jobs_db:
        raise HTTPException(status_code=404, detail="Job ID not found.")

    job = jobs_db[job_id]
    if job["status"] != "done":
        raise HTTPException(status_code=400, detail=f"Job is not completed yet (current status: {job['status']}).")

    return {
        "job_id": job_id,
        "filename": job["filename"],
        "audio_url": job.get("audio_url") or f"/static/{job_id}/output.wav",
        "midi_url": job.get("midi_url") or f"/static/{job_id}/output.mid",
        "musicxml_url": job.get("musicxml_url") or f"/static/{job_id}/output.musicxml",
        "metadata": job.get("metadata") or {
            "title": os.path.splitext(job["filename"])[0].replace("_", " ").title(),
            "tempo": 120,
            "time_signature": "4/4",
            "key_signature": "C Major",
            "total_measures": 16,
            "staves_detected": 2,
            "duration_seconds": 8.0
        }
    }
