# Bulk Document Service - Hexagonal Architecture

This is the refactored version of the bulk document conversion service following hexagonal architecture principles.

## Architecture Overview

The codebase is organized into four main layers:

### 1. Domain Layer (`domain/`)
Contains the core business logic and entities:
- **Entities**: `JobEntity`, `FileEntity` - Core business objects
- **Value Objects**: `ConversionResult`, `JobProcessingResult`, `FileValidationResult`
- **Repositories**: Abstract interfaces for data persistence
- **Services**: Abstract interfaces for external services

### 2. Application Layer (`application/`)
Contains use cases and application services:
- **Use Cases**: `CreateJobUseCase`, `GetJobStatusUseCase`, `ProcessJobUseCase`
- **DTOs**: Data transfer objects for API responses
- **Container**: Dependency injection container

### 3. Infrastructure Layer (`infrastructure/`)
Contains concrete implementations of domain interfaces:
- **Database**: SQLAlchemy models and repositories
- **Services**: File converter, validator, storage, and job queue implementations

### 4. Interface Layer (`interface/`)
Contains external interfaces:
- **API**: FastAPI controllers and endpoints
- **Workers**: Celery task workers

## Key Benefits of Hexagonal Architecture

1. **Separation of Concerns**: Each layer has a clear responsibility
2. **Testability**: Easy to mock dependencies and test business logic in isolation
3. **Flexibility**: Can easily swap implementations (e.g., change database or file storage)
4. **Maintainability**: Changes to one layer don't affect others
5. **Dependency Inversion**: High-level modules don't depend on low-level modules

## Project Structure

```
bulk_doc_service/
├── domain/                    # Core business logic
│   ├── entities.py           # Business entities
│   ├── value_objects.py      # Value objects
│   ├── repositories.py       # Repository interfaces
│   └── services.py           # Service interfaces
├── application/              # Application logic
│   ├── use_cases.py         # Use cases
│   ├── dto.py               # Data transfer objects
│   └── container.py         # Dependency injection
├── infrastructure/          # External concerns
│   ├── database/           # Database implementations
│   └── services/           # External service implementations
├── interface/              # External interfaces
│   ├── api/               # REST API
│   └── workers/           # Celery workers
├── main_hexagonal.py      # New main entry point
├── worker_hexagonal.py    # New worker entry point
└── README_HEXAGONAL.md    # This file
```

## Running the Application

### Using the Hexagonal Architecture Version

1. **Start the API server:**
   ```bash
   python main_hexagonal.py
   ```

2. **Start the worker:**
   ```bash
   python worker_hexagonal.py
   ```

### Using the Original Version

1. **Start the API server:**
   ```bash
   python main.py
   ```

2. **Start the worker:**
   ```bash
   python worker.py
   ```

## Migration Benefits

The hexagonal architecture refactoring provides:

1. **Better Testability**: Each use case can be tested independently
2. **Easier Maintenance**: Changes to external services don't affect business logic
3. **Flexible Deployment**: Can easily swap implementations for different environments
4. **Clear Boundaries**: Each layer has well-defined responsibilities
5. **Future-Proof**: Easy to add new features or change external dependencies

## Example: Adding a New File Format

To add support for a new file format (e.g., RTF), you would:

1. **Domain Layer**: Add new value objects and update entities if needed
2. **Application Layer**: Update use cases to handle the new format
3. **Infrastructure Layer**: Implement the new converter service
4. **Interface Layer**: No changes needed - the API remains the same

This demonstrates the power of hexagonal architecture - the core business logic remains unchanged while external implementations can be easily swapped or extended.
