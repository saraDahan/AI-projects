# Architecture

## Overview

```
┌─────────────┐     HTTP      ┌──────────────────┐
│  wwwroot    │ ────────────► │ TasksController  │
│  (UI/JS)    │   /api/tasks  └────────┬─────────┘
└─────────────┘                        │
                                       ▼
                              ┌──────────────────┐
                              │ ITaskItemRepo    │
                              │ (interface)      │
                              └────────┬─────────┘
                                       │
                                       ▼
                              ┌──────────────────┐
                              │ TaskItemRepo     │
                              └────────┬─────────┘
                                       │
                                       ▼
                              ┌──────────────────┐
                              │ AppDbContext     │
                              │ (EF Core)        │
                              └────────┬─────────┘
                                       │
                                       ▼
                              ┌──────────────────┐
                              │ SQLite (tasks.db)│
                              └──────────────────┘
```

## Layers

### 1. Presentation — UI

- `wwwroot/` — static HTML, CSS, and JavaScript files
- Communicates with the API via `fetch`
- RTL support (Hebrew layout)

### 2. API — Controllers

- `TasksController` — maps HTTP requests to repository calls
- DTOs (`CreateTaskItemDto`, `UpdateTaskItemDto`) with Data Annotations for validation
- Throws `NotFoundException` when a task is not found

### 3. Business / Data Access — Repository

- `ITaskItemRepository` — abstract contract
- `TaskItemRepository` — implementation using EF Core
- All operations are **async**

### 4. Data — Entity Framework Core

- `AppDbContext` — DbContext with Fluent API configuration
- `TaskItem` — entity
- `SeedData` — 3 sample tasks loaded on first run

## Dependency Injection

Registered in `Program.cs`:

```csharp
builder.Services.AddDbContext<AppDbContext>(...);
builder.Services.AddScoped<ITaskItemRepository, TaskItemRepository>();
```

| Service | Lifetime |
|---------|----------|
| `AppDbContext` | Scoped |
| `ITaskItemRepository` | Scoped |

## Middleware Pipeline

```
Request
  → GlobalExceptionHandlerMiddleware
  → Swagger (Development)
  → Static Files (wwwroot)
  → HTTPS Redirection
  → Authorization
  → Controllers (/api/*)
  → Fallback → index.html
```

## Global Exception Handling

`GlobalExceptionHandlerMiddleware` catches exceptions and returns JSON:

| Exception | HTTP Status |
|-----------|-------------|
| `NotFoundException` | 404 |
| `ValidationException` | 400 |
| Other | 500 |

## Validation

- **DTO level:** `[Required]`, `[StringLength]` on `Title`
- **EF level:** `IsRequired()`, `HasMaxLength(200)` in `OnModelCreating`
- **API level:** `[ApiController]` automatically returns `400` on invalid ModelState

## Design Decisions

| Decision | Reason |
|----------|--------|
| Repository Pattern | Separates controller from data access, easier to test |
| SQLite | Simple for development, no separate DB server needed |
| Static UI in wwwroot | No extra framework, same server for API and UI |
| EnsureCreated | Automatic DB creation without migrations |
