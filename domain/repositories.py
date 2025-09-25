from abc import ABC, abstractmethod
from typing import List, Optional
from .entities import JobEntity, FileEntity


class JobRepository(ABC):
    @abstractmethod
    async def create(self, job: JobEntity) -> JobEntity:
        pass

    @abstractmethod
    async def get_by_id(self, job_id: str) -> Optional[JobEntity]:
        pass

    @abstractmethod
    async def update(self, job: JobEntity) -> JobEntity:
        pass

    @abstractmethod
    async def delete(self, job_id: str) -> bool:
        pass


class FileRepository(ABC):
    @abstractmethod
    async def create(self, file: FileEntity) -> FileEntity:
        pass

    @abstractmethod
    async def get_by_job_id(self, job_id: str) -> List[FileEntity]:
        pass

    @abstractmethod
    async def update(self, file: FileEntity) -> FileEntity:
        pass

    @abstractmethod
    async def update_batch(self, files: List[FileEntity]) -> List[FileEntity]:
        pass
