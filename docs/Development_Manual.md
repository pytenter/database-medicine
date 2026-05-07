# Database Application System Development Manual

## 1. Project Overview

- **Project name:** Chain Pharmacy Management System
- **Project type:** Database application system course design
- **Core database:** Huawei openGauss
- **System architecture:** Browser + Vue frontend + Django REST backend + openGauss database
- **Recommended deployment:** Docker Compose

The project builds a complete management system for a chain pharmacy company. It covers daily business operations such as employee account management, pharmacy store management, medicine maintenance, inventory control, sales order creation, logistics tracking, order review, announcements, and business dashboard analysis.

The system is designed around three user roles:

- **System administrator:** manages stores, pharmacy administrators, salespersons, announcements, and chain-level business analysis.
- **Pharmacy administrator:** manages medicine data, manufacturers, inventory, purchase orders, and salesperson shift schedules for their own store.
- **Salesperson:** searches medicines, creates sales orders, tracks logistics, submits order reviews, and views authorized order records.

## 2. Project Planning

### 2.1 Objectives

The project aims to demonstrate the complete lifecycle of a database application:

- Analyze real business requirements for a chain pharmacy scenario.
- Design a relational database with entities, relationships, constraints, indexes, views, and triggers.
- Implement role-based permission control at both frontend and backend levels.
- Provide user-friendly CRUD pages for daily maintenance operations.
- Support fuzzy search by medicine name, manufacturer, code, order number, customer, phone number, and other key fields.
- Implement transaction-safe sales order creation and inventory deduction.
- Provide visual dashboards for supervisors to understand sales, stock risk, order status, and store revenue.
- Package the system with Docker Compose so reviewers can reproduce it quickly.

### 2.2 Schedule

| Stage | Main work | Deliverables |
|---|---|---|
| Week 1 | Topic selection and requirement analysis | Requirement list, role list, business scope |
| Week 2 | Conceptual database design | Entity list, E-R relationship design |
| Week 3 | Logical and physical database design | Tables, keys, constraints, indexes |
| Week 4 | Backend API implementation | Django apps, serializers, permissions, REST APIs |
| Week 5 | Frontend implementation | Vue pages, route guards, management tables, forms |
| Week 6 | Testing, documentation, deployment | SQL files, Docker guide, demo accounts, manual, video |

## 3. Requirement Analysis

### 3.1 User Roles and Permissions

| Role | Main permissions | Business scope |
|---|---|---|
| System administrator | Manage stores, pharmacy administrators, salespersons, announcements, chain dashboard | All stores |
| Pharmacy administrator | Manage medicines, manufacturers, inventory, purchase orders, shift schedules | Own store |
| Salesperson | Search medicines, create sales orders, view orders, update logistics, submit reviews | Own store |

### 3.2 Functional Requirements

| Requirement | Implementation |
|---|---|
| Login and identity recognition | JWT login API and frontend route guard |
| User management | Add, edit, deactivate, search, and reset password |
| Store management | Add, edit, delete, search, and view store details |
| Medicine management | Add, edit, soft delete, search by code/name/manufacturer |
| Manufacturer management | Add, edit, soft delete, fuzzy search |
| Inventory management | Add, edit, soft delete, warning threshold, low-stock filtering |
| Purchase order management | Add, edit, delete, status management |
| Sales order creation | Cart-style order creation, stock validation, transaction-safe inventory deduction |
| Sales record query | Search by order number/customer/phone, status filtering, date filtering, detail view |
| Logistics and review | Order logistics update and customer review submission |
| Announcement management | Published announcements shown on dashboard |
| Visualization | Income trend, order trend, category ratio, hot medicines, order status, store revenue ranking |
| Export | CSV export for inventory, sales records, and store revenue comparison |

### 3.3 Non-Functional Requirements

- **Reproducibility:** Docker Compose starts database, backend, and frontend with one command.
- **Data integrity:** openGauss constraints and backend validation prevent invalid data.
- **Security:** APIs require JWT authentication and role-based permissions.
- **Usability:** the interface provides search, filters, pagination, warning tags, dialogs, and export buttons.
- **Maintainability:** backend is split into apps, frontend is split into views and API modules, SQL files are stored separately.

## 4. System Architecture

```mermaid
flowchart LR
    U[User Browser] --> F[Vue 3 Frontend]
    F -->|Axios HTTP /api| B[Django REST Framework Backend]
    B -->|SQL| D[(openGauss Database)]
    D --> V[v_medicine_stock View]
    D --> T[Triggers and Constraints]
```

