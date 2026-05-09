# Submission Checklist

## 1. Folder Naming

Use the following naming format when submitting:

```text
YourName+ChainPharmacySystem
```

If this is a group submission, use the format required by the instructor. Keep the project root clean and make sure reviewers can run it directly after extraction.

## 2. Required Files

| Item | Required | Notes |
|---|---|---|
| `backend/` | Yes | Django backend source code |
| `frontend/` | Yes | Vue frontend source code |
| `sql/schema.sql` | Yes | Authoritative database schema |
| `sql/init_data.sql` | Yes | Demo data for reproduction |
| `docker-compose.yml` | Yes | One-command reproduction |
| `.env.example` | Yes | Root Docker environment template |
| `backend/.env.example` | Yes | Backend local development environment template |
| `frontend/.env.example` | Yes | Frontend environment template |
| `README.md` | Yes | Main project guide and E-R diagrams |
| `docs/Development_Manual.md` | Yes | Development and design manual |
| `docs/Run_Guide.md` | Yes | Running and troubleshooting guide |
| `docs/Submission_Checklist.md` | Yes | This checklist |
| Demo video | Usually yes | Keep within the instructor's time limit |

Do not submit:

- `.env`
- `backend/.env`
- `frontend/.env`
- database volume files
- `node_modules/`
- Python virtual environment folders
- temporary logs or screenshots not required by the instructor

## 3. Documentation Check

Before submission, confirm the documents describe the current system accurately:

- README project name is **Chain Pharmacy System** and matches the Chinese title used in the application.
- E-R diagrams are organized by three roles:
  - System administrator
  - Pharmacy administrator
  - Salesperson
- E-R diagrams include `purchase_order_item` and `sale_order_item`.
- Purchase order amount is described as calculated from medicine purchase price and quantity.
- Sales order amount is described as calculated from medicine retail price and quantity.
- Store code, medicine code, purchase order number, and sales order number are described as system-generated.
- Sales order customer name and customer phone are described as required fields.
- The documents keep sales records within the chain pharmacy business scope.
- The documents do not treat Django migrations as the main database initialization method.

## 4. Database Check

Use `sql/schema.sql` and `sql/init_data.sql` as the final submitted database source.

Confirm:

- `purchase_order_item` exists.
- `sale_order_item` exists.
- `v_medicine_stock` exists.
- `fn_set_updated_at` trigger function exists.
- `fn_log_sale_item` trigger function exists.
- Demo users exist:
  - `sysadmin`
  - `storeadmin`
  - `sales01`
- Demo data covers:
  - Stores
  - Users
  - Manufacturers
  - Medicine categories
  - Medicines
  - Inventory
  - Purchase orders and purchase order items
  - Sales orders and sales order items
  - Shift schedules
  - Announcements

## 5. Functional Check

### 5.1 System Administrator

Login:

```text
sysadmin / Admin@123
```

Verify:

- Dashboard opens.
- Store management works.
- Store code is generated automatically when adding a store.
- Pharmacy administrator management works.
- Salesperson management works.
- Announcement management works.
- Revenue comparison page loads data and can export CSV.

### 5.2 Pharmacy Administrator

Login:

```text
storeadmin / Admin@123
```

Verify:

- Manufacturer management works.
- Manufacturer contact person and contact phone are required.
- Medicine category management works.
- Medicine management works.
- Medicine code is generated automatically when adding a medicine.
- Inventory management works.
- Purchase order management works.
- Purchase order number is generated automatically.
- Purchase order amount is calculated from purchase details.
- Shift schedule uses weekday selection.

### 5.3 Salesperson

Login:

```text
sales01 / Admin@123
```

Verify:

- Sellable medicine list loads.
- Customer name is required before submitting a sales order.
- Customer phone is required before submitting a sales order.
- Sales order number is generated automatically.
- Sales order total is calculated from order items.
- Inventory is deducted after a successful sale.
- Sales records and order detail can be viewed.

## 6. Command Verification

Run these before submission when possible.

Backend:

```powershell
cd backend
python manage.py check
```

Frontend:

```powershell
cd frontend
npm.cmd run build
```

Smoke check:

```powershell
cd backend
python scripts\smoke_check.py
```

If a command cannot be run due to environment limitations, write down the reason in the final submission notes.

## 7. Demo Video Suggested Sequence

Keep the demo focused and avoid spending time on implementation details.

1. Briefly introduce the project: three roles and core business scope.
2. Show database schema in Navicat or another database tool.
3. Show role-based E-R diagrams in README or Development Manual.
4. Login as system administrator:
   - Manage stores.
   - Show system-generated store code.
   - Manage pharmacy administrators and salespersons.
5. Login as pharmacy administrator:
   - Manage manufacturers and medicines.
   - Show system-generated medicine code.
   - Create a purchase order.
   - Show purchase amount calculated from purchase details.
   - Show inventory and shift schedule.
6. Login as salesperson:
   - Add medicines to a sales order.
   - Show required customer name and phone validation.
   - Submit the order.
   - Show inventory deduction and sales record detail.
7. Show dashboard or revenue comparison page.

## 8. Final Packaging Check

Before compressing:

- Remove local `.env` files.
- Remove `node_modules/`.
- Remove Python virtual environment folders.
- Confirm README opens normally.
- Confirm Mermaid diagrams are readable in Markdown preview.
- Confirm demo accounts are written in README and Run Guide.
- Confirm the project can be started from a clean environment using the documented steps.
