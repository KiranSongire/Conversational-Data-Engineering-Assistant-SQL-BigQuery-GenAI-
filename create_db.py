import sqlite3
from datetime import datetime, timedelta

conn = sqlite3.connect("dataops_demo.db")
cur = conn.cursor()

cur.executescript("""
DROP TABLE IF EXISTS pipeline_errors;
DROP TABLE IF EXISTS data_quality_checks;
DROP TABLE IF EXISTS pipeline_runs;

CREATE TABLE pipeline_runs (
    run_id INTEGER PRIMARY KEY AUTOINCREMENT,
    pipeline_name TEXT NOT NULL,
    source_system TEXT,
    target_table TEXT,
    status TEXT,
    start_time TEXT,
    end_time TEXT,
    rows_read INTEGER,
    rows_written INTEGER,
    error_message TEXT
);

CREATE TABLE pipeline_errors (
    error_id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id INTEGER,
    error_type TEXT,
    error_message TEXT,
    error_time TEXT,
    severity TEXT,
    FOREIGN KEY (run_id) REFERENCES pipeline_runs(run_id)
);

CREATE TABLE data_quality_checks (
    check_id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id INTEGER,
    table_name TEXT,
    check_name TEXT,
    expected_count INTEGER,
    actual_count INTEGER,
    check_status TEXT,
    created_at TEXT,
    FOREIGN KEY (run_id) REFERENCES pipeline_runs(run_id)
);
""")

now = datetime.now()

pipeline_data = [
    ("customer_ingestion", "PostgreSQL", "bq_customer", "SUCCESS", now- timedelta(hours=5), now- timedelta(hours=4, minutes=50), 10000, 10000, None),
    ("orders_ingestion", "PostgreSQL", "bq_orders", "FAILED", now- timedelta(hours=4), now- timedelta(hours=3, minutes=45), 15000, 12000, "Schema mismatch on column order_status"),
    ("billing_pipeline", "API", "bq_billing", "RUNNING", now- timedelta(hours=3), None, 8000, 0, None),
    ("claims_pipeline", "GCS", "bq_claims", "FAILED", now- timedelta(days=1), now- timedelta(days=1, minutes=-20), 5000, 4700, "Null value found in required column"),
    ("inventory_pipeline", "MySQL", "bq_inventory", "SUCCESS", now- timedelta(hours=2), now- timedelta(hours=1, minutes=45), 20000, 20000, None),
]

for row in pipeline_data:
    cur.execute("""
        INSERT INTO pipeline_runs
        (pipeline_name, source_system, target_table, status, start_time, end_time, rows_read, rows_written, error_message)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        row[0], row[1], row[2], row[3],
        row[4].isoformat(),
        row[5].isoformat() if row[5] else None,
        row[6], row[7], row[8]
    ))

error_data = [
    (2, "SCHEMA_ERROR", "Column order_status changed from STRING to INTEGER", now- timedelta(hours=3, minutes=50), "HIGH"),
    (4, "DATA_QUALITY", "Required column claim_id contains NULL values", now- timedelta(days=1, minutes=-10), "HIGH"),
]

for row in error_data:
    cur.execute("""
        INSERT INTO pipeline_errors
        (run_id, error_type, error_message, error_time, severity)
        VALUES (?, ?, ?, ?, ?)
    """, (row[0], row[1], row[2], row[3].isoformat(), row[4]))

dq_data = [
    (1, "bq_customer", "row_count_match", 10000, 10000, "PASS", now),
    (2, "bq_orders", "row_count_match", 15000, 12000, "FAIL", now),
    (4, "bq_claims", "null_check", 0, 25, "FAIL", now),
    (5, "bq_inventory", "row_count_match", 20000, 20000, "PASS", now),
]

for row in dq_data:
    cur.execute("""
        INSERT INTO data_quality_checks
        (run_id, table_name, check_name, expected_count, actual_count, check_status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (row[0], row[1], row[2], row[3], row[4], row[5], row[6].isoformat()))

conn.commit()
conn.close()

print("dataops_demo.db created successfully.")