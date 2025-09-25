"""
Dependency injection container for the application
"""
from typing import Dict, Any
from ..infrastructure.database.repositories import SQLAlchemyJobRepository, SQLAlchemyFileRepository
from ..infrastructure.services.file_converter import LibreOfficeFileConverter
from ..infrastructure.services.file_validator import DocxFileValidator
from ..infrastructure.services.file_storage import LocalFileStorage
from ..infrastructure.services.job_queue import CeleryJobQueue
from .use_cases import CreateJobUseCase, GetJobStatusUseCase, ProcessJobUseCase


class Container:
    def __init__(self):
        self._services: Dict[str, Any] = {}

    def register(self, name: str, service: Any):
        """Register a service in the container"""
        self._services[name] = service

    def get(self, name: str) -> Any:
        """Get a service from the container"""
        return self._services.get(name)

    def create_job_repository(self, db_session):
        """Create job repository with database session"""
        return SQLAlchemyJobRepository(db_session)

    def create_file_repository(self, db_session):
        """Create file repository with database session"""
        return SQLAlchemyFileRepository(db_session)

    def create_file_converter(self):
        """Create file converter service"""
        return LibreOfficeFileConverter()

    def create_file_validator(self):
        """Create file validator service"""
        return DocxFileValidator()

    def create_file_storage(self):
        """Create file storage service"""
        return LocalFileStorage()

    def create_job_queue(self):
        """Create job queue service"""
        return CeleryJobQueue()

    def create_create_job_use_case(self, db_session):
        """Create the create job use case with all dependencies"""
        return CreateJobUseCase(
            job_repository=self.create_job_repository(db_session),
            file_repository=self.create_file_repository(db_session),
            file_validator=self.create_file_validator(),
            file_storage=self.create_file_storage(),
            job_queue=self.create_job_queue()
        )

    def create_get_job_status_use_case(self, db_session):
        """Create the get job status use case with all dependencies"""
        return GetJobStatusUseCase(
            job_repository=self.create_job_repository(db_session),
            file_repository=self.create_file_repository(db_session)
        )

    def create_process_job_use_case(self, db_session):
        """Create the process job use case with all dependencies"""
        return ProcessJobUseCase(
            job_repository=self.create_job_repository(db_session),
            file_repository=self.create_file_repository(db_session),
            file_converter=self.create_file_converter(),
            file_storage=self.create_file_storage()
        )


# Global container instance
container = Container()
