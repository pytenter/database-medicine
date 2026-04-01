INSERT INTO store (id, code, name, address, phone, manager_name, is_active) VALUES
(1, 'ST001', 'Main City Pharmacy', 'No. 88 Renmin Road, City Center', '020-88886666', 'Li Ming', TRUE),
(2, 'ST002', 'East District Pharmacy', 'No. 18 Jianshe Road, East District', '020-66668888', 'Wang Hui', TRUE);

INSERT INTO manufacturer (id, name, contact_person, contact_phone) VALUES
(1, 'Guangzhou Pharma Group', 'Chen Wei', '13800138001'),
(2, 'HealthCare Bio Ltd.', 'Liu Fang', '13800138002'),
(3, 'Sunrise Medical Co.', 'Zhang Lei', '13800138003');

INSERT INTO medicine_category (id, name, description) VALUES
(1, 'Cold Medicine', 'Medicine for cold and flu symptoms'),
(2, 'Antibiotic', 'Prescription antibiotics'),
(3, 'Vitamin', 'Vitamin and nutritional supplements');

INSERT INTO medicine (id, code, name, specification, unit, purchase_price, retail_price, manufacturer_id, category_id, approval_number, production_date, expiry_date, is_active) VALUES
(1, 'MED001', 'Paracetamol Tablets', '500mg*24 tablets', 'box', 8.50, 12.00, 1, 1, 'H20240001', '2025-01-10', '2027-01-09', TRUE),
(2, 'MED002', 'Amoxicillin Capsules', '250mg*24 capsules', 'box', 10.00, 15.50, 2, 2, 'H20240002', '2025-02-15', '2027-02-14', TRUE),
(3, 'MED003', 'Vitamin C Tablets', '100mg*60 tablets', 'bottle', 11.20, 18.00, 3, 3, 'H20240003', '2025-03-01', '2027-02-28', TRUE),
(4, 'MED004', 'Ibuprofen Sustained-Release Capsules', '300mg*20 capsules', 'box', 13.40, 20.00, 1, 1, 'H20240004', '2025-04-01', '2027-03-31', TRUE);

INSERT INTO inventory (id, store_id, medicine_id, quantity, warning_threshold) VALUES
(1, 1, 1, 120, 20),
(2, 1, 2, 80, 15),
(3, 1, 3, 200, 30),
(4, 1, 4, 60, 15),
(5, 2, 1, 90, 20),
(6, 2, 3, 160, 30);

INSERT INTO sys_user (
    id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff,
    is_active, date_joined, full_name, role, phone, store_id, created_at, updated_at
) VALUES
(1, 'pbkdf2_sha256$720000$pharmacysalt$mdIxpcALutnXzEVnumj7V6UVBm403DRDjvYNvGMMpyk=', NULL, TRUE, 'sysadmin', '', '', 'sysadmin@example.com', TRUE, TRUE, CURRENT_TIMESTAMP, 'System Admin', 'system_admin', '13800000001', NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
(2, 'pbkdf2_sha256$720000$pharmacysalt$mdIxpcALutnXzEVnumj7V6UVBm403DRDjvYNvGMMpyk=', NULL, FALSE, 'storeadmin', '', '', 'storeadmin@example.com', FALSE, TRUE, CURRENT_TIMESTAMP, 'Store Admin', 'pharmacy_admin', '13800000002', 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
(3, 'pbkdf2_sha256$720000$pharmacysalt$mdIxpcALutnXzEVnumj7V6UVBm403DRDjvYNvGMMpyk=', NULL, FALSE, 'sales01', '', '', 'sales01@example.com', FALSE, TRUE, CURRENT_TIMESTAMP, 'Sales Person 01', 'salesperson', '13800000003', 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

SELECT setval('store_id_seq', (SELECT MAX(id) FROM store));
SELECT setval('manufacturer_id_seq', (SELECT MAX(id) FROM manufacturer));
SELECT setval('medicine_category_id_seq', (SELECT MAX(id) FROM medicine_category));
SELECT setval('medicine_id_seq', (SELECT MAX(id) FROM medicine));
SELECT setval('inventory_id_seq', (SELECT MAX(id) FROM inventory));
SELECT setval('sys_user_id_seq', (SELECT MAX(id) FROM sys_user));
