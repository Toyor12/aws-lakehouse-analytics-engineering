# Budget Banking Data Platform — Implementation Plan

For Gemini, this can be a good way for it to start.


**Goal:** Build a budget-friendly banking ELT pipeline using Terraform, AWS Glue, S3, Athena, and dbt in 6 hours (2 days x 3 hours).

**Architecture:** CSV seed data → S3 raw/ → Glue Crawler (schema discovery) → Glue ETL Job (clean to Parquet) → S3 staging/ → dbt-athena (transform via medallion layers) → S3 marts/ → Athena (query). All infrastructure provisioned via Terraform and torn down at end.

**Tech Stack:** Terraform, AWS Glue (Crawler + ETL), S3, Athena, dbt Core + dbt-athena, Python, AWS CLI

---

## Day 1: Infrastructure + Ingestion (3 hours)

### Task 1: Project Structure

**Files:**
- Create: `terraform/main.tf`
- Create: `terraform/variables.tf`
- Create: `terraform/outputs.tf`
- Create: `terraform/glue_scripts/etl_job.py`
- Create: `data/seed/accounts.csv`
- Create: `data/seed/customers.csv`
- Create: `data/seed/transactions.csv`
- Create: `dbt_project/dbt_project.yml`
- Create: `dbt_project/profiles.yml`

**Step 1: Create directory structure**

```bash
mkdir -p terraform/glue_scripts
mkdir -p data/seed
mkdir -p dbt_project/models/staging
mkdir -p dbt_project/models/intermediate
mkdir -p dbt_project/models/marts
mkdir -p dbt_project/tests
```

**Step 2: Commit scaffold**

```bash
git add -A
git commit -m "chore: scaffold project structure"
```

---

### Task 2: Generate Synthetic Seed Data

**Files:**
- Create: `data/seed/customers.csv`
- Create: `data/seed/accounts.csv`
- Create: `data/seed/transactions.csv`
- Create: `scripts/generate_seed_data.py`

**Step 1: Write seed data generator**

```python
# scripts/generate_seed_data.py
import csv
import random
from datetime import datetime, timedelta

random.seed(42)

COUNTRIES = ["US", "UK", "DE", "FR", "JP"]
ACCOUNT_TYPES = ["checking", "savings", "business"]
ACCOUNT_STATUSES = ["active", "inactive", "closed"]
TXN_TYPES = ["debit", "credit"]
TXN_STATUSES = ["completed", "pending", "failed"]
KYC_STATUSES = ["verified", "pending", "expired"]

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
with open("data/seed/customers.csv", "w", newline="") as f:
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
with open("data/seed/accounts.csv", "w", newline="") as f:
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
with open("data/seed/transactions.csv", "w", newline="") as f:
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
```

**Step 2: Run the generator**

```bash
python scripts/generate_seed_data.py
```

**Step 3: Verify files exist and have correct row counts**

```bash
wc -l data/seed/*.csv
# Expected: 201 customers.csv, 501 accounts.csv, 5001 transactions.csv
```

**Step 4: Commit**

```bash
git add data/seed/ scripts/
git commit -m "feat: add synthetic seed data generator and CSV files"
```

---

### Task 3: Terraform — S3 Buckets

**Files:**
- Create: `terraform/variables.tf`
- Create: `terraform/main.tf`

**Step 1: Write variables**

```hcl
# terraform/variables.tf
variable "aws_region" {
  description = "AWS region for all resources"
  type        = string
  default     = "us-east-1"
}

variable "project_prefix" {
  description = "Prefix for all resource names"
  type        = string
  default     = "banking-mini"
}

variable "environment" {
  description = "Environment tag"
  type        = string
  default     = "dev"
}
```

**Step 2: Write main.tf with provider and S3**

