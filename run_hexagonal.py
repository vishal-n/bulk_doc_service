#!/usr/bin/env python3
"""
Script to run the hexagonal architecture version of the bulk document service
"""
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    print("Starting Bulk Document Service - Hexagonal Architecture")
    print("=" * 60)
    print("Architecture layers:")
    print("1. Domain Layer: Core business logic")
    print("2. Application Layer: Use cases and DTOs")
    print("3. Infrastructure Layer: Database and external services")
    print("4. Interface Layer: REST API and Celery workers")
    print("=" * 60)
    
    try:
        from interface.api.controllers import app
        import uvicorn
        print("Starting FastAPI server...")
        uvicorn.run(app, host="0.0.0.0", port=8000)
    except ImportError as e:
        print(f"Error importing modules: {e}")
        print("Make sure all dependencies are installed:")
        print("pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)
