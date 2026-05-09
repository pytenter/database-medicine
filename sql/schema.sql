DROP TABLE IF EXISTS operation_log CASCADE;
DROP TABLE IF EXISTS sale_order_item CASCADE;
DROP TABLE IF EXISTS sale_order CASCADE;
DROP TABLE IF EXISTS shift_schedule CASCADE;
DROP TABLE IF EXISTS purchase_order_item CASCADE;
DROP TABLE IF EXISTS purchase_order CASCADE;
DROP TABLE IF EXISTS announcement CASCADE;
DROP TABLE IF EXISTS inventory CASCADE;
DROP TABLE IF EXISTS medicine CASCADE;
DROP TABLE IF EXISTS manufacturer CASCADE;
DROP TABLE IF EXISTS medicine_category CASCADE;
DROP TABLE IF EXISTS sys_user CASCADE;
DROP TABLE IF EXISTS store CASCADE;

CREATE TABLE store (
    id SERIAL PRIMARY KEY,
    code VARCHAR(20) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL UNIQUE,
    address VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    manager_name VARCHAR(50),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE sys_user (
    id SERIAL PRIMARY KEY,
    password VARCHAR(128) NOT NULL,
    last_login TIMESTAMP NULL,
    is_superuser BOOLEAN NOT NULL DEFAULT FALSE,
    username VARCHAR(150) NOT NULL UNIQUE,
    first_name VARCHAR(150) NOT NULL DEFAULT '',
    last_name VARCHAR(150) NOT NULL DEFAULT '',
    email VARCHAR(254) NOT NULL DEFAULT '',
    is_staff BOOLEAN NOT NULL DEFAULT FALSE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    date_joined TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    full_name VARCHAR(100) NOT NULL,
    role VARCHAR(30) NOT NULL,
    phone VARCHAR(20),
    store_id INTEGER NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT ck_sys_user_role CHECK (role IN ('system_admin', 'pharmacy_admin', 'salesperson')),
    CONSTRAINT fk_sys_user_store FOREIGN KEY (store_id) REFERENCES store(id)
);

CREATE TABLE announcement (
    id SERIAL PRIMARY KEY,
    title VARCHAR(120) NOT NULL,
    content TEXT NOT NULL,
    is_published BOOLEAN NOT NULL DEFAULT TRUE,
    created_by_id INTEGER NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_announcement_created_by FOREIGN KEY (created_by_id) REFERENCES sys_user(id) ON DELETE SET NULL
);

CREATE TABLE manufacturer (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    contact_person VARCHAR(50),
    contact_phone VARCHAR(20),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE medicine_category (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description VARCHAR(255),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE medicine (
    id SERIAL PRIMARY KEY,
    code VARCHAR(30) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    specification VARCHAR(100) NOT NULL,
    unit VARCHAR(20) NOT NULL DEFAULT '盒',
    purchase_price NUMERIC(10, 2) NOT NULL,
    retail_price NUMERIC(10, 2) NOT NULL,
    manufacturer_id INTEGER NOT NULL,
    category_id INTEGER NOT NULL,
    approval_number VARCHAR(60),
    production_date DATE,
    expiry_date DATE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT ck_medicine_purchase_price CHECK (purchase_price > 0),
    CONSTRAINT ck_medicine_retail_price CHECK (retail_price > 0),
    CONSTRAINT fk_medicine_manufacturer FOREIGN KEY (manufacturer_id) REFERENCES manufacturer(id),
    CONSTRAINT fk_medicine_category FOREIGN KEY (category_id) REFERENCES medicine_category(id)
);

CREATE TABLE inventory (
    id SERIAL PRIMARY KEY,
    store_id INTEGER NOT NULL,
    medicine_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 0,
    warning_threshold INTEGER NOT NULL DEFAULT 10,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uk_inventory_store_medicine UNIQUE (store_id, medicine_id),
    CONSTRAINT ck_inventory_quantity CHECK (quantity >= 0),
    CONSTRAINT ck_inventory_warning CHECK (warning_threshold >= 0),
    CONSTRAINT fk_inventory_store FOREIGN KEY (store_id) REFERENCES store(id) ON DELETE CASCADE,
    CONSTRAINT fk_inventory_medicine FOREIGN KEY (medicine_id) REFERENCES medicine(id) ON DELETE CASCADE
);

CREATE TABLE purchase_order (
    id SERIAL PRIMARY KEY,
    order_no VARCHAR(30) NOT NULL UNIQUE,
    store_id INTEGER NOT NULL,
    manufacturer_id INTEGER NOT NULL,
    purchaser_name VARCHAR(50) NOT NULL,
    planned_date DATE NULL,
    total_amount NUMERIC(10, 2) NOT NULL DEFAULT 0,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    item_summary VARCHAR(255) NOT NULL,
    remark VARCHAR(255) NOT NULL DEFAULT '',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT ck_purchase_order_total_amount CHECK (total_amount >= 0),
    CONSTRAINT ck_purchase_order_status CHECK (status IN ('pending', 'ordered', 'received', 'cancelled')),
    CONSTRAINT fk_purchase_order_store FOREIGN KEY (store_id) REFERENCES store(id) ON DELETE CASCADE,
    CONSTRAINT fk_purchase_order_manufacturer FOREIGN KEY (manufacturer_id) REFERENCES manufacturer(id) ON DELETE RESTRICT
);

CREATE TABLE purchase_order_item (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL,
    medicine_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price NUMERIC(10, 2) NOT NULL,
    amount NUMERIC(12, 2) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT ck_purchase_order_item_quantity CHECK (quantity > 0),
    CONSTRAINT ck_purchase_order_item_unit_price CHECK (unit_price > 0),
    CONSTRAINT ck_purchase_order_item_amount CHECK (amount > 0),
    CONSTRAINT fk_purchase_order_item_order FOREIGN KEY (order_id) REFERENCES purchase_order(id) ON DELETE CASCADE,
    CONSTRAINT fk_purchase_order_item_medicine FOREIGN KEY (medicine_id) REFERENCES medicine(id) ON DELETE RESTRICT
);

CREATE TABLE shift_schedule (
    id SERIAL PRIMARY KEY,
    store_id INTEGER NOT NULL,
    salesperson_id INTEGER NOT NULL,
    shift_date DATE NOT NULL,
    shift_period VARCHAR(20) NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    note VARCHAR(255) NOT NULL DEFAULT '',
    created_by_id INTEGER NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT ck_shift_schedule_shift_period CHECK (shift_period IN ('morning', 'afternoon', 'evening')),
    CONSTRAINT fk_shift_schedule_store FOREIGN KEY (store_id) REFERENCES store(id) ON DELETE CASCADE,
    CONSTRAINT fk_shift_schedule_salesperson FOREIGN KEY (salesperson_id) REFERENCES sys_user(id) ON DELETE CASCADE,
    CONSTRAINT fk_shift_schedule_created_by FOREIGN KEY (created_by_id) REFERENCES sys_user(id) ON DELETE SET NULL
);

CREATE TABLE sale_order (
    id SERIAL PRIMARY KEY,
    order_no VARCHAR(32) NOT NULL UNIQUE,
    store_id INTEGER NOT NULL,
    salesperson_id INTEGER NOT NULL,
    customer_name VARCHAR(100) NOT NULL DEFAULT '',
    customer_phone VARCHAR(20) NOT NULL DEFAULT '',
    total_amount NUMERIC(12, 2) NOT NULL DEFAULT 0,
    remark VARCHAR(255) NOT NULL DEFAULT '',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT ck_sale_order_total_amount CHECK (total_amount >= 0),
    CONSTRAINT fk_sale_order_store FOREIGN KEY (store_id) REFERENCES store(id),
    CONSTRAINT fk_sale_order_salesperson FOREIGN KEY (salesperson_id) REFERENCES sys_user(id)
);

CREATE TABLE sale_order_item (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL,
    medicine_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price NUMERIC(10, 2) NOT NULL,
    amount NUMERIC(12, 2) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT ck_sale_order_item_quantity CHECK (quantity > 0),
    CONSTRAINT ck_sale_order_item_unit_price CHECK (unit_price > 0),
    CONSTRAINT ck_sale_order_item_amount CHECK (amount > 0),
    CONSTRAINT fk_sale_order_item_order FOREIGN KEY (order_id) REFERENCES sale_order(id) ON DELETE CASCADE,
    CONSTRAINT fk_sale_order_item_medicine FOREIGN KEY (medicine_id) REFERENCES medicine(id)
);

CREATE TABLE operation_log (
    id SERIAL PRIMARY KEY,
    operator_id INTEGER,
    action_type VARCHAR(30) NOT NULL,
    action_detail VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_operation_log_operator FOREIGN KEY (operator_id) REFERENCES sys_user(id)
);

CREATE INDEX idx_announcement_created_at ON announcement(created_at);
CREATE INDEX idx_medicine_name ON medicine(name);
CREATE INDEX idx_medicine_code ON medicine(code);
CREATE INDEX idx_manufacturer_name ON manufacturer(name);
CREATE INDEX idx_inventory_store ON inventory(store_id);
CREATE INDEX idx_inventory_medicine ON inventory(medicine_id);
CREATE INDEX idx_purchase_order_store ON purchase_order(store_id);
CREATE INDEX idx_purchase_order_manufacturer ON purchase_order(manufacturer_id);
CREATE INDEX idx_purchase_order_status ON purchase_order(status);
CREATE INDEX idx_purchase_order_item_order ON purchase_order_item(order_id);
CREATE INDEX idx_purchase_order_item_medicine ON purchase_order_item(medicine_id);
CREATE INDEX idx_shift_schedule_store ON shift_schedule(store_id);
CREATE INDEX idx_shift_schedule_salesperson ON shift_schedule(salesperson_id);
CREATE INDEX idx_shift_schedule_date ON shift_schedule(shift_date);
CREATE INDEX idx_sale_order_created_at ON sale_order(created_at);
CREATE OR REPLACE VIEW v_medicine_stock AS
SELECT
    s.id AS store_id,
    s.name AS store_name,
    m.id AS medicine_id,
    m.code AS medicine_code,
    m.name AS medicine_name,
    mf.name AS manufacturer_name,
    i.quantity,
    i.warning_threshold,
    CASE WHEN i.quantity <= i.warning_threshold THEN '库存预警' ELSE '库存正常' END AS stock_status
FROM inventory i
JOIN store s ON i.store_id = s.id
JOIN medicine m ON i.medicine_id = m.id
JOIN manufacturer mf ON m.manufacturer_id = mf.id;

CREATE OR REPLACE FUNCTION fn_set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION fn_log_sale_item()
RETURNS TRIGGER AS $$
DECLARE
    v_salesperson_id INTEGER;
BEGIN
    SELECT salesperson_id INTO v_salesperson_id FROM sale_order WHERE id = NEW.order_id;
    INSERT INTO operation_log(operator_id, action_type, action_detail)
    VALUES (v_salesperson_id, '销售出库', '销售出库：药品ID=' || NEW.medicine_id || '，数量=' || NEW.quantity);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_store_updated_at BEFORE UPDATE ON store
FOR EACH ROW EXECUTE PROCEDURE fn_set_updated_at();

CREATE TRIGGER trg_sys_user_updated_at BEFORE UPDATE ON sys_user
FOR EACH ROW EXECUTE PROCEDURE fn_set_updated_at();

CREATE TRIGGER trg_announcement_updated_at BEFORE UPDATE ON announcement
FOR EACH ROW EXECUTE PROCEDURE fn_set_updated_at();

CREATE TRIGGER trg_manufacturer_updated_at BEFORE UPDATE ON manufacturer
FOR EACH ROW EXECUTE PROCEDURE fn_set_updated_at();

CREATE TRIGGER trg_medicine_category_updated_at BEFORE UPDATE ON medicine_category
FOR EACH ROW EXECUTE PROCEDURE fn_set_updated_at();

CREATE TRIGGER trg_medicine_updated_at BEFORE UPDATE ON medicine
FOR EACH ROW EXECUTE PROCEDURE fn_set_updated_at();

CREATE TRIGGER trg_inventory_updated_at BEFORE UPDATE ON inventory
FOR EACH ROW EXECUTE PROCEDURE fn_set_updated_at();

CREATE TRIGGER trg_purchase_order_updated_at BEFORE UPDATE ON purchase_order
FOR EACH ROW EXECUTE PROCEDURE fn_set_updated_at();

CREATE TRIGGER trg_purchase_order_item_updated_at BEFORE UPDATE ON purchase_order_item
FOR EACH ROW EXECUTE PROCEDURE fn_set_updated_at();

CREATE TRIGGER trg_shift_schedule_updated_at BEFORE UPDATE ON shift_schedule
FOR EACH ROW EXECUTE PROCEDURE fn_set_updated_at();

CREATE TRIGGER trg_sale_order_updated_at BEFORE UPDATE ON sale_order
FOR EACH ROW EXECUTE PROCEDURE fn_set_updated_at();

CREATE TRIGGER trg_sale_order_item_updated_at BEFORE UPDATE ON sale_order_item
FOR EACH ROW EXECUTE PROCEDURE fn_set_updated_at();

CREATE TRIGGER trg_log_sale_item AFTER INSERT ON sale_order_item
FOR EACH ROW EXECUTE PROCEDURE fn_log_sale_item();