```hcl
# terraform/main.tf
terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# --- S3 Buckets ---

resource "aws_s3_bucket" "data_lake" {
  bucket        = "${var.project_prefix}-data-lake-${random_id.suffix.hex}"
  force_destroy = true

  tags = {
    Project     = var.project_prefix
    Environment = var.environment
  }
}

resource "aws_s3_bucket" "athena_results" {
  bucket        = "${var.project_prefix}-athena-results-${random_id.suffix.hex}"
  force_destroy = true

  tags = {
    Project     = var.project_prefix
    Environment = var.environment
  }
}

resource "aws_s3_bucket" "glue_scripts" {
  bucket        = "${var.project_prefix}-glue-scripts-${random_id.suffix.hex}"
  force_destroy = true

  tags = {
    Project     = var.project_prefix
    Environment = var.environment
  }
}

resource "random_id" "suffix" {
  byte_length = 4
}
```

**Step 3: Run `terraform init` to validate**

```bash
cd terraform && terraform init
```

**Step 4: Commit**

```bash
git add terraform/
git commit -m "feat: add Terraform provider config and S3 buckets"
```

---

### Task 4: Terraform — IAM Role for Glue

**Files:**
- Modify: `terraform/main.tf`

**Step 1: Add IAM role and policy to main.tf**

```hcl
# --- IAM Role for Glue ---

resource "aws_iam_role" "glue_role" {
  name = "${var.project_prefix}-glue-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "glue.amazonaws.com"
      }
    }]
  })

  tags = {
    Project     = var.project_prefix
    Environment = var.environment
  }
}

resource "aws_iam_role_policy" "glue_s3_access" {
  name = "${var.project_prefix}-glue-s3-policy"
  role = aws_iam_role.glue_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.data_lake.arn,
          "${aws_s3_bucket.data_lake.arn}/*",
          aws_s3_bucket.glue_scripts.arn,
          "${aws_s3_bucket.glue_scripts.arn}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "glue:*"
        ]
        Resource = ["*"]
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = ["*"]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "glue_service" {
  role       = aws_iam_role.glue_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole"
}
```

**Step 2: Commit**

```bash
git add terraform/main.tf
git commit -m "feat: add Glue IAM role with S3 access policy"
```

---

### Task 5: Terraform — Glue Data Catalog + Crawler

**Files:**
- Modify: `terraform/main.tf`

**Step 1: Add Glue database and crawler**

```hcl
# --- Glue Data Catalog ---

resource "aws_glue_catalog_database" "banking" {
  name = "${var.project_prefix}_db"
}

# --- Glue Crawler (discovers schema from raw CSVs in S3) ---

resource "aws_glue_crawler" "raw_data" {
  name          = "${var.project_prefix}-raw-crawler"
  role          = aws_iam_role.glue_role.arn
  database_name = aws_glue_catalog_database.banking.name

  s3_target {
    path = "s3://${aws_s3_bucket.data_lake.bucket}/raw/"
  }

  schema_change_policy {
    update_behavior = "UPDATE_IN_DATABASE"
    delete_behavior = "LOG"
  }

  tags = {
    Project     = var.project_prefix
    Environment = var.environment
  }
}
```

**Step 2: Commit**

```bash
git add terraform/main.tf
git commit -m "feat: add Glue Data Catalog database and raw crawler"
```

---

### Task 6: Terraform — Glue ETL Job

**Files:**
- Modify: `terraform/main.tf`
- Create: `terraform/glue_scripts/etl_job.py`

**Step 1: Write PySpark ETL script**

