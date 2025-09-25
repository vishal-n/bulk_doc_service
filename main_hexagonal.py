"""
Main entry point for the hexagonal architecture version of the bulk document service
"""
from interface.api.controllers import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
