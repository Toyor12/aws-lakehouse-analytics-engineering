import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

random.seed(42)

COUNTRIES = ["US", "UK", "DE", "FR", "JP"]
ACCOUNT_TYPES = ["checking", "savings", "business"]
ACCOUNT_STATUSES = ["active", "inactive", "closed"]
TXN_TYPES = ["debit", "credit"]
TXN_STATUSES = ["completed", "pending", "failed"]
KYC_STATUSES = ["verified", "pending", "expired"]

OUT_DIR = Path("data/seed")
OUT_DIR.mkdir(parents=True, exist_ok=True)

def random_date(start_year=2022, end_year=2025):
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 12, 31)
    delta = end - start
    return (start + timedelta(days=random.randint(0, delta.days))).strftime("%Y-%m-%d")

def random_timestamp(start_year=2024, end_year=2025):
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 12, 31)
    delta = end - start
    dt = start + timedelta(seconds=random.randint(0, int(delta.total_seconds())))
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")

# Customers (200 rows)
with open(OUT_DIR / "customers.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["customer_id", "first_name", "last_name", "email", "country", "kyc_status", "created_at"])
    for i in range(1, 201):
        writer.writerow([
            f"CUST-{i:04d}",
            f"First{i}",
            f"Last{i}",
            f"customer{i}@example.com",
            random.choice(COUNTRIES),
            random.choice(KYC_STATUSES),
            random_date(2020, 2023)
        ])

# Accounts (500 rows)
with open(OUT_DIR / "accounts.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["account_id", "customer_id", "account_type", "balance", "status", "opened_date"])
    for i in range(1, 501):
        writer.writerow([
            f"ACC-{i:05d}",
            f"CUST-{random.randint(1, 200):04d}",
            random.choice(ACCOUNT_TYPES),
            round(random.uniform(100, 500000), 2),
            random.choice(ACCOUNT_STATUSES),
            random_date(2021, 2024)
        ])

# Transactions (5000 rows)
with open(OUT_DIR / "transactions.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["txn_id", "account_id", "amount", "txn_type", "txn_date", "status"])
    for i in range(1, 5001):
        writer.writerow([
            f"TXN-{i:07d}",
            f"ACC-{random.randint(1, 500):05d}",
            round(random.uniform(1, 50000), 2),
            random.choice(TXN_TYPES),
            random_timestamp(),
            random.choice(TXN_STATUSES)
        ])