The frontend is responsible for page rendering, route-level permission display, forms, tables, dashboards, and user interaction. The backend is responsible for authentication, API permission checking, validation, transaction processing, and data aggregation. openGauss stores business data and enforces relational integrity.

## 5. Technology Stack

### 5.1 Frontend

- Vue 3
- Vite
- Vue Router
- Pinia
- Axios
- Element Plus

### 5.2 Backend

- Python 3.9
- Django 4.2
- Django REST Framework
- Simple JWT
- gunicorn

### 5.3 Database and Deployment

- openGauss 5.0.1
- SQL scripts for schema and initial data
- Docker Compose
- nginx for serving the production frontend container

## 6. Database Design

### 6.1 Main Entities

| Entity | Table | Description |
|---|---|---|
| Store | `store` | Chain pharmacy store information |
| User | `sys_user` | System users and role information |
| Announcement | `announcement` | Published system announcements |
| Manufacturer | `manufacturer` | Medicine manufacturer information |
| MedicineCategory | `medicine_category` | Medicine classification |
| Medicine | `medicine` | Medicine master data |
| Inventory | `inventory` | Store-level stock quantity and warning threshold |
| PurchaseOrder | `purchase_order` | Store purchasing records |
| ShiftSchedule | `shift_schedule` | Salesperson shift schedule |
| SaleOrder | `sale_order` | Sales order header |
| SaleOrderItem | `sale_order_item` | Sales order item details |
| OrderLogistics | `order_logistics` | Order logistics records |
| OrderReview | `order_review` | Customer order review |
| OperationLog | `operation_log` | Database-triggered operation records |

### 6.2.1 Role-Based E-R Diagrams

The role-based E-R diagrams are split by permission scope. This keeps each diagram readable in Markdown preview and avoids very small nodes caused by putting every table into one large graph.

#### 6.2.1.1 Permission Overview

```mermaid
flowchart LR
    SYS_ADMIN["System Administrator<br/>sys_user.id PK<br/>role = system_admin"]
    STORE_ADMIN["Pharmacy Administrator<br/>sys_user.id PK<br/>role = pharmacy_admin<br/>store_id FK"]
    STAFF["Salesperson<br/>sys_user.id PK<br/>role = salesperson<br/>store_id FK"]
    STORE["Store<br/>store.id PK"]

    SYS_ADMIN ==>|"Manages stores, admins, staff, announcements"| STORE
    STORE ==>|"store_id FK ownership"| STORE_ADMIN
    STORE ==>|"store_id FK ownership"| STAFF
    STORE_ADMIN ==>|"Maintains medicines, stock, purchases, shifts"| STORE
    STAFF ==>|"Creates sales, logistics, reviews"| STORE

    classDef role fill:#FFE8CC,stroke:#D9480F,stroke-width:3px,color:#3B1D00
    classDef store fill:#E7F5FF,stroke:#1971C2,stroke-width:2px,color:#102A43
    class SYS_ADMIN,STORE_ADMIN,STAFF role
    class STORE store
```

#### 6.2.1.2 System Administrator E-R Diagram

```mermaid
flowchart LR
    SYS_ADMIN["System Administrator<br/>sys_user.id PK<br/>role = system_admin"]

    subgraph ADMIN_DATA["Data Managed by System Administrator"]
        STORE["Store<br/>store.id PK<br/>code, name UNIQUE"]
        ADMIN_USER["Pharmacy Admin Account<br/>sys_user.id PK<br/>role = pharmacy_admin<br/>store_id FK"]
        STAFF_USER["Salesperson Account<br/>sys_user.id PK<br/>role = salesperson<br/>store_id FK"]
        ANN["Announcement<br/>announcement.id PK<br/>created_by_id FK"]
    end

    SYS_ADMIN ==>|"Creates / manages"| STORE
    SYS_ADMIN ==>|"Creates / manages"| ADMIN_USER
    SYS_ADMIN ==>|"Creates / manages"| STAFF_USER
    SYS_ADMIN ==>|"Publishes"| ANN

    STORE -->|"1:N store_id"| ADMIN_USER
    STORE -->|"1:N store_id"| STAFF_USER
    SYS_ADMIN -.->|"1:N created_by_id"| ANN

    classDef role fill:#FFE8CC,stroke:#D9480F,stroke-width:3px,color:#3B1D00
    classDef admin fill:#FFF4E6,stroke:#F08C00,color:#3B2305
    classDef store fill:#E7F5FF,stroke:#1971C2,stroke-width:2px,color:#102A43
    class SYS_ADMIN role
    class STORE store
    class ADMIN_USER,STAFF_USER,ANN admin
```

