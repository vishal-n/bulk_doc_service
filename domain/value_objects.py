from dataclasses import dataclass
from typing import Optional


@dataclass
class ConversionResult:
    success: bool
    input_path: str
    output_path: str
    error_message: Optional[str] = None

    @classmethod
    def success_result(cls, input_path: str, output_path: str) -> 'ConversionResult':
        return cls(success=True, input_path=input_path, output_path=output_path)

    @classmethod
    def failure_result(cls, input_path: str, output_path: str, 
                      error_message: str) -> 'ConversionResult':
        return cls(success=False, input_path=input_path, 
                  output_path=output_path, error_message=error_message)


@dataclass
class JobProcessingResult:
    job_id: str
    completed_files: int
    failed_files: int
    success: bool
    error_message: Optional[str] = None

    @classmethod
    def success_result(cls, job_id: str, completed_files: int, 
                      failed_files: int) -> 'JobProcessingResult':
        return cls(
            job_id=job_id,
            completed_files=completed_files,
            failed_files=failed_files,
            success=True
        )

    @classmethod
    def failure_result(cls, job_id: str, 
                      error_message: str) -> 'JobProcessingResult':
        return cls(
            job_id=job_id,
            completed_files=0,
            failed_files=0,
            success=False,
            error_message=error_message
        )


@dataclass
class FileValidationResult:
    is_valid: bool
    filename: str
    error_message: Optional[str] = None

    @classmethod
    def valid_file(cls, filename: str) -> 'FileValidationResult':
        return cls(is_valid=True, filename=filename)

    @classmethod
    def invalid_file(cls, filename: str, 
                    error_message: str) -> 'FileValidationResult':
        return cls(is_valid=False, filename=filename, 
                  error_message=error_message)
