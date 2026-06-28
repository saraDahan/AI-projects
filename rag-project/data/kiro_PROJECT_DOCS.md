# Project Documentation — Task API

> A .NET 8 Web API for task management, with a built-in UI and Swagger support.

---

## Overview

| Detail | Value |
|--------|-------|
| Project Name | TaskApi |
| Platform | .NET 8 Web API |
| Language | C# |
| Database | SQLite (file: `tasks.db`) |
| ORM | Entity Framework Core 8.0 |
| API Docs | Swagger / OpenAPI |
| User Interface | HTML + CSS + JavaScript (built into the project) |
| Default URL | `http://localhost:5000` |

---

## Project Structure

```
TaskApi/
├── Controllers/
│   └── TasksController.cs              ← 5 CRUD endpoints
├── Data/
│   └── AppDbContext.cs                 ← EF Core DbContext + seed data
├── Middleware/
│   └── ExceptionHandlingMiddleware.cs  ← Global error handling
├── Models/
│   ├── TaskItem.cs                     ← Task entity
│   └── DTOs/
│       ├── CreateTaskDto.cs            ← Input model for POST
│       └── UpdateTaskDto.cs            ← Input model for PUT
├── Repositories/
│   ├── ITaskRepository.cs              ← Repository interface
│   └── TaskRepository.cs              ← Repository implementation
├── wwwroot/
│   ├── index.html                      ← Main UI page (RTL, Hebrew)
│   ├── style.css                       ← Styling
│   └── app.js                          ← UI logic (Fetch API)
├── appsettings.json                    ← Config + connection string
├── Program.cs                          ← Entry point, DI, Middleware
├── TaskApi.csproj                      ← Project settings and dependencies
└── tasks.db                            ← SQLite file (auto-created)
```

---

## Architecture

The project follows the **Repository Pattern** with **Dependency Injection**:

```
HTTP Request
     ↓
TasksController          ← Receives request, returns response
     ↓
ITaskRepository          ← Interface
     ↓
TaskRepository           ← Implementation, DB access
     ↓
AppDbContext             ← EF Core DbContext
     ↓
tasks.db (SQLite)        ← Database
```

---

## Data Model

### TaskItem (Entity)

```csharp
public class TaskItem
{
    public int Id { get; set; }

    [Required]
    [MaxLength(200)]
    public string Title { get; set; }

    public bool IsCompleted { get; set; }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `Id` | `int` | Primary key, auto-generated |
| `Title` | `string` | Task name, required, max 200 characters |
| `IsCompleted` | `bool` | Completion status, default `false` |

### DTOs

**CreateTaskDto** — POST request body:
```json
{
  "title": "Task name",
  "isCompleted": false
}
```

**UpdateTaskDto** — PUT request body:
```json
{
  "title": "Updated task name",
  "isCompleted": true
}
```

---

## API Endpoints

| Method | URL | Description | Success Code | Error Code |
|--------|-----|-------------|--------------|------------|
| `GET` | `/api/tasks` | Get all tasks | `200 OK` | — |
| `GET` | `/api/tasks/{id}` | Get task by ID | `200 OK` | `404 Not Found` |
| `POST` | `/api/tasks` | Create a new task | `201 Created` | `400 Bad Request` |
| `PUT` | `/api/tasks/{id}` | Update an existing task | `200 OK` | `400`, `404` |
| `DELETE` | `/api/tasks/{id}` | Delete a task | `204 No Content` | `404 Not Found` |

### Examples

**GET /api/tasks** — returns an array:
```json
[
  { "id": 1, "title": "Buy groceries",        "isCompleted": false },
  { "id": 2, "title": "Read a book",          "isCompleted": true  },
  { "id": 3, "title": "Complete the project", "isCompleted": false }
]
```

**POST /api/tasks**:
```json
// Request Body:
{ "title": "New task", "isCompleted": false }

// Response 201:
{ "id": 4, "title": "New task", "isCompleted": false }
```

**Validation error (400)**:
```json
{
  "title": ["Title is required."]
}
```

**Not Found error (404)**:
```json
{ "message": "Task with id 99 was not found." }
```

---

## Dependencies (NuGet Packages)

| Package | Version | Purpose |
|---------|---------|---------|
| `Microsoft.AspNetCore.OpenApi` | 8.0.26 | OpenAPI support |
| `Microsoft.EntityFrameworkCore.Sqlite` | 8.0.0 | EF Core with SQLite |
| `Swashbuckle.AspNetCore` | 6.6.2 | Swagger UI |

---

## Configuration (appsettings.json)

```json
{
  "ConnectionStrings": {
    "DefaultConnection": "Data Source=tasks.db"
  },
  "Logging": {
    "LogLevel": {
      "Default": "Information",
      "Microsoft.AspNetCore": "Warning"
    }
  },
  "AllowedHosts": "*"
}
```

---

## Running the Project

### Prerequisites
- [.NET 8 SDK](https://dotnet.microsoft.com/download/dotnet/8) or later

### Steps

```bash
# 1. Navigate to the project folder
cd TaskApi

# 2. Restore dependencies
dotnet restore

# 3. Run the project
dotnet run
```

### URLs after startup

| URL | Content |
|-----|---------|
| `http://localhost:5000` | User Interface (UI) |
| `http://localhost:5000/swagger` | Swagger documentation |
| `http://localhost:5000/api/tasks` | API directly |

> The terminal must stay open as long as you want the project running.

---

## Seed Data

On first run, 3 sample tasks are created automatically:

| ID | Title | IsCompleted |
|----|-------|-------------|
| 1 | Buy groceries | false |
| 2 | Read a book | true |
| 3 | Complete the project | false |

---

## User Interface (UI)

A visual interface built into the project, written in plain HTML/CSS/JavaScript.

### Features
- List of all tasks
- Add a new task (also works with Enter key)
- Toggle task completion status
- Delete a task (with confirmation dialog)
- Statistics counter (total / completed / pending)
- Filters: All / Pending / Completed
- Toast notifications for every action
- Client-side validation
- RTL layout with Hebrew support
- Mobile responsive design

### Files
| File | Purpose |
|------|---------|
| `wwwroot/index.html` | Page structure |
| `wwwroot/style.css` | Full styling |
| `wwwroot/app.js` | API communication via Fetch |

---

## Error Handling

`ExceptionHandlingMiddleware` catches all unhandled exceptions and returns a consistent JSON response:

```json
{
  "status": 500,
  "error": "InternalServerError",
  "message": "Error description"
}
```

| Exception Type | HTTP Code |
|----------------|-----------|
| `ArgumentException` | 400 Bad Request |
| `KeyNotFoundException` | 404 Not Found |
| Any other exception | 500 Internal Server Error |

---

## Technical Notes

- **EF Core** auto-creates the database on first run (`EnsureCreated`)
- **Repository Pattern** allows swapping the database in the future without changing the Controller
- **Async/Await** used in all DB operations to avoid blocking threads
- **AsNoTracking** on read queries for better performance
- **DTOs** decouple the API model from the database model
- **Validation** is applied both in DTOs (Data Annotations) and in JavaScript (client-side)
