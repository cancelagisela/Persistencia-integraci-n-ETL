CREATE TABLE IF NOT EXISTS user_order_metrics (
    user_id INTEGER PRIMARY KEY,
    total_orders INTEGER NOT NULL,
    total_amount REAL NOT NULL
);
