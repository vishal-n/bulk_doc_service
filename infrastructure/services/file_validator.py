import os
import logging

from ...domain.services import FileValidator
from ...domain.value_objects import FileValidationResult

logger = logging.getLogger(__name__)


class DocxFileValidator(FileValidator):
    async def validate_docx_file(self, file_path: str) -> FileValidationResult:
        """
        Validate if the file is a valid DOCX file
        """
        try:
            if not os.path.exists(file_path):
                return FileValidationResult.invalid_file(file_path, "File does not exist")
            
            # Check file extension
            if not file_path.lower().endswith('.docx'):
                return FileValidationResult.invalid_file(file_path, "File is not a DOCX file")
            
            # Try to open with python-docx to validate
            from docx import Document
            doc = Document(file_path)
            # If we can open it, it's likely a valid DOCX
            return FileValidationResult.valid_file(file_path)
            
        except Exception as e:
            logger.error(f"Invalid DOCX file {file_path}: {str(e)}")
            return FileValidationResult.invalid_file(file_path, str(e))
