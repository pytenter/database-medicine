ALTER TABLE sale_order ADD COLUMN customer_phone VARCHAR(20);
ALTER TABLE sale_order ADD COLUMN order_status VARCHAR(20) NOT NULL DEFAULT 'ordered';

CREATE TABLE order_logistics (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES sale_order(id) ON DELETE CASCADE,
    content VARCHAR(255) NOT NULL,
    operator_name VARCHAR(100),
    status_after VARCHAR(20),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE order_review (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL UNIQUE REFERENCES sale_order(id) ON DELETE CASCADE,
    rating SMALLINT NOT NULL DEFAULT 5,
    content VARCHAR(255),
    reviewer_name VARCHAR(100),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_order_logistics_order_id ON order_logistics(order_id);
CREATE INDEX idx_order_review_order_id ON order_review(order_id);
