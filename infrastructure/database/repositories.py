from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from ...domain.entities import JobEntity, FileEntity, JobStatus, FileStatus
from ...domain.repositories import JobRepository, FileRepository
from .models import Job, File


class SQLAlchemyJobRepository(JobRepository):
    def __init__(self, db: Session):
        self.db = db

    async def create(self, job: JobEntity) -> JobEntity:
        db_job = Job(
            id=job.id,
            status=job.status,
            file_count=job.file_count,
            download_url=job.download_url,
            error_message=job.error_message,
            created_at=job.created_at or datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        self.db.add(db_job)
        self.db.commit()
        self.db.refresh(db_job)
        return self._to_entity(db_job)

    async def get_by_id(self, job_id: str) -> Optional[JobEntity]:
        db_job = self.db.query(Job).filter(Job.id == job_id).first()
        return self._to_entity(db_job) if db_job else None

    async def update(self, job: JobEntity) -> JobEntity:
        db_job = self.db.query(Job).filter(Job.id == job.id).first()
        if db_job:
            db_job.status = job.status
            db_job.file_count = job.file_count
            db_job.download_url = job.download_url
            db_job.error_message = job.error_message
            db_job.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(db_job)
            return self._to_entity(db_job)
        return job

    async def delete(self, job_id: str) -> bool:
        db_job = self.db.query(Job).filter(Job.id == job_id).first()
        if db_job:
            self.db.delete(db_job)
            self.db.commit()
            return True
        return False

    def _to_entity(self, db_job: Job) -> JobEntity:
        return JobEntity(
            id=db_job.id,
            status=db_job.status,
            file_count=db_job.file_count,
            download_url=db_job.download_url,
            error_message=db_job.error_message,
            created_at=db_job.created_at,
            updated_at=db_job.updated_at
        )


class SQLAlchemyFileRepository(FileRepository):
    def __init__(self, db: Session):
        self.db = db

    async def create(self, file: FileEntity) -> FileEntity:
        db_file = File(
            job_id=file.job_id,
            filename=file.filename,
            status=file.status,
            error_message=file.error_message,
            created_at=file.created_at or datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        self.db.add(db_file)
        self.db.commit()
        self.db.refresh(db_file)
        return self._to_entity(db_file)

    async def get_by_job_id(self, job_id: str) -> List[FileEntity]:
        db_files = self.db.query(File).filter(File.job_id == job_id).all()
        return [self._to_entity(db_file) for db_file in db_files]

    async def update(self, file: FileEntity) -> FileEntity:
        db_file = self.db.query(File).filter(File.id == file.id).first()
        if db_file:
            db_file.status = file.status
            db_file.error_message = file.error_message
            db_file.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(db_file)
            return self._to_entity(db_file)
        return file

    async def update_batch(self, files: List[FileEntity]) -> List[FileEntity]:
        updated_files = []
        for file in files:
            updated_file = await self.update(file)
            updated_files.append(updated_file)
        return updated_files

    def _to_entity(self, db_file: File) -> FileEntity:
        return FileEntity(
            id=db_file.id,
            job_id=db_file.job_id,
            filename=db_file.filename,
            status=db_file.status,
            error_message=db_file.error_message,
            created_at=db_file.created_at,
            updated_at=db_file.updated_at
        )