#### 6.2.1.3 Pharmacy Administrator E-R Diagram

```mermaid
flowchart LR
    STORE_ADMIN["Pharmacy Administrator<br/>sys_user.id PK<br/>role = pharmacy_admin<br/>store_id FK"]
    STORE["Store<br/>store.id PK"]

    subgraph STORE_DATA["Data Managed by Pharmacy Administrator"]
        MFR["Manufacturer<br/>manufacturer.id PK<br/>name UNIQUE"]
        CAT["Medicine Category<br/>medicine_category.id PK<br/>name UNIQUE"]
        MED["Medicine<br/>medicine.id PK<br/>manufacturer_id FK<br/>category_id FK"]
        INV["Inventory<br/>inventory.id PK<br/>store_id FK<br/>medicine_id FK"]
        PO["Purchase Order<br/>purchase_order.id PK<br/>store_id FK<br/>manufacturer_id FK"]
        SHIFT["Shift Schedule<br/>shift_schedule.id PK<br/>store_id FK<br/>salesperson_id FK"]
    end

    STORE -->|"1:N store_id"| STORE_ADMIN
    STORE_ADMIN ==>|"Maintains"| MFR
    STORE_ADMIN ==>|"Maintains"| CAT
    STORE_ADMIN ==>|"Maintains"| MED
    STORE_ADMIN ==>|"Maintains"| INV
    STORE_ADMIN ==>|"Maintains"| PO
    STORE_ADMIN ==>|"Schedules"| SHIFT

    MFR -->|"1:N manufacturer_id"| MED
    CAT -->|"1:N category_id"| MED
    STORE -->|"1:N store_id"| INV
    MED -->|"1:N medicine_id"| INV
    STORE -->|"1:N store_id"| PO
    MFR -->|"1:N manufacturer_id"| PO
    STORE -->|"1:N store_id"| SHIFT

    classDef role fill:#FFE8CC,stroke:#D9480F,stroke-width:3px,color:#3B1D00
    classDef store fill:#E7F5FF,stroke:#1971C2,stroke-width:2px,color:#102A43
    classDef manager fill:#E6FCF5,stroke:#0CA678,color:#073B2A
    class STORE_ADMIN role
    class STORE store
    class MFR,CAT,MED,INV,PO,SHIFT manager
```

#### 6.2.1.4 Staff E-R Diagram

```mermaid
flowchart LR
    STAFF["Salesperson<br/>sys_user.id PK<br/>role = salesperson<br/>store_id FK"]
    STORE["Store<br/>store.id PK"]
    MED["Medicine<br/>medicine.id PK"]

    subgraph STAFF_DATA["Data Created by Salesperson"]
        SO["Sale Order<br/>sale_order.id PK<br/>store_id FK<br/>salesperson_id FK"]
        SOI["Sale Order Item<br/>sale_order_item.id PK<br/>order_id FK<br/>medicine_id FK"]
        LOGI["Order Logistics<br/>order_logistics.id PK<br/>order_id FK"]
        REVIEW["Order Review<br/>order_review.id PK<br/>order_id FK and UNIQUE"]
    end

    STORE -->|"1:N store_id"| STAFF
    STAFF ==>|"Creates"| SO
    STAFF ==>|"Updates"| LOGI
    STAFF ==>|"Submits"| REVIEW

    STORE -->|"1:N store_id"| SO
    SO -->|"1:N order_id"| SOI
    MED -->|"1:N medicine_id"| SOI
    SO -->|"1:N order_id"| LOGI
    SO -->|"1:1 order_id"| REVIEW

    classDef role fill:#FFE8CC,stroke:#D9480F,stroke-width:3px,color:#3B1D00
    classDef store fill:#E7F5FF,stroke:#1971C2,stroke-width:2px,color:#102A43
    classDef staff fill:#F3F0FF,stroke:#7048E8,color:#24164F
    class STAFF role
    class STORE,MED store
    class SO,SOI,LOGI,REVIEW staff
```

### 6.3 Physical Design Highlights

