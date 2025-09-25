from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import logging

from ...application.use_cases import CreateJobUseCase, GetJobStatusUseCase
from ...application.dto import JobResponseDto, JobCreateResponseDto, ErrorResponseDto, FileInfoDto
from ...application.container import container
from ...infrastructure.database.models import get_db, create_tables

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
    import os
    os.makedirs("/app/uploads", exist_ok=True)
    os.makedirs("/app/outputs", exist_ok=True)
    os.makedirs("/app/temp", exist_ok=True)


def get_create_job_use_case(db: Session = Depends(get_db)) -> CreateJobUseCase:
    return container.create_create_job_use_case(db)


def get_get_job_status_use_case(db: Session = Depends(get_db)) -> GetJobStatusUseCase:
    return container.create_get_job_status_use_case(db)


@app.post(
    "/api/v1/jobs", 
    response_model=JobCreateResponseDto, 
    status_code=status.HTTP_202_ACCEPTED
)
async def create_job(
    file: UploadFile = File(...),
    create_job_use_case: CreateJobUseCase = Depends(get_create_job_use_case)
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
        
        # Read file content
        file_content = await file.read()
        
        # Execute use case
        job = await create_job_use_case.execute(file_content, file.filename)
        
        return JobCreateResponseDto(
            job_id=job.id,
            file_count=job.file_count
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating job: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@app.get("/api/v1/jobs/{job_id}", response_model=JobResponseDto)
async def get_job_status(
    job_id: str,
    get_job_use_case: GetJobStatusUseCase = Depends(get_get_job_status_use_case)
):
    """
    Get the status of a conversion job
    """
    # Execute use case
    job = await get_job_use_case.execute(job_id)
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Convert files to DTOs
    file_infos = [
        FileInfoDto(
            filename=file.filename,
            status=file.status,
            error_message=file.error_message
        )
        for file in job.files
    ]
    
    return JobResponseDto(
        job_id=job.id,
        status=job.status,
        created_at=job.created_at,
        download_url=job.download_url,
        files=file_infos,
        file_count=job.file_count
    )


@app.get("/api/v1/jobs/{job_id}/download")
async def download_job_results(
    job_id: str,
    db: Session = Depends(get_db)
):
    """
    Download the zip archive of converted PDF files
    """
    job_repo = container.create_job_repository(db)
    job = await job_repo.get_by_id(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    if job.status != "COMPLETED":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job is not completed yet"
        )
    
    zip_path = f"/app/outputs/{job_id}/converted_files.zip"
    import os
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
