INSERT INTO store (id, code, name, address, phone, manager_name, is_active) VALUES
(1, 'ST001', '市中心门店', '人民路 88 号', '020-88886666', '李明', TRUE),
(2, 'ST002', '东区门店', '建设路 18 号', '020-66668888', '王辉', TRUE);

INSERT INTO manufacturer (id, name, contact_person, contact_phone) VALUES
(1, '广州医药集团', '陈伟', '13800138001'),
(2, '康健生物有限公司', '刘芳', '13800138002'),
(3, '晨曦医药有限公司', '张磊', '13800138003');

INSERT INTO medicine_category (id, name, description) VALUES
(1, '感冒药', '用于治疗感冒和流感症状'),
(2, '抗生素', '处方抗生素药品'),
(3, '维生素', '维生素与营养补充剂');

INSERT INTO medicine (id, code, name, specification, unit, purchase_price, retail_price, manufacturer_id, category_id, approval_number, production_date, expiry_date, is_active) VALUES
(1, 'MED001', '对乙酰氨基酚片', '500mg*24片', '盒', 8.50, 12.00, 1, 1, 'H20240001', '2025-01-10', '2027-01-09', TRUE),
(2, 'MED002', '阿莫西林胶囊', '250mg*24粒', '盒', 10.00, 15.50, 2, 2, 'H20240002', '2025-02-15', '2027-02-14', TRUE),
(3, 'MED003', '维生素C片', '100mg*60片', '瓶', 11.20, 18.00, 3, 3, 'H20240003', '2025-03-01', '2027-02-28', TRUE),
(4, 'MED004', '布洛芬缓释胶囊', '300mg*20粒', '盒', 13.40, 20.00, 1, 1, 'H20240004', '2025-04-01', '2027-03-31', TRUE);

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
(1, 'pbkdf2_sha256$720000$pharmacysalt$mdIxpcALutnXzEVnumj7V6UVBm403DRDjvYNvGMMpyk=', NULL, TRUE, 'sysadmin', '', '', 'sysadmin@example.com', TRUE, TRUE, CURRENT_TIMESTAMP, '系统管理员', 'system_admin', '13800000001', NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
(2, 'pbkdf2_sha256$720000$pharmacysalt$mdIxpcALutnXzEVnumj7V6UVBm403DRDjvYNvGMMpyk=', NULL, FALSE, 'storeadmin', '', '', 'storeadmin@example.com', FALSE, TRUE, CURRENT_TIMESTAMP, '门店管理员', 'pharmacy_admin', '13800000002', 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
(3, 'pbkdf2_sha256$720000$pharmacysalt$mdIxpcALutnXzEVnumj7V6UVBm403DRDjvYNvGMMpyk=', NULL, FALSE, 'sales01', '', '', 'sales01@example.com', FALSE, TRUE, CURRENT_TIMESTAMP, '销售员01', 'salesperson', '13800000003', 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

SELECT setval('store_id_seq', (SELECT MAX(id) FROM store));
SELECT setval('manufacturer_id_seq', (SELECT MAX(id) FROM manufacturer));
SELECT setval('medicine_category_id_seq', (SELECT MAX(id) FROM medicine_category));
SELECT setval('medicine_id_seq', (SELECT MAX(id) FROM medicine));
SELECT setval('inventory_id_seq', (SELECT MAX(id) FROM inventory));
SELECT setval('sys_user_id_seq', (SELECT MAX(id) FROM sys_user));
