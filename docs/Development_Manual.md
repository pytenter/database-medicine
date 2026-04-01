# Development Manual

## 1. Project Overview

Project Name: Chain Pharmacy Management System  
Development Type: Database application system course design  
Technology Stack: Vue 3, Django REST Framework, openGauss, Docker, Navicat  

This project implements a chain pharmacy management system for three kinds of users: system administrator, pharmacy administrator, and salesperson. The goal is to build a complete database application that demonstrates database design, permission control, data maintenance, fuzzy query, and sales processing.

## 2. Project Planning

### 2.1 Objectives

- Build a clear role-based pharmacy management system.
- Use openGauss as the core database platform.
- Implement CRUD operations for users, medicines, and inventory.
- Implement fuzzy query for medicines by code, name, and manufacturer.
- Implement role-based access control and transaction-safe sales processing.

### 2.2 Schedule

- Week 1: Requirement analysis and topic selection.
- Week 2: E-R design and logical database design.
- Week 3: Physical database design and SQL implementation.
- Week 4: Backend API development.
- Week 5: Frontend page development and testing.
- Week 6: Integration testing, video recording, and documentation.

## 3. Requirement Analysis

### 3.1 User Roles

- System Administrator: manage pharmacy administrators and salespersons.
- Pharmacy Administrator: manage medicine information, categories, manufacturers, and inventory.
- Salesperson: search medicines and create sale orders.

### 3.2 Core Functional Requirements

- User login and identity recognition.
- User creation, modification, deletion, and password reset.
- Medicine creation, modification, deletion, and fuzzy search.
- Inventory creation, modification, deletion, and warning display.
- Sale order creation and sale record query.
- Permission-based menu display and backend interface protection.

## 4. Database Design

### 4.1 Main Entities

- Store
- User
- Manufacturer
- MedicineCategory
- Medicine
- Inventory
- SaleOrder
- SaleOrderItem
- OperationLog

### 4.2 Main Relationships

- One store can have many users.
- One store can store many medicines.
- One manufacturer can produce many medicines.
- One category can include many medicines.
- One sale order can include many sale order items.

### 4.3 Physical Design Features

- Primary keys and foreign keys are defined for all business tables.
- Unique constraints are defined for store code, store name, medicine code, and username.
- Check constraints are used for role values, prices, and inventory quantities.
- Indexes are created for medicine name, medicine code, manufacturer name, and sale order creation time.
- A database view named `v_medicine_stock` is provided for stock overview.
- Trigger functions are provided to update `updated_at` automatically and log inserted sale items.

## 5. System Implementation

### 5.1 Frontend

The frontend is built with Vue 3 and Vite. The interface contains the following pages:

- Login page
- Dashboard page
- User management page
- Medicine management page
- Inventory management page
- Sale order creation page
- Sales record page

### 5.2 Backend

The backend is built with Django REST Framework and divided into the following apps:

- `accounts`
- `medicine`
- `inventory`
- `sales`
- `common`

### 5.3 Permission Design

- System administrator can access user management.
- Pharmacy administrator can maintain medicine and inventory data.
- Salesperson can only query stock and create sales.
- Backend permissions and frontend route guards are both implemented.

## 6. Key SQL Design

Important SQL files are stored in the `sql/` folder.

- `schema.sql`: create tables, constraints, indexes, view, and triggers.
- `init_data.sql`: insert initial stores, medicines, inventory, and demo users.

## 7. Testing

### 7.1 Functional Test Cases

- Login with three different roles.
- Add, update, and delete user data.
- Add, update, and delete medicine data.
- Fuzzy query medicines by keyword.
- Update inventory quantity and threshold.
- Create sale orders and verify inventory deduction.
- Open sales records and check order details.

### 7.2 Expected Results

All pages should be accessible only to authorized roles. CRUD operations should return successful responses. Sale order creation should reduce inventory and generate sale history records.

## 8. Personal Contribution

This project is completed by one student independently.

- Requirement analysis
- Database modeling and SQL development
- Django backend development
- Vue frontend development
- Testing, documentation, and demo preparation

## 9. Conclusion

The project satisfies the requirements of the database course design task. It demonstrates database analysis, physical design, role permission control, CRUD functions, fuzzy query, and a complete web-based application workflow.
