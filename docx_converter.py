import subprocess
import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def convert_docx_to_pdf(input_path: str, output_path: str) -> bool:
    """
    Convert DOCX file to PDF using LibreOffice
    """
    try:
        # Ensure input file exists
        if not os.path.exists(input_path):
            logger.error(f"Input file does not exist: {input_path}")
            return False
        
        # Validate input file before conversion
        if not validate_docx_file(input_path):
            logger.error(f"Input file is not a valid DOCX: {input_path}")
            return False
        
        # Create output directory if it doesn't exist
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Use LibreOffice to convert DOCX to PDF
        cmd = [
            "libreoffice",
            "--headless",
            "--convert-to", "pdf",
            "--outdir", str(Path(output_path).parent),
            input_path
        ]
        
        logger.info(f"Converting {input_path} to PDF...")
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=120
        )
        
        if result.returncode == 0:
            # LibreOffice creates the file with the same name but .pdf extension
            expected_pdf = Path(input_path).with_suffix('.pdf')
            if expected_pdf.exists() and expected_pdf.stat().st_size > 0:
                # Move to the desired output path
                expected_pdf.rename(output_path)
                logger.info(
                    f"Successfully converted {input_path} to {output_path}"
                )
                return True
            else:
                logger.error(
                    f"PDF file was not created or is empty: {expected_pdf}"
                )
                return False
        else:
            logger.error(f"LibreOffice conversion failed for {input_path}")
            logger.error(f"Return code: {result.returncode}")
            logger.error(f"STDOUT: {result.stdout}")
            logger.error(f"STDERR: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        logger.error(f"Conversion timeout for {input_path}")
        return False
    except Exception as e:
        logger.error(f"Error converting {input_path}: {str(e)}")
        return False

def validate_docx_file(file_path: str) -> bool:
    """
    Validate if the file is a valid DOCX file
    """
    try:
        if not os.path.exists(file_path):
            return False
        
        # Check file extension
        if not file_path.lower().endswith('.docx'):
            return False
        
        # Check file size (must be > 0 bytes)
        if os.path.getsize(file_path) == 0:
            return False
        
        # Check if it's a valid ZIP file (DOCX is a ZIP archive)
        import zipfile
        try:
            with zipfile.ZipFile(file_path, 'r') as zip_file:
                # Check if it contains the required DOCX structure
                required_files = ['[Content_Types].xml', 'word/document.xml']
                if not all(file in zip_file.namelist() for file in required_files):
                    return False
        except zipfile.BadZipFile:
            return False
        
        # Try to open with python-docx to validate
        from docx import Document
        Document(file_path)
        # If we can open it, it's likely a valid DOCX
        return True
        
    except Exception as e:
        logger.error(f"Invalid DOCX file {file_path}: {str(e)}")
        return False