- Primary keys are defined for every business table.
- Foreign keys connect users, stores, medicines, inventory, orders, logistics, and reviews.
- Unique constraints are defined for store code, store name, username, manufacturer name, medicine category name, medicine code, inventory store-medicine pair, purchase order number, and sale order number.
- Check constraints validate role values, prices, inventory quantities, purchase status, order status, item amount, and review rating.
- Indexes are defined on high-frequency query fields such as medicine name, medicine code, manufacturer name, store, inventory medicine, order status, and order creation time.
- A database view `v_medicine_stock` provides a stock overview with store, medicine, manufacturer, quantity, warning threshold, and warning status.
- Trigger `fn_set_updated_at` automatically refreshes `updated_at` when records are modified.
- Trigger `fn_log_sale_item` writes sale item insertion records into `operation_log`.

### 6.4 Important SQL Files

| File | Purpose |
|---|---|
| `sql/schema.sql` | Creates tables, constraints, indexes, view, and triggers |
| `sql/init_data.sql` | Inserts demo stores, users, medicines, inventory, orders, announcements, purchase orders, and schedules |
| `sql/announcement_extension.sql` | Compatibility no-op; announcement schema is merged into `schema.sql` |
| `sql/sales_extension.sql` | Compatibility no-op; sales schema is merged into `schema.sql` |

## 7. Backend Design

### 7.1 Django Apps

| App | Responsibility |
|---|---|
| `accounts` | Login, current user, user management, role permissions, shift schedules |
| `medicine` | Manufacturer, category, and medicine APIs |
| `inventory` | Store, inventory, and purchase order APIs |
| `sales` | Sales order, order item, logistics, and review APIs |
| `announcements` | Announcement CRUD APIs |
| `common` | Dashboard overview and statistical aggregation |

### 7.2 Main API Modules

| API prefix | Description |
|---|---|
| `/api/auth/` | Login and current user |
| `/api/users/` | User and shift schedule management |
| `/api/medicines/` | Manufacturer, category, medicine management |
| `/api/inventory/` | Store, inventory, purchase order management |
| `/api/sales/` | Sales orders, logistics, reviews |
| `/api/announcements/` | Announcement management |
| `/api/dashboard/` | Dashboard statistics |

### 7.3 Permission Control

The backend uses DRF permission classes to protect APIs:

- `IsSystemAdmin`: only system administrators can manage stores, pharmacy administrators, salespersons, and announcements.
- `IsPharmacyAdmin`: only pharmacy administrators can manage medicines, manufacturers, inventory, purchase orders, and shift schedules.
- `InventoryPermission`: pharmacy administrators can write inventory data; salespersons can only read it.
- `SalesPermission`: all roles can read authorized sales records; only salespersons can create sales orders and update logistics/reviews.

## 8. Frontend Design

### 8.1 Page Structure

| Page | Main users | Main features |
|---|---|---|
| Login | All users | Login with demo or created accounts |
| Dashboard | All users | Business overview, income trend, stock risk, hot medicines, order status |
| Store Management | System administrator | Store CRUD and details |
| Pharmacy Admin Management | System administrator | Manage pharmacy administrators |
| Salesperson Management | System administrator | Manage salespersons |
| Announcement Management | System administrator | Publish and maintain announcements |
| Revenue Comparison | System administrator | Store revenue ranking, period filter, CSV export |
| Manufacturer Management | Pharmacy administrator | Manufacturer CRUD |
| Medicine Management | Pharmacy administrator, salesperson read-only | Medicine CRUD and fuzzy query |
| Inventory Management | Pharmacy administrator, salesperson read-only | Stock maintenance, warning filter, pagination, CSV export |
| Purchase Orders | Pharmacy administrator | Purchase order management |
| Shift Schedules | Pharmacy administrator | Salesperson scheduling |
| Sales Create | Salesperson | Search medicines, cart, phone validation, submit order |
| Sales Records | All roles | Search, status filter, date filter, pagination, detail view, CSV export |
| Logistics | Salesperson | Logistics update |
| Reviews | Salesperson | Submit customer reviews |

### 8.2 Frontend Permission Flow

```mermaid
flowchart TD
    A[Open page] --> B{Has access token?}
    B -- No --> C[Redirect to login]
    B -- Yes --> D[Read current user role]
    D --> E{Route allows role?}
    E -- No --> F[Redirect to dashboard]
    E -- Yes --> G[Render authorized page and menu]
```

### 8.3 Visual Dashboard Design

The dashboard is designed for supervisors and store managers. It contains:

- Total orders, revenue, store count, employee count.
- Monthly and yearly order/revenue summary.
- Low-stock and near-expiry risk cards.
- Pending payment and delivering order cards.
- Low-stock item list and near-expiry medicine list.
- Ten-day income line chart.
- Ten-day order bar chart.
- Top-selling medicines in the last 30 days.
- Order status distribution.
- Medicine category stock ratio.
- Published announcements.
- Seven-day business activity records.

