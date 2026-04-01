# Run Guide

## 0. Quick Start

Double-click start_project.bat to open the backend and frontend windows automatically.

Use stop_project.bat to close them.

## 1. Database

1. Make sure the openGauss Docker container is running.
2. Create a database named `pharmacy_system`.
3. Execute `sql/schema.sql` first.
4. Execute `sql/init_data.sql` second.
5. Confirm the seeded data in Navicat.

## 2. Backend

```powershell
cd backend
copy .env.example .env
python -m pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

If `makemigrations` and `migrate` are not needed because you initialize the database directly by SQL, keep the model definitions consistent with the SQL schema.

## 3. Frontend

```powershell
cd frontend
copy .env.example .env
npm.cmd install
npm.cmd run dev
```

## 4. Access

- Frontend: `http://127.0.0.1:5173`
- Backend API: `http://127.0.0.1:8000/api`

## 5. Demo Accounts

- `sysadmin / Admin@123`
- `storeadmin / Admin@123`
- `sales01 / Admin@123`

## 6. Smoke Check

`powershell
cd backend
python scripts\\smoke_check.py
` 


