import subprocess
import os
import logging
from pathlib import Path

from ...domain.services import FileConverter
from ...domain.value_objects import ConversionResult

logger = logging.getLogger(__name__)


class LibreOfficeFileConverter(FileConverter):
    async def convert_docx_to_pdf(self, input_path: str, output_path: str) -> ConversionResult:
        """
        Convert DOCX file to PDF using LibreOffice
        """
        try:
            # Ensure input file exists
            if not os.path.exists(input_path):
                logger.error(f"Input file does not exist: {input_path}")
                return ConversionResult.failure_result(input_path, output_path, "Input file does not exist")
            
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
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                # LibreOffice creates the file with the same name but .pdf extension
                expected_pdf = Path(input_path).with_suffix('.pdf')
                if expected_pdf.exists():
                    # Move to the desired output path
                    expected_pdf.rename(output_path)
                    logger.info(f"Successfully converted {input_path} to {output_path}")
                    return ConversionResult.success_result(input_path, output_path)
                else:
                    logger.error(f"PDF file was not created: {expected_pdf}")
                    return ConversionResult.failure_result(input_path, output_path, "PDF file was not created")
            else:
                logger.error(f"LibreOffice conversion failed: {result.stderr}")
                return ConversionResult.failure_result(input_path, output_path, f"LibreOffice conversion failed: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            logger.error(f"Conversion timeout for {input_path}")
            return ConversionResult.failure_result(input_path, output_path, "Conversion timeout")
        except Exception as e:
            logger.error(f"Error converting {input_path}: {str(e)}")
            return ConversionResult.failure_result(input_path, output_path, str(e))
