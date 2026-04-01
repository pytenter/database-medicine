# Chain Pharmacy Management System

A full-stack database application for managing a chain pharmacy business, built with `Vue 3`, `Django REST Framework`, and `openGauss`.

This project was designed as a database course-design system and focuses on role-based access control, medicine and inventory management, fuzzy search, sales processing, and openGauss-oriented database design.

## Overview

The system serves three user roles:

- `System Administrator`: manages pharmacy administrators and sales staff.
- `Pharmacy Administrator`: manages medicines, manufacturers, categories, stores, and inventory.
- `Salesperson`: searches medicines and creates sales orders.

The application follows a frontend-backend separation architecture:

- Frontend: SPA built with Vue 3 and Vite
- Backend: REST API built with Django REST Framework
- Database: openGauss running in Docker

## Key Features

- JWT-based authentication and role-based authorization
- User management for pharmacy administrators and salespersons
- Medicine, manufacturer, and category management
- Inventory management with low-stock warning support
- Fuzzy search by medicine name, code, and manufacturer
- Sales order creation with transaction-based stock deduction
- Sales record query and detail view
- openGauss schema with indexes, view, trigger, and seed data
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

### Database and Tools

- `openGauss 5.0.1`
- `Docker`
- `Navicat`

## Architecture

```text
┌────────────────────────────────────────────────────────────┐
│                        Vue 3 Frontend                      │
│   Login / Dashboard / Users / Medicines / Inventory       │
│   Sales Create / Sales Records                            │
└─────────────────────────────┬──────────────────────────────┘
                              │ HTTP / JSON
                              ▼
┌────────────────────────────────────────────────────────────┐
│                  Django REST Backend                       │
│   accounts / medicine / inventory / sales / common        │
│   JWT auth / permissions / serializers / transactions     │
└─────────────────────────────┬──────────────────────────────┘
                              │ SQL
                              ▼
┌────────────────────────────────────────────────────────────┐
│                     openGauss Database                     │
│   sys_user / store / medicine / inventory / sale_order    │
│   indexes / view / triggers / seed data                   │
└────────────────────────────────────────────────────────────┘
```

## Repository Structure

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
│  └─ init_data.sql
├─ docs/
│  ├─ Development_Manual.md
│  ├─ Run_Guide.md
│  └─ Submission_Checklist.md
├─ start_project.bat
└─ stop_project.bat
```

## Backend Modules

### `accounts`

Responsible for:

- login
- current-user query
- role management
- user CRUD
- reset password

### `medicine`

Responsible for:

- manufacturer management
- category management
- medicine CRUD
- fuzzy medicine search

### `inventory`

Responsible for:

- store management
- inventory CRUD
- low-stock status
- store-scope restrictions for pharmacy administrators

### `sales`

Responsible for:

- sale order creation
- inventory deduction
- sale record query
- sale detail retrieval

### `common`

Provides shared abstract models such as timestamp fields.

## Database Design

Core business tables:

- `sys_user`
- `store`
- `manufacturer`
- `medicine_category`
- `medicine`
- `inventory`
- `sale_order`
- `sale_order_item`
- `operation_log`

Database objects included in `sql/schema.sql`:

- primary keys and foreign keys
- unique constraints
- check constraints
- indexes for query optimization
- view: `v_medicine_stock`
- trigger functions for `updated_at`
- operation logging trigger for sale items

## openGauss Compatibility Note

Django's built-in PostgreSQL backend performs PostgreSQL version checks and introspection logic that are not fully compatible with openGauss 5.0.1.

To solve this, this project includes a lightweight compatibility backend in:

- `backend/opengauss_backend/base.py`
- `backend/opengauss_backend/introspection.py`

This is why the Django database engine in the project is configured as `opengauss_backend` instead of the default PostgreSQL backend.

## Environment

Verified local environment:

- OS: Windows
- Python interpreter: `C:\ProgramData\Miniconda3\python.exe`
- Node.js: `v24.x`
- Database host: `127.0.0.1:5432`
- Database name: `pharmacy_system`
- Database user: `gaussdb`

## Installation

### 1. Start openGauss

```powershell
docker start opengauss
```

### 2. Initialize database

Execute the following SQL files in order in `pharmacy_system`:

1. `sql/schema.sql`
2. `sql/init_data.sql`

You can run them with Navicat or another SQL client.

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

## Local Development

### Option A: Manual startup

Start backend:

```powershell
cd d:\database\backend
python manage.py runserver
```

Start frontend in another terminal:

```powershell
cd d:\database\frontend
npm.cmd run dev
```

Access URLs:

- Frontend: `http://127.0.0.1:5173/`
- Backend: `http://127.0.0.1:8000/`

### Option B: One-click startup

From the project root:

```powershell
.\start_project.bat
```

Stop the opened backend and frontend windows:

```powershell
.\stop_project.bat
```

## Deployment Notes

This repository is designed primarily for course-design development and demonstration.

In the current local setup:

- openGauss runs in Docker
- Django runs as a local development server
- Vue runs through the Vite development server

For a more production-like deployment, the following structure is recommended:

- build the frontend with `npm run build`
- serve frontend static assets via Nginx or Django static hosting
- run Django with Gunicorn/uWSGI equivalent or another production server
- place openGauss behind controlled network access

## Demo Accounts

- `sysadmin / Admin@123`
- `storeadmin / Admin@123`
- `sales01 / Admin@123`

## Verification

The following checks have been verified:

- Django configuration check passes
- frontend production build passes
- demo users can log in successfully
- medicine and inventory queries work
- sale creation works and deducts stock correctly
- live smoke check script runs and cleans test data automatically

Run smoke check:

```powershell
cd d:\database\backend
python scripts\smoke_check.py
```

## Important Notes

### About Django migrations

This project initializes the business schema through SQL scripts rather than relying on Django migrations for the openGauss database.

Because of openGauss compatibility differences, you may still see Django migration warnings during local development. For this project, the authoritative database initialization path is:

- `sql/schema.sql`
- `sql/init_data.sql`

Do not treat the migration warning as a failure of the running system if the SQL schema has already been loaded.

### About Navicat visibility

If you cannot see the project tables in Navicat, make sure you are connected to:

- database: `pharmacy_system`
- schema: `public`

The business tables are stored under `public`, not under `postgres` or `omm`.

## Documentation

Additional project documents:

- `docs/Development_Manual.md`
- `docs/Run_Guide.md`
- `docs/Submission_Checklist.md`

## Suggested Demonstration Flow

1. Start openGauss and run the system.
2. Log in as `sysadmin` and show user management.
3. Log in as `storeadmin` and show medicine and inventory management.
4. Log in as `sales01` and show medicine search and sale creation.
5. Open sales records and explain database updates.
6. Show the relevant tables in Navicat.

## License

This project is intended for academic course-design use.