## 9. Core Business Processes

### 9.1 Login Process

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant Backend
    participant DB as openGauss
    User->>Frontend: Input username and password
    Frontend->>Backend: POST /api/auth/login/
    Backend->>DB: Query user and verify password
    DB-->>Backend: Return user data
    Backend-->>Frontend: Return JWT token and role
    Frontend->>Frontend: Save token and render role menu
```

### 9.2 Sales Order Process

```mermaid
flowchart TD
    A[Salesperson searches inventory] --> B[Add medicines to cart]
    B --> C[Input customer information]
    C --> D[Submit sales order]
    D --> E{Stock sufficient?}
    E -- No --> F[Return stock warning]
    E -- Yes --> G[Create sale_order]
    G --> H[Create sale_order_item records]
    H --> I[Deduct inventory quantity]
    I --> J[Create logistics record]
    J --> K[Trigger operation_log record]
    K --> L[Return order number]
```

The backend wraps order creation and inventory deduction in a database transaction. If any item has insufficient stock, the order is rejected and inventory remains unchanged.

### 9.3 Inventory Warning Process

```mermaid
flowchart LR
    A[Inventory quantity] --> B{quantity <= warning_threshold}
    B -- Yes --> C[Marked as low stock]
    B -- No --> D[Marked as normal]
    C --> E[Shown on inventory page]
    C --> F[Counted on dashboard]
```

## 10. Testing

### 10.1 Functional Test Cases

| No. | Test case | Expected result |
|---|---|---|
| 1 | Login as `sysadmin` | System administrator menu is displayed |
| 2 | Login as `storeadmin` | Pharmacy administrator menu is displayed |
| 3 | Login as `sales01` | Salesperson menu is displayed |
| 4 | System administrator creates a pharmacy administrator | User appears in pharmacy administrator table |
| 5 | System administrator resets password | Target user can login with `Admin@123` |
| 6 | Pharmacy administrator creates a medicine | Medicine appears in medicine table |
| 7 | Search medicine by code/name/manufacturer | Matching records are returned |
| 8 | Pharmacy administrator updates inventory | Quantity and warning status are updated |
| 9 | Salesperson creates a sales order | Order is created and inventory is deducted |
| 10 | Salesperson creates order with insufficient stock | Request is rejected with stock warning |
| 11 | View order detail | Order items, logistics, and review are displayed |
| 12 | Dashboard opens after login | Charts and risk cards load successfully |
| 13 | Export inventory/sales/revenue CSV | Browser downloads the CSV file |
| 14 | Unauthorized route access | User is redirected to dashboard |

### 10.2 Smoke Check

The project includes `backend/scripts/smoke_check.py` for basic API checks after the backend is running.

## 11. Deployment and Reproduction

### 11.1 Docker Compose Mode

```powershell
docker compose up -d --build
```

Access:

- Frontend: `http://127.0.0.1:8080`
- Backend: `http://127.0.0.1:8000`
- API prefix: `http://127.0.0.1:8000/api`

### 11.2 Local Development Mode

```powershell
docker compose up -d db
cd backend
python scripts\init_compose_db.py
python manage.py runserver
```

```powershell
cd frontend
npm.cmd install
npm.cmd run dev
```

Access:

- Frontend: `http://127.0.0.1:5173`
- Backend: `http://127.0.0.1:8000`

## 12. Demo Accounts

| Username | Password | Role |
|---|---|---|
| `sysadmin` | `Admin@123` | System administrator |
| `storeadmin` | `Admin@123` | Pharmacy administrator |
| `sales01` | `Admin@123` | Salesperson |

## 13. Contribution Description

If submitted by a group, replace the member names before final submission.

| Member | Main contribution |
|---|---|
| Member 1 | Requirement analysis, database design, SQL schema, initial data |
| Member 2 | Backend API, authentication, permissions, transaction logic |
| Member 3 | Frontend pages, dashboard visualization, user interaction |
| Member 4 | Testing, documentation, Docker deployment, demo video |

If submitted individually, the student completed requirement analysis, database design, backend development, frontend development, testing, documentation, and deployment independently.

## 14. Conclusion

The Chain Pharmacy Management System satisfies the database course design requirements. It is based on openGauss, implements three role types, supports CRUD operations, fuzzy query, user permission management, transaction-safe sales processing, and a user-friendly visual interface. The system also provides Docker-based reproduction, complete SQL files, demo data, and documentation suitable for course submission and demonstration.
