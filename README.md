# Chain Pharmacy Management System

A full-stack chain pharmacy management system built with `Vue 3`, `Django REST Framework`, and `openGauss`.

This project follows a frontend-backend separation architecture and covers user management, medicine management, inventory control, sales order processing, logistics tracking, and order review workflows.

## Highlights

- Role-based access control for `System Administrator`, `Pharmacy Administrator`, and `Salesperson`
- Medicine, manufacturer, category, store, and inventory management
- Fuzzy search by medicine name, manufacturer, and code
- Sales order creation with transactional stock deduction
- Order detail, logistics update, and order review pages
- openGauss schema with indexes, views, triggers, and seed data
- Windows one-click startup scripts for local demonstration

## Tech Stack

### Frontend

- `Vue 3`
- `Vite`
- `Vue Router`
- `Pinia`
- `Axios`
- `Element Plus`

### Backend

- `Python 3.9`
- `Django 4.2`
- `Django REST Framework`
- `Simple JWT`
- `psycopg2`

### Database

- `openGauss 5.x`
- `Docker`

## Architecture

```text
Frontend (Vue 3 + Vite)
  -> REST API (Django + DRF)
  -> openGauss Database
```

## Core Modules

- `accounts`: login, current user, role-based permission control, user CRUD
- `medicine`: manufacturer, category, medicine CRUD, fuzzy search
- `inventory`: store management, inventory management, stock warning
- `sales`: sales order creation, order detail, logistics, review
- `sql`: database schema, seed data, and sales extension script

## Project Structure

```text
.
├─ backend/
│  ├─ apps/
│  │  ├─ accounts/
│  │  ├─ common/
│  │  ├─ inventory/
│  │  ├─ medicine/
│  │  └─ sales/
│  ├─ config/
│  ├─ opengauss_backend/
│  ├─ scripts/
│  ├─ manage.py
│  └─ requirements.txt
├─ frontend/
│  ├─ src/
│  │  ├─ api/
│  │  ├─ layout/
│  │  ├─ router/
│  │  ├─ stores/
│  │  └─ views/
│  ├─ package.json
│  └─ vite.config.js
├─ sql/
│  ├─ schema.sql
│  ├─ init_data.sql
│  └─ sales_extension.sql
├─ docs/
├─ start_project.bat
└─ stop_project.bat
```

## Local Setup

### 1. Start openGauss

```powershell
docker start opengauss
```

### 2. Initialize the database

Use Navicat or another SQL client and execute these scripts in the `pharmacy_system` database:

```text
sql/schema.sql
sql/init_data.sql
sql/sales_extension.sql
```

### 3. Install backend dependencies

```powershell
cd d:\database\backend
python -m pip install -r requirements.txt
```

### 4. Install frontend dependencies

```powershell
cd d:\database\frontend
npm.cmd install
```

## Run Locally

### Option A: Start manually

Backend:

```powershell
cd d:\database\backend
python manage.py runserver
```

Frontend:

```powershell
cd d:\database\frontend
npm.cmd run dev
```

Default local addresses:

- Frontend: `http://127.0.0.1:5173/`
- Backend: `http://127.0.0.1:8000/`

### Option B: One-click startup

From the project root:

```powershell
.\start_project.bat
```

Stop the spawned frontend and backend windows:

```powershell
.\stop_project.bat
```

## Demo Accounts

- `sysadmin / Admin@123`
- `storeadmin / Admin@123`
- `sales01 / Admin@123`

## Verification

Backend check:

```powershell
cd d:\database\backend
python manage.py check
```

Frontend build:

```powershell
cd d:\database\frontend
npm.cmd run build
```

Smoke test:

```powershell
cd d:\database\backend
python scripts\smoke_check.py
```

## Notes

- The project uses SQL scripts as the primary database initialization path for openGauss.
- Django migration warnings may still appear during development; for this project, the authoritative schema comes from the SQL files in `sql/`.
- The custom backend in `backend/opengauss_backend/` is used to keep Django compatible with openGauss.

## Documentation

- `docs/Development_Manual.md`
- `docs/Run_Guide.md`
- `docs/Submission_Checklist.md`

