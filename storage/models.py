from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime
from enum import Enum

class JobStatus(str, Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class TranscriptionSegment(BaseModel):
    start: float
    end: float
    text: str

class TranscriptResult(BaseModel):
    segments: List[TranscriptionSegment]
    language: str
    duration: float

class Job(BaseModel):
    id: str
    filename: str
    filepath: str
    created_at: datetime
    status: JobStatus = JobStatus.QUEUED
    result: Optional[TranscriptResult] = None
    error: Optional[str] = None
    model_used: Optional[str] = None
    processing_time: Optional[float] = None
