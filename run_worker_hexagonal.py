#!/usr/bin/env python3
"""
Script to run the hexagonal architecture worker
"""
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    print("Starting Bulk Document Service Worker - Hexagonal Architecture")
    print("=" * 60)
    print("Worker features:")
    print("- Processes document conversion jobs")
    print("- Uses hexagonal architecture")
    print("- Separated concerns for better maintainability")
    print("=" * 60)
    
    try:
        from interface.workers.celery_worker import celery
        print("Starting Celery worker...")
        celery.start()
    except ImportError as e:
        print(f"Error importing modules: {e}")
        print("Make sure all dependencies are installed:")
        print("pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"Error starting worker: {e}")
        sys.exit(1)
