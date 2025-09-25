from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from enum import Enum


class JobStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class FileStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


@dataclass
class FileEntity:
    id: Optional[int]
    job_id: str
    filename: str
    status: FileStatus
    error_message: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def mark_in_progress(self):
        self.status = FileStatus.IN_PROGRESS

    def mark_completed(self):
        self.status = FileStatus.COMPLETED

    def mark_failed(self, error_message: str):
        self.status = FileStatus.FAILED
        self.error_message = error_message


@dataclass
class JobEntity:
    id: str
    status: JobStatus
    file_count: int
    download_url: Optional[str] = None
    error_message: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    files: List[FileEntity] = None

    def __post_init__(self):
        if self.files is None:
            self.files = []

    def mark_in_progress(self):
        self.status = JobStatus.IN_PROGRESS

    def mark_completed(self, download_url: str):
        self.status = JobStatus.COMPLETED
        self.download_url = download_url

    def mark_failed(self, error_message: str):
        self.status = JobStatus.FAILED
        self.error_message = error_message

    def add_file(self, file: FileEntity):
        self.files.append(file)

    def get_completed_files_count(self) -> int:
        return len([f for f in self.files if f.status == FileStatus.COMPLETED])

    def get_failed_files_count(self) -> int:
        return len([f for f in self.files if f.status == FileStatus.FAILED])