```python
# terraform/glue_scripts/etl_job.py
import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.context import SparkContext
from pyspark.sql.functions import current_timestamp, lit, col
from pyspark.sql.types import DecimalType

args = getResolvedOptions(sys.argv, ["JOB_NAME", "SOURCE_BUCKET", "TARGET_BUCKET"])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args["JOB_NAME"], args)

source_bucket = args["SOURCE_BUCKET"]
target_bucket = args["TARGET_BUCKET"]

tables = ["customers", "accounts", "transactions"]

for table in tables:
    source_path = f"s3://{source_bucket}/raw/{table}/"
    target_path = f"s3://{target_bucket}/staging/{table}/"

    df = spark.read.option("header", "true").option("inferSchema", "true").csv(source_path)

    # Add audit columns
    df = df.withColumn("_loaded_at", current_timestamp())
    df = df.withColumn("_source_system", lit("core_banking"))

    # Cast balance/amount to decimal(18,2) if present
    if "balance" in df.columns:
        df = df.withColumn("balance", col("balance").cast(DecimalType(18, 2)))
    if "amount" in df.columns:
        df = df.withColumn("amount", col("amount").cast(DecimalType(18, 2)))

    # Write as Parquet with Snappy compression
    df.write.mode("overwrite").option("compression", "snappy").parquet(target_path)

    print(f"Processed {table}: {df.count()} rows written to {target_path}")

job.commit()
```

**Step 2: Add Glue ETL Job and script upload to Terraform**

```hcl
# --- Upload ETL Script to S3 ---

resource "aws_s3_object" "etl_script" {
  bucket = aws_s3_bucket.glue_scripts.id
  key    = "scripts/etl_job.py"
  source = "${path.module}/glue_scripts/etl_job.py"
  etag   = filemd5("${path.module}/glue_scripts/etl_job.py")
}

# --- Glue ETL Job ---

resource "aws_glue_job" "etl" {
  name     = "${var.project_prefix}-etl-job"
  role_arn = aws_iam_role.glue_role.arn

  command {
    name            = "glueetl"
    script_location = "s3://${aws_s3_bucket.glue_scripts.bucket}/scripts/etl_job.py"
    python_version  = "3"
  }

  default_arguments = {
    "--SOURCE_BUCKET"             = aws_s3_bucket.data_lake.bucket
    "--TARGET_BUCKET"             = aws_s3_bucket.data_lake.bucket
    "--job-language"              = "python"
    "--TempDir"                   = "s3://${aws_s3_bucket.glue_scripts.bucket}/temp/"
    "--enable-metrics"            = "true"
    "--enable-continuous-cloudwatch-log" = "true"
  }

  max_retries       = 0
  number_of_workers = 2
  worker_type       = "G.1X"
  glue_version      = "4.0"

  tags = {
    Project     = var.project_prefix
    Environment = var.environment
  }
}
```

**Step 3: Commit**

```bash
git add terraform/
git commit -m "feat: add Glue ETL job with PySpark script"
```

---

### Task 7: Terraform — Athena Workgroup + Outputs

**Files:**
- Modify: `terraform/main.tf`
- Create: `terraform/outputs.tf`

**Step 1: Add Athena workgroup**

```hcl
# --- Athena Workgroup ---

resource "aws_athena_workgroup" "primary" {
  name = "${var.project_prefix}-workgroup"

  configuration {
    enforce_workgroup_configuration = true

    result_configuration {
      output_location = "s3://${aws_s3_bucket.athena_results.bucket}/results/"
    }
  }

  tags = {
    Project     = var.project_prefix
    Environment = var.environment
  }
}
```

**Step 2: Write outputs.tf**

```hcl
# terraform/outputs.tf
output "data_lake_bucket" {
  description = "S3 data lake bucket name"
  value       = aws_s3_bucket.data_lake.bucket
}

output "athena_results_bucket" {
  description = "S3 Athena results bucket name"
  value       = aws_s3_bucket.athena_results.bucket
}

output "glue_scripts_bucket" {
  description = "S3 Glue scripts bucket name"
  value       = aws_s3_bucket.glue_scripts.bucket
}

output "glue_database_name" {
  description = "Glue Data Catalog database name"
  value       = aws_glue_catalog_database.banking.name
}

output "glue_crawler_name" {
  description = "Glue Crawler name"
  value       = aws_glue_crawler.raw_data.name
}

output "glue_etl_job_name" {
  description = "Glue ETL Job name"
  value       = aws_glue_job.etl.name
}

output "athena_workgroup" {
  description = "Athena workgroup name"
  value       = aws_athena_workgroup.primary.name
}
```

