# Chain Pharmacy Management System

A complete database course-design project for a chain pharmacy management system based on Vue 3, Django REST Framework, and openGauss.

## Tech Stack

- Frontend: Vue 3, Vite, Vue Router, Pinia, Axios, Element Plus
- Backend: Django 4.2, Django REST Framework, JWT authentication
- Database: openGauss running in Docker
- Tooling: Navicat for database inspection and SQL execution

## Core Roles

- System administrator: manage pharmacy administrators and salespersons
- Pharmacy administrator: manage medicines, categories, manufacturers, and inventory
- Salesperson: search medicines and create sales orders

## Project Structure

```text
backend/
  apps/
  config/
  opengauss_backend/
frontend/
  src/
sql/
docs/
start_project.bat
stop_project.bat
```

## Main Features

- Role-based login with JWT
- User management
- Medicine, category, and manufacturer management
- Inventory management with low-stock warning
- Fuzzy search by medicine name, manufacturer, and code
- Sales order creation with transaction-based stock deduction
- Sales record query
- openGauss schema, indexes, view, and triggers

## Database Connection

Current verified local connection:

- Host: `127.0.0.1`
- Port: `5432`
- User: `gaussdb`
- Database: `pharmacy_system`

A small Django backend shim is included in `backend/opengauss_backend/` to bypass PostgreSQL version validation for openGauss.

## Terminal Startup Steps

### 1. Start the openGauss container

Open PowerShell and run:

```powershell
docker start opengauss
```

If the container is already running, Docker will tell you directly.

### 2. Start the backend manually

Open a new PowerShell window and run:

```powershell
cd d:\database\backend
python manage.py runserver
```

Backend address:

```text
http://127.0.0.1:8000/
```

### 3. Start the frontend manually

Open another PowerShell window and run:

```powershell
cd d:\database\frontend
npm.cmd run dev
```

Frontend address:

```text
http://127.0.0.1:5173/
```

### 4. One-command startup from terminal

If you are already in the project root directory `d:\database`, you can run:

```powershell
.\start_project.bat
```

To stop the backend and frontend windows created by the script:

```powershell
.\stop_project.bat
```

## Setup

### 1. Database initialization

Execute the following files in Navicat or another SQL client in order:

1. `sql/schema.sql`
2. `sql/init_data.sql`

### 2. Backend dependencies

```powershell
cd d:\database\backend
python -m pip install -r requirements.txt
```

### 3. Frontend dependencies

```powershell
cd d:\database\frontend
npm.cmd install
```

## Demo Accounts

- `sysadmin / Admin@123`
- `storeadmin / Admin@123`
- `sales01 / Admin@123`

## Verification

Verified locally:

- Django project check passes
- Vue production build passes
- Login works for all three demo accounts
- Live smoke script works for login, query, inventory, and sales creation

## Smoke Check

```powershell
cd d:\database\backend
python scripts\smoke_check.py
```

## Documentation

- `docs/Development_Manual.md`
- `docs/Run_Guide.md`
- `docs/Submission_Checklist.md`
