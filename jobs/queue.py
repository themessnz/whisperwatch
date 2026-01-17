import threading
import time
import uuid
from datetime import datetime
from queue import Queue
from storage.db import db
from storage.models import Job, JobStatus
from utils.logger import app_logger

class JobManager:
    def __init__(self):
        self.job_queue = Queue()
        self.active_jobs = {} # Map job_id to thread/status if needed for monitoring

    def create_job(self, filepath: str) -> Job:
        job_id = str(uuid.uuid4())
        filename = filepath.split('/')[-1]
        
        job = Job(
            id=job_id,
            filename=filename,
            filepath=filepath,
            created_at=datetime.now(),
            status=JobStatus.QUEUED
        )
        
        db.add_job(job)
        self.job_queue.put(job)
        app_logger.info(f"Job created and queued: {job_id} for {filename}")
        return job

    def get_next_job(self):
        return self.job_queue.get()

    def mark_done(self):
        self.job_queue.task_done()

# Global Job Queue
job_manager = JobManager()
