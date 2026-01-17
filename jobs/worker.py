import threading
import time
import os
from jobs.queue import job_manager
from transcription.engine import engine
from transcription.utils import save_transcript
from storage.db import db
from storage.models import JobStatus, TranscriptResult
from config.manager import config
from utils.logger import app_logger

def worker_loop():
    app_logger.info("Worker thread started.")
    while True:
        try:
            job = job_manager.get_next_job()
            if job is None:
                break
            
            process_job(job)
            job_manager.mark_done()
        except Exception as e:
            app_logger.error(f"Worker loop error: {e}")

def process_job(job):
    app_logger.info(f"Processing job {job.id}: {job.filename}")
    db.update_job_status(job.id, JobStatus.PROCESSING)
    
    start_time = time.time()
    try:
        if not os.path.exists(job.filepath):
             raise FileNotFoundError(f"File not found: {job.filepath}")

        # Run transcription
        result_data = engine.transcribe(job.filepath)
        
        # Save Outputs
        output_conf = config.get("output", {})
        output_dir = output_conf.get("output_dir", "/workspace/transcripts")
        formats = output_conf.get("formats", ["json", "txt"])
        
        # Use filename without extension for output
        file_stem = os.path.splitext(job.filename)[0]
        save_transcript(result_data, output_dir, file_stem, formats)
        
        processing_time = time.time() - start_time
        
        # Convert to Pydantic model for consistency with DB but retain dict structure for saving
        # Simplification: we might just store the dict in DB as JSON
        
        # Update DB
        # Construct TranscriptResult object
        trans_result = TranscriptResult(
            segments=result_data['segments'],
            language=result_data['language'],
            duration=result_data['duration']
        )

        db.update_job_status(
            job.id, 
            JobStatus.COMPLETED, 
            result=trans_result,
            processing_time=processing_time,
            error=None
        )
        app_logger.info(f"Job {job.id} completed in {processing_time:.2f}s")
        
    except Exception as e:
        app_logger.error(f"Job {job.id} failed: {e}")
        processing_time = time.time() - start_time
        db.update_job_status(
            job.id, 
            JobStatus.FAILED, 
            error=str(e),
            processing_time=processing_time
        )

def start_worker():
    t = threading.Thread(target=worker_loop, daemon=True)
    t.start()
    return t
