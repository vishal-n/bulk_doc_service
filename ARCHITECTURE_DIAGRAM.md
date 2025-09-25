# Hexagonal Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        INTERFACE LAYER                         │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐    ┌─────────────────────────────────────┐ │
│  │   REST API      │    │         Celery Workers              │ │
│  │   Controllers   │    │                                     │ │
│  │                 │    │  - process_job_task                 │ │
│  │ - create_job    │    │  - File conversion processing       │ │
│  │ - get_job_status│    │                                     │ │
│  │ - download_job  │    │                                     │ │
│  └─────────────────┘    └─────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      APPLICATION LAYER                         │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐    ┌─────────────────────────────────────┐ │
│  │   Use Cases     │    │              DTOs                    │ │
│  │                 │    │                                     │ │
│  │ - CreateJob     │    │ - JobResponseDto                    │ │
│  │ - GetJobStatus  │    │ - JobCreateResponseDto              │ │
│  │ - ProcessJob    │    │ - FileInfoDto                       │ │
│  │                 │    │                                     │ │
│  └─────────────────┘    └─────────────────────────────────────┘ │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │              Dependency Injection Container                 │ │
│  │                                                             │ │
│  │ - Manages service dependencies                              │ │
│  │ - Creates use cases with proper dependencies                │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                        DOMAIN LAYER                            │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐    ┌─────────────────────────────────────┐ │
│  │    Entities     │    │           Value Objects              │ │
│  │                 │    │                                     │ │
│  │ - JobEntity     │    │ - ConversionResult                  │ │
│  │ - FileEntity    │    │ - JobProcessingResult               │ │
│  │                 │    │ - FileValidationResult              │ │
│  └─────────────────┘    └─────────────────────────────────────┘ │
│  ┌─────────────────┐    ┌─────────────────────────────────────┐ │
│  │   Repositories  │    │              Services                │ │
│  │   (Interfaces)  │    │            (Interfaces)             │ │
│  │                 │    │                                     │ │
│  │ - JobRepository │    │ - FileConverter                     │ │
│  │ - FileRepository│    │ - FileValidator                     │ │
│  │                 │    │ - FileStorage                       │ │
│  │                 │    │ - JobQueue                          │ │
│  └─────────────────┘    └─────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    INFRASTRUCTURE LAYER                        │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐    ┌─────────────────────────────────────┐ │
│  │    Database     │    │            Services                  │ │
│  │   Adapters      │    │            Adapters                  │ │
│  │                 │    │                                     │ │
│  │ - SQLAlchemy    │    │ - LibreOfficeFileConverter          │ │
│  │   JobRepository │    │ - DocxFileValidator                 │ │
│  │ - SQLAlchemy    │    │ - LocalFileStorage                  │ │
│  │   FileRepository│    │ - CeleryJobQueue                    │ │
│  │                 │    │                                     │ │
│  └─────────────────┘    └─────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Key Principles

1. **Dependency Inversion**: High-level modules don't depend on low-level modules
2. **Separation of Concerns**: Each layer has a single responsibility
3. **Testability**: Easy to mock dependencies and test in isolation
4. **Flexibility**: Can swap implementations without changing business logic
5. **Maintainability**: Changes to one layer don't affect others

## Data Flow

1. **Request comes in** → Interface Layer (REST API)
2. **Use case execution** → Application Layer (Use Cases)
3. **Business logic** → Domain Layer (Entities & Services)
4. **Data persistence** → Infrastructure Layer (Database Adapters)
5. **External services** → Infrastructure Layer (Service Adapters)

## Benefits

- **Testable**: Each layer can be tested independently
- **Maintainable**: Clear separation of concerns
- **Flexible**: Easy to change implementations
- **Scalable**: Can add new features without affecting existing code
- **Clean**: Business logic is isolated from external concerns
