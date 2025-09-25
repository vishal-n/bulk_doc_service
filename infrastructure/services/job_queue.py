import os
import logging
from celery import Celery

from ...domain.services import JobQueue

logger = logging.getLogger(__name__)


class CeleryJobQueue(JobQueue):
    def __init__(self):
        REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.celery = Celery("worker", broker=REDIS_URL, backend=REDIS_URL)

    async def enqueue_job(self, job_id: str) -> bool:
        """Enqueue a job for processing"""
        try:
            # Import here to avoid circular imports
            from ...interface.workers import process_job_task
            process_job_task.delay(job_id)
            logger.info(f"Enqueued job {job_id} for processing")
            return True
        except Exception as e:
            logger.error(f"Error enqueueing job {job_id}: {str(e)}")
            return False
