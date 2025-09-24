from celery import Celery
import os
import zipfile
import tempfile
import shutil
from pathlib import Path
from database import SessionLocal, Job, File, JobStatus, FileStatus
from docx_converter import convert_docx_to_pdf
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Celery configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
celery = Celery("worker", broker=REDIS_URL, backend=REDIS_URL)

@celery.task
def process_job(job_id: str):
    """Process a conversion job"""
    db = SessionLocal()
    try:
        # Get job from database
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            logger.error(f"Job {job_id} not found")
            return
        
        # Update job status to IN_PROGRESS
        job.status = JobStatus.IN_PROGRESS
        db.commit()
        
        # Get all files for this job
        files = db.query(File).filter(File.job_id == job_id).all()
        
        # Process each file
        completed_files = 0
        failed_files = 0
        
        for file_record in files:
            try:
                # Update file status to IN_PROGRESS
                file_record.status = FileStatus.IN_PROGRESS
                db.commit()
                
                # Convert the file
                input_path = f"/app/uploads/{job_id}/{file_record.filename}"
                output_path = f"/app/outputs/{job_id}/{file_record.filename.replace('.docx', '.pdf')}"
                
                # Ensure output directory exists
                Path(output_path).parent.mkdir(parents=True, exist_ok=True)
                
                # Convert DOCX to PDF
                success = convert_docx_to_pdf(input_path, output_path)
                
                if success:
                    file_record.status = FileStatus.COMPLETED
                    completed_files += 1
                    logger.info(f"Successfully converted {file_record.filename}")
                else:
                    file_record.status = FileStatus.FAILED
                    file_record.error_message = "Conversion failed"
                    failed_files += 1
                    logger.error(f"Failed to convert {file_record.filename}")
                
                db.commit()
                
            except Exception as e:
                file_record.status = FileStatus.FAILED
                file_record.error_message = str(e)
                failed_files += 1
                logger.error(f"Error processing {file_record.filename}: {str(e)}")
                db.commit()
        
        # Create zip archive if there are completed files
        if completed_files > 0:
            zip_path = f"/app/outputs/{job_id}/converted_files.zip"
            create_zip_archive(job_id, zip_path)
            
            # Update job with download URL
            job.download_url = f"/api/v1/jobs/{job_id}/download"
            job.status = JobStatus.COMPLETED
        else:
            job.status = JobStatus.FAILED
            job.error_message = "All files failed to convert"
        
        db.commit()
        logger.info(f"Job {job_id} completed. Success: {completed_files}, Failed: {failed_files}")
        
    except Exception as e:
        logger.error(f"Error processing job {job_id}: {str(e)}")
        job.status = JobStatus.FAILED
        job.error_message = str(e)
        db.commit()
    finally:
        db.close()

def create_zip_archive(job_id: str, zip_path: str):
    """Create a zip archive of all converted PDF files"""
    output_dir = f"/app/outputs/{job_id}"
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in Path(output_dir).glob("*.pdf"):
            zipf.write(file_path, file_path.name)
    
    logger.info(f"Created zip archive: {zip_path}")
