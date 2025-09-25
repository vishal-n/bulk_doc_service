from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import uuid
import zipfile
import os
import shutil
import logging

from database import (
    get_db, create_tables, Job, File as FileModel, JobStatus, FileStatus
)
from models import JobResponse, JobCreateResponse, FileInfo
from worker import process_job
from docx_converter import validate_docx_file

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Bulk Document Conversion Service",
    description="A service for converting DOCX files to PDF in bulk",
    version="1.0.0"
)


# Create database tables on startup
@app.on_event("startup")
async def startup_event():
    create_tables()
    # Create necessary directories
    os.makedirs("/app/uploads", exist_ok=True)
    os.makedirs("/app/outputs", exist_ok=True)
    os.makedirs("/app/temp", exist_ok=True)


@app.post(
    "/api/v1/jobs", 
    response_model=JobCreateResponse, 
    status_code=status.HTTP_202_ACCEPTED
)
async def create_job(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Submit a new conversion job with a zip file containing DOCX files
    """
    try:
        # Validate file type
        if not file.filename.endswith('.zip'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only ZIP files are allowed"
            )
        
        # Generate unique job ID
        job_id = str(uuid.uuid4())
        
        # Create job directory
        job_upload_dir = f"/app/uploads/{job_id}"
        job_output_dir = f"/app/outputs/{job_id}"
        os.makedirs(job_upload_dir, exist_ok=True)
        os.makedirs(job_output_dir, exist_ok=True)
        
        # Save uploaded zip file
        zip_path = f"{job_upload_dir}/uploaded_files.zip"
        with open(zip_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Extract and validate DOCX files
        docx_files = []
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                for file_info in zip_ref.infolist():
                    # Skip directories, system files, and non-DOCX files
                    if (file_info.is_dir() or
                            file_info.filename.startswith('__MACOSX/') or
                            file_info.filename.startswith('.') or
                            not file_info.filename.lower().endswith('.docx')):
                        continue
                    
                    # Extract file
                    zip_ref.extract(file_info, job_upload_dir)
                    extracted_path = f"{job_upload_dir}/{file_info.filename}"
                    
                    # Validate DOCX file
                    if validate_docx_file(extracted_path):
                        docx_files.append(file_info.filename)
                    else:
                        logger.warning(
                            f"Invalid DOCX file: {file_info.filename}"
                        )
        except zipfile.BadZipFile:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid ZIP file"
            )
        
        if not docx_files:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid DOCX files found in the ZIP"
            )
        
        # Create job record
        job = Job(
            id=job_id,
            status=JobStatus.PENDING,
            file_count=len(docx_files)
        )
        db.add(job)
        
        # Create file records
        for filename in docx_files:
            file_record = FileModel(
                job_id=job_id,
                filename=filename,
                status=FileStatus.PENDING
            )
            db.add(file_record)
        
        db.commit()
        
        # Queue the job for processing
        process_job.delay(job_id)
        
        logger.info(f"Created job {job_id} with {len(docx_files)} files")
        
        return JobCreateResponse(
            job_id=job_id,
            file_count=len(docx_files)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating job: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@app.get("/api/v1/jobs/{job_id}", response_model=JobResponse)
async def get_job_status(job_id: str, db: Session = Depends(get_db)):
    """
    Get the status of a conversion job
    """
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Get file statuses
    files = db.query(FileModel).filter(FileModel.job_id == job_id).all()
    file_infos = [
        FileInfo(
            filename=file.filename,
            status=file.status,
            error_message=file.error_message
        )
        for file in files
    ]
    
    return JobResponse(
        job_id=job.id,
        status=job.status,
        created_at=job.created_at,
        download_url=job.download_url,
        files=file_infos,
        file_count=job.file_count
    )


@app.get("/api/v1/jobs/{job_id}/download")
async def download_job_results(job_id: str, db: Session = Depends(get_db)):
    """
    Download the zip archive of converted PDF files
    """
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    if job.status == JobStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job is still pending"
        )
    
    if job.status == JobStatus.IN_PROGRESS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job is still in progress"
        )
    
    if job.status == JobStatus.FAILED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Job failed: {job.error_message or 'Unknown error'}"
        )
    
    if job.status != JobStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job is not completed yet"
        )
    
    zip_path = f"/app/outputs/{job_id}/converted_files.zip"
    if not os.path.exists(zip_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Download file not found"
        )
    
    return FileResponse(
        path=zip_path,
        filename=f"converted_files_{job_id}.zip",
        media_type="application/zip"
    )


@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
