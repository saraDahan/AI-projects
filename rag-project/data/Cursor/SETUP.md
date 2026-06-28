# Setup and Running Instructions

## 1. Install .NET

Verify that .NET 8 is installed:

```powershell
dotnet --version
dotnet --list-runtimes
```

Look for a line containing `Microsoft.AspNetCore.App 8.x`.

## 2. Restore Packages

```powershell
cd TaskApi
dotnet restore
```

If you get a timeout:

```powershell
dotnet restore --disable-parallel
```

## 3. Build

```powershell
dotnet build
```

## 4. Run

### HTTP (recommended for development)

```powershell
dotnet run --launch-profile http
```

### HTTPS

```powershell
dotnet run --launch-profile https
```

On first run you may be prompted to trust the development certificate:

```powershell
dotnet dev-certs https --trust
```

## 5. Access the Application

| URL | Purpose |
|-----|---------|
| http://localhost:5262 | UI — user interface |
| http://localhost:5262/swagger | Swagger |
| http://localhost:5262/api/tasks | API — JSON |

Ports are configured in `Properties/launchSettings.json`.

## 6. Database

- Engine: **SQLite**
- File: `tasks.db` (auto-created in the project folder)
- Connection string: `appsettings.json` → `DefaultConnection`

```json
"ConnectionStrings": {
  "DefaultConnection": "Data Source=tasks.db"
}
```

On first run:
1. The `Tasks` table is created
2. 3 sample tasks are loaded (`SeedData`)

## 7. Stopping the Server

Press `Ctrl+C` in the terminal where `dotnet run` is running.

## 8. Running in Visual Studio / Cursor

1. Open the `TaskApi` folder
2. Run with F5 or `dotnet run`
3. The browser will open automatically on the user interface
