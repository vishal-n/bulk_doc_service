# Bulk Document Conversion Service

A high-performance, scalable service for converting DOCX files to PDF in bulk using FastAPI, Celery, and PostgreSQL.

## 🚀 Features

- **Bulk Processing**: Upload a ZIP file containing multiple DOCX files for batch conversion
- **Asynchronous Processing**: Uses Celery workers for background job processing
- **RESTful API**: Clean, well-documented REST API with automatic OpenAPI documentation
- **Real-time Status**: Track job progress and individual file conversion status
- **File Validation**: Validates DOCX files before processing
- **Docker Support**: Fully containerized with Docker Compose for easy deployment
- **Database Persistence**: PostgreSQL for reliable job and file status tracking
- **Redis Queue**: Redis for task queue management
- **Error Handling**: Comprehensive error handling and logging

## 🏗️ Architecture

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   FastAPI   │    │   Celery    │    │ PostgreSQL  │
│   (API)     │◄──►│  (Worker)   │◄──►│ (Database)  │
└─────────────┘    └─────────────┘    └─────────────┘
       │                   │
       ▼                   ▼
┌─────────────┐    ┌─────────────┐
│    Redis    │    │ LibreOffice │
│   (Queue)   │    │ (Converter) │
└─────────────┘    └─────────────┘
```

## 📋 Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)
- LibreOffice (for local development)

## 🚀 Quick Start

### Using Docker Compose (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd bulk_doc_service
   ```

2. **Start the services**
   ```bash
   ./start.sh
   ```
   Or manually:
   ```bash
   docker-compose up --build
   ```

3. **Access the service**
   - API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Interactive API: http://localhost:8000/redoc

### Local Development

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables**
   ```bash
   export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/bulk_doc_service"
   export REDIS_URL="redis://localhost:6379/0"
   ```

3. **Start PostgreSQL and Redis**
   ```bash
   # Using Docker
   docker run -d --name postgres -e POSTGRES_PASSWORD=postgres -p 5432:5432 postgres:15
   docker run -d --name redis -p 6379:6379 redis:7-alpine
   ```

4. **Run the application**
   ```bash
   # Terminal 1: Start the API
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   
   # Terminal 2: Start the worker
   celery -A worker.celery worker --loglevel=info
   ```

## 📚 API Documentation

### Endpoints

#### 1. Create Job
**POST** `/api/v1/jobs`

Upload a ZIP file containing DOCX files for conversion.

**Request:**
- Content-Type: `multipart/form-data`
- Body: ZIP file containing DOCX files

**Response:**
```json
{
  "job_id": "uuid-string",
  "file_count": 5
}
```

#### 2. Get Job Status
**GET** `/api/v1/jobs/{job_id}`

Get the current status of a conversion job.

**Response:**
```json
{
  "job_id": "uuid-string",
  "status": "COMPLETED",
  "created_at": "2024-01-01T12:00:00Z",
  "download_url": "/api/v1/jobs/{job_id}/download",
  "files": [
    {
      "filename": "document1.docx",
      "status": "COMPLETED",
      "error_message": null
    },
    {
      "filename": "document2.docx",
      "status": "FAILED",
      "error_message": "Invalid DOCX format"
    }
  ],
  "file_count": 2
}
```

#### 3. Download Results
**GET** `/api/v1/jobs/{job_id}/download`

Download the ZIP archive containing converted PDF files.

**Response:**
- Content-Type: `application/zip`
- Body: ZIP file containing PDF files

#### 4. Health Check
**GET** `/health`

Check if the service is running.

**Response:**
```json
{
  "status": "healthy"
}
```

### Job Statuses

- `PENDING`: Job is queued for processing
- `IN_PROGRESS`: Job is currently being processed
- `COMPLETED`: Job completed successfully
- `FAILED`: Job failed due to an error

### File Statuses

- `PENDING`: File is queued for conversion
- `IN_PROGRESS`: File is currently being converted
- `COMPLETED`: File converted successfully
- `FAILED`: File conversion failed

## 🔧 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql://postgres:postgres@localhost:5432/bulk_doc_service` | PostgreSQL connection string |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis connection string |

### Docker Compose Services

- **api**: FastAPI application server
- **worker**: Celery worker for background processing
- **db**: PostgreSQL database
- **redis**: Redis message broker

## 📁 Project Structure

```
bulk_doc_service/
├── main.py                 # FastAPI application
├── worker.py              # Celery worker configuration
├── models.py              # Pydantic models
├── database.py            # Database models and configuration
├── docx_converter.py      # Document conversion utilities
├── redis_client.py        # Redis client configuration
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker image configuration
├── docker-compose.yml    # Docker Compose configuration
├── start.sh              # Startup script
├── uploads/              # Uploaded ZIP files (created at runtime)
├── outputs/              # Converted PDF files (created at runtime)
└── temp/                 # Temporary files (created at runtime)
```

## 🛠️ Development

### Adding New Features

1. **API Endpoints**: Add new routes in `main.py`
2. **Database Models**: Add new models in `database.py`
3. **Pydantic Models**: Add response/request models in `models.py`
4. **Background Tasks**: Add new Celery tasks in `worker.py`

### Testing

```bash
# Run the test client
python test_client.py
```

### Logging

The service uses Python's built-in logging module. Logs are available in the Docker containers:

```bash
# View API logs
docker-compose logs api

# View worker logs
docker-compose logs worker
```

## 🚨 Troubleshooting

### Common Issues

1. **LibreOffice not found**
   - Ensure LibreOffice is installed in the container
   - Check the Dockerfile includes LibreOffice installation

2. **Database connection errors**
   - Verify PostgreSQL is running
   - Check DATABASE_URL environment variable

3. **Redis connection errors**
   - Verify Redis is running
   - Check REDIS_URL environment variable

4. **File conversion failures**
   - Check if DOCX files are valid
   - Verify file permissions
   - Check worker logs for detailed error messages

### Performance Tuning

- **Worker Scaling**: Increase the number of Celery workers
- **Database**: Use connection pooling for high concurrency
- **Redis**: Configure Redis for better performance
- **File Storage**: Use faster storage for uploads/outputs

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For support and questions, please open an issue in the repository or contact the development team.

---

**Note**: This service is designed for production use with proper security measures, monitoring, and backup strategies in place.