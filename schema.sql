-- schema.sql
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT,
    amount INTEGER,
    person TEXT,
    date TEXT,
    raw_sms TEXT
);
