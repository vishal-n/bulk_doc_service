"""
Worker entry point for the hexagonal architecture version of the bulk document service
"""
from interface.workers.celery_worker import celery

if __name__ == "__main__":
    celery.start()
