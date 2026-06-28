# API Documentation

Base URL: `http://localhost:5262`

All responses are in **JSON** format.

## TaskItem

```json
{
  "id": 1,
  "title": "Learn ASP.NET Core",
  "isCompleted": false
}
```

## Endpoints

### GET /api/tasks

Returns all tasks.

**Response:** `200 OK`

```json
[
  { "id": 1, "title": "Learn ASP.NET Core", "isCompleted": false },
  { "id": 2, "title": "Build a REST API", "isCompleted": false },
  { "id": 3, "title": "Write unit tests", "isCompleted": true }
]
```

---

### GET /api/tasks/{id}

Returns a task by ID.

**Response:** `200 OK` — single task

**Errors:** `404 Not Found`

```json
{
  "status": 404,
  "error": "Task with id 99 was not found.",
  "details": null
}
```

---

### POST /api/tasks

Creates a new task.

**Body:**

```json
{
  "title": "New task",
  "isCompleted": false
}
```

**Validation:**
- `title` — required, 1–200 characters

**Response:** `201 Created` + `Location: /api/tasks/{id}` header

**Errors:** `400 Bad Request` (validation)

---

### PUT /api/tasks/{id}

Updates an existing task.

**Body:**

```json
{
  "title": "Updated title",
  "isCompleted": true
}
```

**Response:** `200 OK`

**Errors:** `404 Not Found`, `400 Bad Request`

---

### DELETE /api/tasks/{id}

Deletes a task.

**Response:** `204 No Content`

**Errors:** `404 Not Found`

---

## curl Examples

```bash
# Get all tasks
curl http://localhost:5262/api/tasks

# Get a single task
curl http://localhost:5262/api/tasks/1

# Create
curl -X POST http://localhost:5262/api/tasks \
  -H "Content-Type: application/json" \
  -d "{\"title\":\"New task\",\"isCompleted\":false}"

# Update
curl -X PUT http://localhost:5262/api/tasks/1 \
  -H "Content-Type: application/json" \
  -d "{\"title\":\"Updated\",\"isCompleted\":true}"

# Delete
curl -X DELETE http://localhost:5262/api/tasks/1
```

## Swagger

Interactive documentation available at:

**http://localhost:5262/swagger**

## Error Handling

Unhandled errors pass through `GlobalExceptionHandlerMiddleware` and are returned as JSON:

```json
{
  "status": 404,
  "error": "Error message",
  "details": null
}
```

Validation errors from `[ApiController]` are automatically returned as `400` with field-level details.
