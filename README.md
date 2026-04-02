# Chain Pharmacy Management System

A full-stack chain pharmacy management system based on `Vue 3`, `Django REST Framework`, and `openGauss`.

This repository is organized for both course delivery and team collaboration. It supports:
- local development with separate frontend and backend processes
- containerized deployment with `Docker Compose`
- SQL-based database initialization for reproducible openGauss setup

## Project Goals

The system is designed around three roles:
- `System Administrator`: manages pharmacy administrators, salespersons, stores, announcements, and dashboard-level operations
- `Pharmacy Administrator`: manages medicines, manufacturers, inventory, purchase orders, and salesperson shift schedules
- `Salesperson`: searches medicines, creates sales orders, updates logistics, and submits order reviews

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
- `gunicorn`

### Database
- `openGauss 5.0.1`
- `Docker`

## Architecture

```text
frontend (Vue 3 + nginx or Vite dev server)
  -> /api
backend (Django + DRF + gunicorn/runserver)
  -> openGauss
```

## Core Modules

- `accounts`: login, role-based access control, pharmacy admin management, salesperson management, shift scheduling
- `announcements`: announcement publishing and listing
- `medicine`: manufacturer, category, medicine CRUD, fuzzy search
- `inventory`: store management, inventory management, purchase orders
- `sales`: sales orders, order detail, logistics, order review
- `common`: dashboard overview aggregation
- `sql`: authoritative schema and demo data for openGauss

## Repository Layout

```text
backend/
  apps/
    accounts/
    announcements/
    common/
    inventory/
    medicine/
    sales/
  config/
  opengauss_backend/
  scripts/
  Dockerfile
  manage.py
  requirements.txt
frontend/
  src/
    api/
    layout/
    router/
    stores/
    views/
  Dockerfile
  nginx.conf
  package.json
  vite.config.js
sql/
  schema.sql
  init_data.sql
docker-compose.yml
README.md
```

## Team Collaboration Workflow

### Recommended Role Split

- Member A: database schema, seed data, SQL scripts, openGauss validation
- Member B: authentication, permissions, system administrator modules
- Member C: medicine, manufacturer, inventory, purchase order modules
- Member D: sales, logistics, review, frontend integration, documentation polishing

### Git Workflow

Recommended branch model:
- `main`: stable submission branch
- `feature/<module-name>`: development branch for one module
- `fix/<issue-name>`: targeted bug fix branch

Recommended process:
1. Pull the latest `main`
2. Create a feature branch
3. Complete one module or one bug fix only
4. Run backend/frontend checks locally
5. Merge back into `main` after verification

### Collaboration Rules

- Do not use Django migrations as the primary database initialization path for this project
- Treat `sql/schema.sql` as the authoritative schema file
- Treat `sql/init_data.sql` as the authoritative demo data file
- If you add a table or change schema, update SQL files before merging
- If you only change demo data in your local database, sync it back to `init_data.sql` before final submission
- Keep frontend API paths under `/api` so local development and Docker deployment stay aligned

## Database Initialization Strategy

The project uses SQL scripts as the authoritative initialization path.

Use these files in order:
1. [schema.sql](/d:/database/sql/schema.sql)
2. [init_data.sql](/d:/database/sql/init_data.sql)

Notes:
- `schema.sql` already contains the full current schema, including announcements, purchase orders, shift schedules, logistics, and reviews
- `init_data.sql` contains demo data exported from the current working database
- `sales_extension.sql` and `announcement_extension.sql` are retained only for compatibility reference and are no longer required for fresh initialization
- Do not rely on `python manage.py migrate` to create the project schema

## Docker Compose Deployment

This is the recommended team deployment setup. It starts:
- `db`: openGauss
- `backend`: Django API on `http://127.0.0.1:8000`
- `frontend`: nginx-served Vue app on `http://127.0.0.1:8080`

### 1. Prepare environment

```powershell
Copy-Item .env.example .env
```

Adjust if needed:
- `DB_PASSWORD`
- `SECRET_KEY`
- `INIT_DB_DEMO_DATA`

### 2. Start all services

```powershell
docker compose up --build
```

### 3. Access the system

- Frontend: `http://127.0.0.1:8080`
- Backend API: `http://127.0.0.1:8000/api`

### 4. Stop services

```powershell
docker compose down
```

Remove the database volume as well:

```powershell
docker compose down -v
```

### Docker Notes

- Backend startup automatically waits for openGauss
- Backend startup creates `pharmacy_system` if it does not exist
- On a fresh database, backend startup executes `sql/schema.sql`
- If `INIT_DB_DEMO_DATA=True`, backend startup also executes `sql/init_data.sql`

## Local Development

### Prerequisites

- Python `3.9`
- Node.js `20+`
- npm
- Docker with a running openGauss container, or another reachable openGauss instance

### Backend

```powershell
cd d:\database\backend
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python manage.py runserver
```

Backend address:
- `http://127.0.0.1:8000`

### Frontend

```powershell
cd d:\database\frontend
npm.cmd install
Copy-Item .env.example .env
npm.cmd run dev
```

Frontend address:
- `http://127.0.0.1:5173`

### Windows One-Click Startup

The project root already contains these scripts:
- [start_project.bat](/d:/database/start_project.bat): starts backend and frontend in separate windows
- [stop_project.bat](/d:/database/stop_project.bat): closes the spawned backend and frontend windows

Run from PowerShell in the project root:

```powershell
cd d:\database
.\start_project.bat
```

Stop them with:

```powershell
cd d:\database
.\stop_project.bat
```

Local Vite development proxies `/api` to `http://127.0.0.1:8000`, so local development and Docker deployment use the same API path design.

## Manual Database Setup

If you initialize openGauss manually through Navicat or another SQL client:

1. Create or open the `pharmacy_system` database
2. Execute [schema.sql](/d:/database/sql/schema.sql)
3. Execute [init_data.sql](/d:/database/sql/init_data.sql)

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

Seed additional demo data into the current database:

```powershell
cd d:\database\backend
python scripts\seed_demo_data.py
```

## Delivery Checklist

Before submission, verify:
- source code is complete
- `sql/schema.sql` and `sql/init_data.sql` match the current project state
- frontend and backend both run successfully
- three roles can log in and use their corresponding modules
- English development manual is updated
- demo video and final compressed submission package are prepared

## Operational Notes

- The custom backend in `backend/opengauss_backend/` keeps Django compatible with openGauss
- Role restrictions are enforced in both frontend routes and backend APIs
- The current Docker deployment files are complete, but actual image build still depends on external access to Docker Hub
- For a clean Docker redeploy, remove the compose volume with `docker compose down -v`