**Step 3: Commit**

```bash
git add terraform/
git commit -m "feat: add Athena workgroup and Terraform outputs"
```

---

### Task 8: Deploy Infrastructure + Upload Data

**Step 1: Run Terraform**

```bash
cd terraform
terraform plan
terraform apply -auto-approve
```

**Step 2: Upload seed CSV data to S3 raw/**

```bash
BUCKET=$(terraform output -raw data_lake_bucket)
aws s3 cp data/seed/customers.csv "s3://${BUCKET}/raw/customers/customers.csv"
aws s3 cp data/seed/accounts.csv "s3://${BUCKET}/raw/accounts/accounts.csv"
aws s3 cp data/seed/transactions.csv "s3://${BUCKET}/raw/transactions/transactions.csv"
```

**Step 3: Verify upload**

```bash
aws s3 ls "s3://${BUCKET}/raw/" --recursive
```

---

### Task 9: Run Glue Crawler + ETL Job

**Step 1: Run the Glue Crawler**

```bash
CRAWLER=$(terraform output -raw glue_crawler_name)
aws glue start-crawler --name "$CRAWLER"
```

**Step 2: Wait for crawler to complete (~2 min)**

```bash
aws glue get-crawler --name "$CRAWLER" --query 'Crawler.State'
# Wait until "READY"
```

**Step 3: Verify tables in Data Catalog**

```bash
DB=$(terraform output -raw glue_database_name)
aws glue get-tables --database-name "$DB" --query 'TableList[].Name'
# Expected: ["accounts", "customers", "transactions"]
```

**Step 4: Run the Glue ETL Job**

```bash
JOB=$(terraform output -raw glue_etl_job_name)
aws glue start-job-run --job-name "$JOB"
```

**Step 5: Wait for job to complete (~3-5 min)**

```bash
aws glue get-job-runs --job-name "$JOB" --query 'JobRuns[0].JobRunState'
# Wait until "SUCCEEDED"
```

**Step 6: Verify Parquet files in staging/**

```bash
BUCKET=$(terraform output -raw data_lake_bucket)
aws s3 ls "s3://${BUCKET}/staging/" --recursive
```

---

### Task 10: Verify Data in Athena

**Step 1: Run ad-hoc Athena query to verify**

```bash
WORKGROUP=$(terraform output -raw athena_workgroup)
DB=$(terraform output -raw glue_database_name)

# You may need to re-run the crawler on staging/ or create tables manually.
# Alternatively, query via the Athena console.
```

**Step 2: Run sample query in Athena Console**

```sql
SELECT COUNT(*) AS total_customers FROM banking_mini_db.customers;
SELECT COUNT(*) AS total_transactions FROM banking_mini_db.transactions;
SELECT account_type, COUNT(*) AS cnt, AVG(balance) AS avg_balance
FROM banking_mini_db.accounts
GROUP BY account_type;
```

**Step 3: Commit day 1 progress**

```bash
git add -A
git commit -m "feat: complete Day 1 - infrastructure deployed and data ingested"
```

---

## Day 2: Transformation + Analytics (3 hours)

### Task 11: dbt Project Setup

**Files:**
- Create: `dbt_project/dbt_project.yml`
- Create: `dbt_project/profiles.yml`
- Create: `dbt_project/models/sources.yml`

**Step 1: Install dbt-athena**

```bash
pip install dbt-athena-community
```

**Step 2: Write dbt_project.yml**

```yaml
# dbt_project/dbt_project.yml
name: banking_mini
version: "1.0.0"

profile: banking_mini

model-paths: ["models"]
test-paths: ["tests"]
macro-paths: ["macros"]

clean-targets:
  - target
  - dbt_packages

models:
  banking_mini:
    staging:
      +materialized: view
    intermediate:
      +materialized: table
    marts:
      +materialized: table
```

**Step 3: Write profiles.yml**

```yaml
# dbt_project/profiles.yml
banking_mini:
  target: dev
  outputs:
    dev:
      type: athena
      s3_staging_dir: "s3://{{ env_var('ATHENA_RESULTS_BUCKET') }}/dbt-staging/"
      region_name: "{{ env_var('AWS_REGION', 'us-east-1') }}"
      database: "{{ env_var('GLUE_DATABASE', 'banking-mini_db') }}"
      schema: dbt
      work_group: "{{ env_var('ATHENA_WORKGROUP', 'banking-mini-workgroup') }}"
```

**Step 4: Write sources.yml**

```yaml
# dbt_project/models/sources.yml
version: 2

sources:
  - name: raw
    database: "{{ env_var('GLUE_DATABASE', 'banking-mini_db') }}"
    schema: ""
    tables:
      - name: customers
        description: "Raw customer data from Core Banking System"
      - name: accounts
        description: "Raw account data from Core Banking System"
      - name: transactions
        description: "Raw transaction data from Core Banking System"
```

**Step 5: Set environment variables**

```bash
export ATHENA_RESULTS_BUCKET=$(cd terraform && terraform output -raw athena_results_bucket)
export GLUE_DATABASE=$(cd terraform && terraform output -raw glue_database_name)
export ATHENA_WORKGROUP=$(cd terraform && terraform output -raw athena_workgroup)
export AWS_REGION=us-east-1
```

**Step 6: Verify connection**

```bash
cd dbt_project && dbt debug
```

**Step 7: Commit**

```bash
git add dbt_project/
git commit -m "feat: initialize dbt project with Athena adapter"
```

---

### Task 12: dbt Staging Models

**Files:**
- Create: `dbt_project/models/staging/stg_customers.sql`
- Create: `dbt_project/models/staging/stg_accounts.sql`
- Create: `dbt_project/models/staging/stg_transactions.sql`
- Create: `dbt_project/models/staging/schema.yml`

**Step 1: Write stg_customers.sql**

```sql
-- dbt_project/models/staging/stg_customers.sql
with source as (
    select * from {{ source('raw', 'customers') }}
)

select
    customer_id,
    first_name,
    last_name,
    email,
    country,
    kyc_status,
    cast(created_at as date) as created_at,
    _loaded_at,
    _source_system
from source
```

**Step 2: Write stg_accounts.sql**

```sql
-- dbt_project/models/staging/stg_accounts.sql
with source as (
    select * from {{ source('raw', 'accounts') }}
)

select
    account_id,
    customer_id,
    account_type,
    cast(balance as decimal(18, 2)) as balance,
    status as account_status,
    cast(opened_date as date) as opened_date,
    _loaded_at,
    _source_system
from source
```

**Step 3: Write stg_transactions.sql**

```sql
-- dbt_project/models/staging/stg_transactions.sql
with source as (
    select * from {{ source('raw', 'transactions') }}
)

select
    txn_id,
    account_id,
    cast(amount as decimal(18, 2)) as amount,
    txn_type,
    cast(txn_date as timestamp) as txn_date,
    status as txn_status,
    _loaded_at,
    _source_system
from source
```

**Step 4: Write schema.yml for staging**

```yaml
# dbt_project/models/staging/schema.yml
version: 2

models:
  - name: stg_customers
    description: "Cleaned customer data from Core Banking System"
    columns:
      - name: customer_id
        tests: [unique, not_null]

  - name: stg_accounts
    description: "Cleaned account data from Core Banking System"
    columns:
      - name: account_id
        tests: [unique, not_null]
      - name: customer_id
        tests:
          - not_null
          - relationships:
              to: ref('stg_customers')
              field: customer_id

  - name: stg_transactions
    description: "Cleaned transaction data from Core Banking System"
    columns:
      - name: txn_id
        tests: [unique, not_null]
      - name: account_id
        tests:
          - not_null
          - relationships:
              to: ref('stg_accounts')
              field: account_id
```

**Step 5: Run staging models**

```bash
cd dbt_project && dbt run --select staging
```

**Step 6: Commit**

```bash
git add dbt_project/models/staging/
git commit -m "feat: add dbt staging models for customers, accounts, transactions"
```

---

### Task 13: dbt Intermediate Model

**Files:**
- Create: `dbt_project/models/intermediate/int_customer_accounts.sql`
- Create: `dbt_project/models/intermediate/schema.yml`

**Step 1: Write int_customer_accounts.sql**

```sql
-- dbt_project/models/intermediate/int_customer_accounts.sql
with customers as (
    select * from {{ ref('stg_customers') }}
),

accounts as (
    select * from {{ ref('stg_accounts') }}
),

customer_accounts as (
    select
        c.customer_id,
        c.first_name,
        c.last_name,
        c.email,
        c.country,
        c.kyc_status,
        c.created_at as customer_created_at,
        a.account_id,
        a.account_type,
        a.balance,
        a.account_status,
        a.opened_date
    from customers c
    inner join accounts a on c.customer_id = a.customer_id
)

select * from customer_accounts
```

**Step 2: Write schema.yml**

```yaml
# dbt_project/models/intermediate/schema.yml
version: 2

models:
  - name: int_customer_accounts
    description: "Customers joined with their accounts"
    columns:
      - name: account_id
        tests: [unique, not_null]
      - name: customer_id
        tests: [not_null]
```

**Step 3: Run intermediate models**

```bash
cd dbt_project && dbt run --select intermediate
```

**Step 4: Commit**

```bash
git add dbt_project/models/intermediate/
git commit -m "feat: add intermediate customer-accounts join model"
```

---

### Task 14: dbt Mart Models

**Files:**
- Create: `dbt_project/models/marts/dim_customers.sql`
- Create: `dbt_project/models/marts/fct_daily_transactions.sql`
- Create: `dbt_project/models/marts/schema.yml`

**Step 1: Write dim_customers.sql**

```sql
-- dbt_project/models/marts/dim_customers.sql
with customer_accounts as (
    select * from {{ ref('int_customer_accounts') }}
),

aggregated as (
    select
        customer_id,
        first_name,
        last_name,
        email,
        country,
        kyc_status,
        customer_created_at,
        count(account_id) as total_accounts,
        sum(balance) as total_balance,
        min(opened_date) as earliest_account_date,
        max(opened_date) as latest_account_date,
        count(case when account_status = 'active' then 1 end) as active_accounts
    from customer_accounts
    group by
        customer_id,
        first_name,
        last_name,
        email,
        country,
        kyc_status,
        customer_created_at
)

select * from aggregated
```

**Step 2: Write fct_daily_transactions.sql**

```sql
-- dbt_project/models/marts/fct_daily_transactions.sql
with transactions as (
    select * from {{ ref('stg_transactions') }}
),

daily_agg as (
    select
        account_id,
        cast(txn_date as date) as txn_day,
        count(*) as total_transactions,
        sum(case when txn_type = 'debit' then amount else 0 end) as total_debits,
        sum(case when txn_type = 'credit' then amount else 0 end) as total_credits,
        sum(case when txn_type = 'credit' then amount else -amount end) as net_amount,
        count(case when txn_status = 'completed' then 1 end) as completed_transactions,
        count(case when txn_status = 'failed' then 1 end) as failed_transactions
    from transactions
    group by account_id, cast(txn_date as date)
)

select * from daily_agg
```

**Step 3: Write schema.yml**

```yaml
# dbt_project/models/marts/schema.yml
version: 2

models:
  - name: dim_customers
    description: "Customer dimension with aggregated account metrics"
    columns:
      - name: customer_id
        description: "Unique customer identifier from Core Banking System"
        tests: [unique, not_null]
      - name: first_name
        description: "Customer first name"
      - name: last_name
        description: "Customer last name"
      - name: email
        description: "Customer email address"
      - name: country
        description: "Customer country code (ISO 3166-1 alpha-2)"
      - name: kyc_status
        description: "Know Your Customer verification status"
      - name: customer_created_at
        description: "Date customer record was created"
      - name: total_accounts
        description: "Total number of accounts held by customer"
      - name: total_balance
        description: "Sum of all account balances (decimal 18,2)"
      - name: earliest_account_date
        description: "Date of first account opened"
      - name: latest_account_date
        description: "Date of most recent account opened"
      - name: active_accounts
        description: "Number of currently active accounts"

  - name: fct_daily_transactions
    description: "Daily transaction aggregates per account"
    columns:
      - name: account_id
        description: "Account identifier"
        tests: [not_null]
      - name: txn_day
        description: "Transaction date (day granularity)"
        tests: [not_null]
      - name: total_transactions
        description: "Total number of transactions on this day"
      - name: total_debits
        description: "Sum of debit transaction amounts"
      - name: total_credits
        description: "Sum of credit transaction amounts"
      - name: net_amount
        description: "Net amount (credits - debits)"
      - name: completed_transactions
        description: "Count of transactions with completed status"
      - name: failed_transactions
        description: "Count of transactions with failed status"
```

**Step 4: Run all models**

```bash
cd dbt_project && dbt run
```

**Step 5: Commit**

```bash
git add dbt_project/models/marts/
git commit -m "feat: add mart models - dim_customers and fct_daily_transactions"
```

---

### Task 15: Run dbt Tests + Generate Docs

**Step 1: Run all tests**

```bash
cd dbt_project && dbt test
```

Expected: All tests pass (unique, not_null, relationships).

**Step 2: Generate and serve docs**

```bash
dbt docs generate
dbt docs serve --port 8080
```

**Step 3: Commit**

```bash
git add -A
git commit -m "feat: dbt tests passing, docs generated"
```

---

### Task 16: Query Marts in Athena

**Step 1: Run analytical queries in Athena Console**

```sql
-- Top 10 customers by total balance
SELECT customer_id, first_name, last_name, country, total_accounts, total_balance
FROM dbt.dim_customers
ORDER BY total_balance DESC
LIMIT 10;

-- Daily transaction volume trend
SELECT txn_day, SUM(total_transactions) AS daily_txns, SUM(net_amount) AS daily_net
FROM dbt.fct_daily_transactions
GROUP BY txn_day
ORDER BY txn_day;

-- Transactions by country
SELECT c.country, COUNT(*) AS total_txns, SUM(f.net_amount) AS total_net
FROM dbt.fct_daily_transactions f
JOIN dbt.dim_customers c ON f.account_id IN (
    SELECT account_id FROM dbt.int_customer_accounts WHERE customer_id = c.customer_id
)
GROUP BY c.country
ORDER BY total_txns DESC;
```

---

### Task 17: Teardown

**Step 1: Destroy all AWS resources**

```bash
cd terraform && terraform destroy -auto-approve
```

**Step 2: Verify no resources remain**

```bash
terraform show
# Expected: empty state
```

**Step 3: Final commit**

```bash
git add -A
git commit -m "chore: complete mini-project, all resources destroyed"
```

---

## Deliverables Checklist

- [ ] Terraform configs provisioning S3, Glue, Athena, IAM
- [ ] Synthetic seed data (3 CSV files)
- [ ] Glue Crawler discovering schema in Data Catalog
- [ ] Glue ETL Job converting CSV to Parquet with audit columns
- [ ] dbt staging models (3 views)
- [ ] dbt intermediate model (1 join table)
- [ ] dbt mart models (1 fact, 1 dimension)
- [ ] dbt tests (unique, not_null, relationships)
- [ ] dbt docs generated
- [ ] Athena queries on mart tables
- [ ] Clean teardown via terraform destroy
