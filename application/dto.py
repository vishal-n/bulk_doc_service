from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from ..domain.entities import JobStatus, FileStatus


class FileInfoDto(BaseModel):
    filename: str
    status: FileStatus
    error_message: Optional[str] = None


class JobResponseDto(BaseModel):
    job_id: str
    status: JobStatus
    created_at: datetime
    download_url: Optional[str] = None
    files: List[FileInfoDto]
    file_count: int


class JobCreateResponseDto(BaseModel):
    job_id: str
    file_count: int


class ErrorResponseDto(BaseModel):
    detail: str
