from abc import ABC, abstractmethod
from typing import List
from .value_objects import ConversionResult, FileValidationResult


class FileConverter(ABC):
    @abstractmethod
    async def convert_docx_to_pdf(self, input_path: str, 
                                 output_path: str) -> ConversionResult:
        pass


class FileValidator(ABC):
    @abstractmethod
    async def validate_docx_file(self, file_path: str) -> 
        FileValidationResult:
        pass


class FileStorage(ABC):
    @abstractmethod
    async def save_uploaded_file(self, file_content: bytes, 
                                file_path: str) -> bool:
        pass

    @abstractmethod
    async def extract_zip_file(self, zip_path: str, 
                              extract_to: str) -> List[str]:
        pass

    @abstractmethod
    async def create_zip_archive(self, files: List[str], zip_path: str) -> bool:
        pass

    @abstractmethod
    async def file_exists(self, file_path: str) -> bool:
        pass

    @abstractmethod
    async def create_directory(self, directory_path: str) -> bool:
        pass


class JobQueue(ABC):
    @abstractmethod
    async def enqueue_job(self, job_id: str) -> bool:
        pass
