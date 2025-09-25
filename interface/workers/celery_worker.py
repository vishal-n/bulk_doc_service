from celery import Celery
import os
import logging

from ...application.use_cases import ProcessJobUseCase
from ...application.container import container
from ...infrastructure.database.models import SessionLocal

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Celery configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
celery = Celery("worker", broker=REDIS_URL, backend=REDIS_URL)


@celery.task
def process_job_task(job_id: str):
    """Process a conversion job"""
    import asyncio
    db = SessionLocal()
    try:
        # Create use case with all dependencies
        process_job_use_case = container.create_process_job_use_case(db)
        
        # Execute use case (run async function in sync context)
        result = asyncio.run(process_job_use_case.execute(job_id))
        
        if result.success:
            logger.info(f"Job {job_id} completed successfully. Completed: {result.completed_files}, Failed: {result.failed_files}")
        else:
            logger.error(f"Job {job_id} failed: {result.error_message}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error processing job {job_id}: {str(e)}")
        raise
    finally:
        db.close()
