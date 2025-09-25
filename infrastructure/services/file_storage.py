import os
import zipfile
import shutil
import logging
from pathlib import Path
from typing import List

from ...domain.services import FileStorage

logger = logging.getLogger(__name__)


class LocalFileStorage(FileStorage):
    async def save_uploaded_file(self, file_content: bytes, file_path: str) -> bool:
        """Save uploaded file content to the specified path"""
        try:
            # Create directory if it doesn't exist
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, "wb") as f:
                f.write(file_content)
            return True
        except Exception as e:
            logger.error(f"Error saving file {file_path}: {str(e)}")
            return False

    async def extract_zip_file(self, zip_path: str, extract_to: str) -> List[str]:
        """Extract zip file and return list of extracted file paths"""
        extracted_files = []
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                for file_info in zip_ref.infolist():
                    if not file_info.is_dir():
                        # Extract file
                        zip_ref.extract(file_info, extract_to)
                        extracted_path = os.path.join(extract_to, file_info.filename)
                        extracted_files.append(extracted_path)
            return extracted_files
        except zipfile.BadZipFile as e:
            logger.error(f"Invalid ZIP file {zip_path}: {str(e)}")
            raise ValueError("Invalid ZIP file")
        except Exception as e:
            logger.error(f"Error extracting zip file {zip_path}: {str(e)}")
            raise

    async def create_zip_archive(self, files: List[str], zip_path: str) -> bool:
        """Create a zip archive of the specified files"""
        try:
            # Create directory if it doesn't exist
            Path(zip_path).parent.mkdir(parents=True, exist_ok=True)
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in files:
                    if os.path.exists(file_path):
                        zipf.write(file_path, Path(file_path).name)
            
            logger.info(f"Created zip archive: {zip_path}")
            return True
        except Exception as e:
            logger.error(f"Error creating zip archive {zip_path}: {str(e)}")
            return False

    async def file_exists(self, file_path: str) -> bool:
        """Check if file exists"""
        return os.path.exists(file_path)

    async def create_directory(self, directory_path: str) -> bool:
        """Create directory if it doesn't exist"""
        try:
            Path(directory_path).mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            logger.error(f"Error creating directory {directory_path}: {str(e)}")
            return False
