from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from database import JobStatus, FileStatus

class FileInfo(BaseModel):
    filename: str
    status: FileStatus
    error_message: Optional[str] = None

class JobResponse(BaseModel):
    job_id: str
    status: JobStatus
    created_at: datetime
    download_url: Optional[str] = None
    files: List[FileInfo]
    file_count: int

class JobCreateResponse(BaseModel):
    job_id: str
    file_count: int

class ErrorResponse(BaseModel):
    detail: str
