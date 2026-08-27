CREATE SCHEMA IF NOT EXISTS raw;

CREATE TABLE raw.customers (
    customer_id     SERIAL PRIMARY KEY,
    email           TEXT NOT NULL,
    full_name       TEXT NOT NULL,
    segment         TEXT NOT NULL DEFAULT 'regular',
    signup_date     DATE NOT NULL,
    updated_at      TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE raw.products (
    product_id      SERIAL PRIMARY KEY,
    sku             TEXT NOT NULL,
    product_name    TEXT NOT NULL,
    category        TEXT NOT NULL,
    price           NUMERIC(10, 2) NOT NULL,
    updated_at      TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE raw.orders (
    order_id        SERIAL PRIMARY KEY,
    customer_id     INTEGER NOT NULL REFERENCES raw.customers(customer_id),
    order_date      TIMESTAMP NOT NULL,
    status          TEXT NOT NULL DEFAULT 'completed',
    updated_at      TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE raw.order_items (
    order_item_id   SERIAL PRIMARY KEY,
    order_id        INTEGER NOT NULL REFERENCES raw.orders(order_id),
    product_id      INTEGER NOT NULL REFERENCES raw.products(product_id),
    quantity        INTEGER NOT NULL,
    unit_price      NUMERIC(10, 2) NOT NULL
);

CREATE TABLE raw.events (
    event_id        BIGSERIAL PRIMARY KEY,
    customer_id     INTEGER REFERENCES raw.customers(customer_id),
    event_type      TEXT NOT NULL,
    product_id      INTEGER REFERENCES raw.products(product_id),
    event_ts        TIMESTAMP NOT NULL DEFAULT now()
);

CREATE INDEX idx_orders_customer
    ON raw.orders(customer_id);

CREATE INDEX idx_order_items_order
    ON raw.order_items(order_id);

CREATE INDEX idx_events_customer
    ON raw.events(customer_id);

CREATE INDEX idx_events_ts
    ON raw.events(event_ts);