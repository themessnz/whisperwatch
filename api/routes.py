from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from typing import List, Optional
from pydantic import BaseModel
import shutil
import os
import uuid

from storage.db import db
from storage.models import Job, JobStatus
from config.manager import config
from jobs.queue import job_manager
from utils.logger import app_logger

router = APIRouter()

class ConfigUpdate(BaseModel):
    section: str
    settings: dict

@router.get("/status")
def get_service_status():
    return {"status": "running", "uptime": "todo"}

@router.get("/jobs", response_model=List[Job])
def list_jobs(limit: int = 50):
    return db.get_all_jobs(limit)

@router.get("/jobs/{job_id}", response_model=Job)
def get_job_details(job_id: str):
    job = db.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@router.post("/transcribe")
async def manual_upload(file: UploadFile = File(...)):
    # Save uploaded file to a specific upload dir or just one of the watch dirs?
    # Let's save to a dedicated uploads folder in media path to avoid circular watcher trigger if possible, 
    # but watcher is configured on paths. If we drop it there, watcher picks it up.
    # But if we want manual trigger, saving to a NON-watched folder and calling create_job is safer.
    
    upload_dir = "/workspace/uploads"
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
        
    file_path = os.path.join(upload_dir, file.filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    job = job_manager.create_job(file_path)
    return job

@router.get("/config/models")
def get_available_models():
    # Return what logic is supported or what is currently configured vs available?
    # faster-whisper supports these roughly
    return {
        "models": ["tiny", "base", "small", "medium", "large-v3"],
        "devices": ["cpu", "cuda"],
        "compute_types": ["int8", "int8_float16", "float16", "float32"],
        "current": config.get("model")
    }

@router.get("/config")
def get_full_config():
    # Exposing raw config dict
    return config._config

@router.post("/config/model")
def update_model_config(conf: dict):
    # Expects dict with name, device, compute_type
    current_model_conf = config.get("model", {})
    current_model_conf.update(conf)
    config.update({"model": current_model_conf})
    
    # Trigger reload in engine? The worker imports 'engine'. 
    # The 'engine' checks config on every 'transcribe' call, 
    # but strictly speaking `reload_model()` is called inside `transcribe` only if not loaded?
    # No, `transcribe` calls `reload_model` which checks config hash.
    # So next job will pick up new model.
    
    return {"status": "updated", "config": current_model_conf}
