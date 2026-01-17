import sqlite3
import json
from typing import List, Optional
from datetime import datetime
from storage.models import Job, JobStatus
from utils.logger import app_logger

class JobDatabase:
    def __init__(self, db_path: str = "whisperwatch.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS jobs (
                id TEXT PRIMARY KEY,
                filename TEXT,
                filepath TEXT,
                created_at TEXT,
                status TEXT,
                result TEXT,
                error TEXT,
                model_used TEXT,
                processing_time REAL
            )
        ''')
        conn.commit()
        conn.close()

    def add_job(self, job: Job):
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute('''
                INSERT INTO jobs (id, filename, filepath, created_at, status, result, error, model_used, processing_time)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                job.id, 
                job.filename, 
                job.filepath, 
                job.created_at.isoformat(), 
                job.status.value, 
                job.result.model_dump_json() if job.result else None, 
                job.error,
                job.model_used,
                job.processing_time
            ))
            conn.commit()
            conn.close()
        except Exception as e:
            app_logger.error(f"DB Error add_job: {e}")

    def update_job_status(self, job_id: str, status: JobStatus, result=None, error=None, processing_time=None):
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            updates = ["status = ?"]
            params = [status.value]

            if result:
                updates.append("result =?")
                params.append(result.model_dump_json())
            if error:
                updates.append("error = ?")
                params.append(str(error))
            if processing_time:
                updates.append("processing_time = ?")
                params.append(processing_time)
            
            params.append(job_id)
            
            query = f"UPDATE jobs SET {', '.join(updates)} WHERE id = ?"
            c.execute(query, params)
            conn.commit()
            conn.close()
        except Exception as e:
            app_logger.error(f"DB Error update_job_status: {e}")

    def get_job(self, job_id: str) -> Optional[Job]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM jobs WHERE id = ?", (job_id,))
        row = c.fetchone()
        conn.close()
        if row:
            return self._row_to_job(row)
        return None

    def get_all_jobs(self, limit=50) -> List[Job]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM jobs ORDER BY created_at DESC LIMIT ?", (limit,))
        rows = c.fetchall()
        conn.close()
        return [self._row_to_job(row) for row in rows]

    def _row_to_job(self, row) -> Job:
        return Job(
            id=row['id'],
            filename=row['filename'],
            filepath=row['filepath'],
            created_at=datetime.fromisoformat(row['created_at']),
            status=JobStatus(row['status']),
            result=json.loads(row['result']) if row['result'] else None,
            error=row['error'],
            model_used=row['model_used'],
            processing_time=row['processing_time']
        )

# Global DB instance
db = JobDatabase()
