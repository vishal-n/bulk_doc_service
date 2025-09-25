from typing import List, Optional
import uuid
import logging
from datetime import datetime

from ..domain.entities import JobEntity, FileEntity, JobStatus, FileStatus
from ..domain.value_objects import JobProcessingResult, ConversionResult
from ..domain.repositories import JobRepository, FileRepository
from ..domain.services import FileConverter, FileValidator, FileStorage, JobQueue

logger = logging.getLogger(__name__)


class CreateJobUseCase:
    def __init__(
        self,
        job_repository: JobRepository,
        file_repository: FileRepository,
        file_validator: FileValidator,
        file_storage: FileStorage,
        job_queue: JobQueue
    ):
        self.job_repository = job_repository
        self.file_repository = file_repository
        self.file_validator = file_validator
        self.file_storage = file_storage
        self.job_queue = job_queue

    async def execute(self, zip_content: bytes, zip_filename: str) -> JobEntity:
        # Generate unique job ID
        job_id = str(uuid.uuid4())
        
        # Create job directories
        job_upload_dir = f"/app/uploads/{job_id}"
        job_output_dir = f"/app/outputs/{job_id}"
        
        await self.file_storage.create_directory(job_upload_dir)
        await self.file_storage.create_directory(job_output_dir)
        
        # Save uploaded zip file
        zip_path = f"{job_upload_dir}/uploaded_files.zip"
        await self.file_storage.save_uploaded_file(zip_content, zip_path)
        
        # Extract and validate DOCX files
        extracted_files = await self.file_storage.extract_zip_file(zip_path, job_upload_dir)
        valid_docx_files = []
        
        for file_path in extracted_files:
            if file_path.endswith('.docx'):
                validation_result = await self.file_validator.validate_docx_file(file_path)
                if validation_result.is_valid:
                    valid_docx_files.append(file_path)
                else:
                    logger.warning(f"Invalid DOCX file: {file_path}")
        
        if not valid_docx_files:
            raise ValueError("No valid DOCX files found in the ZIP")
        
        # Create job entity
        job = JobEntity(
            id=job_id,
            status=JobStatus.PENDING,
            file_count=len(valid_docx_files),
            created_at=datetime.utcnow()
        )
        
        # Create file entities
        for file_path in valid_docx_files:
            filename = file_path.split('/')[-1]
            file_entity = FileEntity(
                id=None,
                job_id=job_id,
                filename=filename,
                status=FileStatus.PENDING,
                created_at=datetime.utcnow()
            )
            job.add_file(file_entity)
        
        # Save to repositories
        saved_job = await self.job_repository.create(job)
        for file_entity in job.files:
            await self.file_repository.create(file_entity)
        
        # Queue the job for processing
        await self.job_queue.enqueue_job(job_id)
        
        logger.info(f"Created job {job_id} with {len(valid_docx_files)} files")
        return saved_job


class GetJobStatusUseCase:
    def __init__(self, job_repository: JobRepository, file_repository: FileRepository):
        self.job_repository = job_repository
        self.file_repository = file_repository

    async def execute(self, job_id: str) -> Optional[JobEntity]:
        job = await self.job_repository.get_by_id(job_id)
        if job:
            files = await self.file_repository.get_by_job_id(job_id)
            job.files = files
        return job


class ProcessJobUseCase:
    def __init__(
        self,
        job_repository: JobRepository,
        file_repository: FileRepository,
        file_converter: FileConverter,
        file_storage: FileStorage
    ):
        self.job_repository = job_repository
        self.file_repository = file_repository
        self.file_converter = file_converter
        self.file_storage = file_storage

    async def execute(self, job_id: str) -> JobProcessingResult:
        try:
            # Get job from repository
            job = await self.job_repository.get_by_id(job_id)
            if not job:
                logger.error(f"Job {job_id} not found")
                return JobProcessingResult.failure_result(job_id, "Job not found")
            
            # Update job status to IN_PROGRESS
            job.mark_in_progress()
            await self.job_repository.update(job)
            
            # Get all files for this job
            files = await self.file_repository.get_by_job_id(job_id)
            job.files = files
            
            # Process each file
            completed_files = 0
            failed_files = 0
            
            for file_entity in files:
                try:
                    # Update file status to IN_PROGRESS
                    file_entity.mark_in_progress()
                    await self.file_repository.update(file_entity)
                    
                    # Convert the file
                    input_path = f"/app/uploads/{job_id}/{file_entity.filename}"
                    output_path = f"/app/outputs/{job_id}/{file_entity.filename.replace('.docx', '.pdf')}"
                    
                    # Ensure output directory exists
                    await self.file_storage.create_directory(str(output_path).rsplit('/', 1)[0])
                    
                    # Convert DOCX to PDF
                    conversion_result = await self.file_converter.convert_docx_to_pdf(input_path, output_path)
                    
                    if conversion_result.success:
                        file_entity.mark_completed()
                        completed_files += 1
                        logger.info(f"Successfully converted {file_entity.filename}")
                    else:
                        file_entity.mark_failed(conversion_result.error_message or "Conversion failed")
                        failed_files += 1
                        logger.error(f"Failed to convert {file_entity.filename}")
                    
                    await self.file_repository.update(file_entity)
                    
                except Exception as e:
                    file_entity.mark_failed(str(e))
                    failed_files += 1
                    logger.error(f"Error processing {file_entity.filename}: {str(e)}")
                    await self.file_repository.update(file_entity)
            
            # Create zip archive if there are completed files
            if completed_files > 0:
                zip_path = f"/app/outputs/{job_id}/converted_files.zip"
                pdf_files = [f"/app/outputs/{job_id}/{f.filename.replace('.docx', '.pdf')}" 
                           for f in files if f.status == FileStatus.COMPLETED]
                
                await self.file_storage.create_zip_archive(pdf_files, zip_path)
                
                # Update job with download URL
                download_url = f"/api/v1/jobs/{job_id}/download"
                job.mark_completed(download_url)
            else:
                job.mark_failed("All files failed to convert")
            
            await self.job_repository.update(job)
            logger.info(f"Job {job_id} completed. Success: {completed_files}, Failed: {failed_files}")
            
            return JobProcessingResult.success_result(job_id, completed_files, failed_files)
            
        except Exception as e:
            logger.error(f"Error processing job {job_id}: {str(e)}")
            job.mark_failed(str(e))
            await self.job_repository.update(job)
            return JobProcessingResult.failure_result(job_id, str(e))
