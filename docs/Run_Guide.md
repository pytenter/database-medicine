# Run Guide

## 1. Overview

This guide explains how to run the Chain Pharmacy System locally for demonstration, development, and verification.

Recommended options:

| Mode | Best for | Frontend URL |
|---|---|---|
| Docker Compose | Fast reproduction and final demo | `http://127.0.0.1:8080` |
| Local development | Code modification and debugging | `http://127.0.0.1:5173` |
| Windows scripts | Quick local start after dependencies are ready | `http://127.0.0.1:5173` |

The project uses `sql/schema.sql` and `sql/init_data.sql` as the authoritative database initialization files.

## 2. Demo Accounts

| Username | Password | Role |
|---|---|---|
| `sysadmin` | `Admin@123` | System administrator |
| `storeadmin` | `Admin@123` | Pharmacy administrator |
| `sales01` | `Admin@123` | Salesperson |

## 3. Docker Compose Mode

Use this mode when you want the fastest and most stable way to reproduce the project.

### 3.1 Requirements

- Git
- Docker Desktop or another Docker environment
- Available ports: `5432`, `8000`, `8080`

### 3.2 Prepare Environment Variables

From the project root:

```powershell
Copy-Item .env.example .env
```

Check these key values in `.env`:

```env
DB_NAME=pharmacy_system
DB_USER=gaussdb
DB_PASSWORD=your-password
DB_PORT=5432
INIT_DB_DEMO_DATA=True
```

### 3.3 Start Services

```powershell
docker compose up -d --build
```

The startup process will:

1. Start openGauss.
2. Start the Django backend.
3. Create the target database if needed.
4. Initialize schema and demo data when the database is empty.
5. Start the nginx frontend container.

### 3.4 Check Status

```powershell
docker compose ps
docker logs pharmacy-opengauss --tail 100
docker logs pharmacy-backend --tail 100
docker logs pharmacy-frontend --tail 100
```

### 3.5 Access

- Frontend: `http://127.0.0.1:8080`
- Backend: `http://127.0.0.1:8000`
- API prefix: `http://127.0.0.1:8000/api`

### 3.6 Stop Services

```powershell
docker compose down
```

To remove the database volume and initialize from scratch:

```powershell
docker compose down -v
docker compose up -d --build
```

## 4. Local Development Mode

Use this mode when you need Vite hot reload or backend debugging.

### 4.1 Start Database Only

```powershell
Copy-Item .env.example .env
docker compose up -d db
```

Database connection:

| Item | Value |
|---|---|
| Host | `127.0.0.1` |
| Port | `5432` |
| Database | `pharmacy_system` |
| User | `gaussdb` |
| Password | value of `DB_PASSWORD` in `.env` |

### 4.2 Configure Backend

```powershell
Copy-Item backend\.env.example backend\.env
```

Check `backend/.env`:

```env
DEBUG=True
DB_NAME=pharmacy_system
DB_USER=gaussdb
DB_PASSWORD=your-password
DB_HOST=127.0.0.1
DB_PORT=5432
INIT_DB_DEMO_DATA=True
```

`DB_PASSWORD` must match the root `.env`.

### 4.3 Initialize Database

```powershell
cd backend
python -m pip install -r requirements.txt
python scripts\init_compose_db.py
```

Do not use `python manage.py makemigrations` and `python manage.py migrate` as the main initialization method for this project. The submitted database structure is maintained in:

- `sql/schema.sql`
- `sql/init_data.sql`

### 4.4 Start Backend

```powershell
cd backend
python manage.py check
python manage.py runserver
```

Backend URL:

- `http://127.0.0.1:8000`

### 4.5 Start Frontend

Open another terminal:

```powershell
cd frontend
Copy-Item .env.example .env
npm.cmd install
npm.cmd run dev
```

Frontend URL:

- `http://127.0.0.1:5173`

Vite proxies `/api` requests to `http://127.0.0.1:8000`.

## 5. Windows Script Mode

The project root provides:

```powershell
.\start_project.bat
.\stop_project.bat
```

Use this mode only after these prerequisites are ready:

- Local openGauss is running on `127.0.0.1:5432`.
- `backend/.env` is configured.
- Backend dependencies are installed.
- Frontend dependencies are installed.
- Database has been initialized by `python scripts\init_compose_db.py`.

## 6. Smoke Check

After backend and database are running:

```powershell
cd backend
python scripts\smoke_check.py
```

The smoke check verifies:

- Login API.
- Current user API.
- User list API.
- Medicine fuzzy search.
- Inventory query.
- Sales order creation.
- Inventory deduction.
- Test order cleanup.

## 7. Manual Verification

Verify these workflows before demonstration:

1. Login as `sysadmin`, `storeadmin`, and `sales01`.
2. System administrator can manage stores, pharmacy administrators, salespersons, and announcements.
3. Store code is generated automatically when adding a store.
4. Pharmacy administrator can add manufacturers, categories, medicines, inventory, purchase orders, and schedules.
5. Medicine code is generated automatically when adding a medicine.
6. Purchase order number is generated automatically.
7. Purchase amount is calculated from purchase order items.
8. Salesperson must fill customer name and phone before creating a sales order.
9. Sales order number is generated automatically.
10. Sales order creation deducts inventory correctly.
11. Sales records show order details correctly.
12. Dashboard and revenue comparison pages load charts and data.

## 8. Common Problems

### 8.1 Docker image pull fails

Use an available mirror, then tag the image back to the original name:

```bash
docker pull docker.1ms.run/enmotech/opengauss:5.0.1
docker tag docker.1ms.run/enmotech/opengauss:5.0.1 enmotech/opengauss:5.0.1

docker pull docker.1ms.run/library/python:3.9-slim
docker tag docker.1ms.run/library/python:3.9-slim python:3.9-slim

docker pull docker.1ms.run/library/node:20-alpine
docker tag docker.1ms.run/library/node:20-alpine node:20-alpine

docker pull docker.1ms.run/library/nginx:1.27-alpine
docker tag docker.1ms.run/library/nginx:1.27-alpine nginx:1.27-alpine
```

Then run:

```bash
docker compose up -d --build --pull never
```

### 8.2 Frontend opens but has no data

Check:

- `sql/schema.sql` has been executed.
- `sql/init_data.sql` has been executed.
- `INIT_DB_DEMO_DATA=True`.
- Backend is running.
- Frontend `/api` proxy points to the backend.

### 8.3 Backend cannot connect to database

Check:

- openGauss container is running.
- `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, and `DB_PASSWORD` are correct.
- Root `.env` and `backend/.env` use the same password.

