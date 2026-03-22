# Budget-Friendly Banking Data Platform

End-to-end cloud ELT pipeline on AWS using Terraform, AWS Glue, dbt, and Athena. This project provisions a low-cost serverless data platform, ingests raw banking data into a data lake, transforms it into analytics-ready models, and enables SQL-based querying through Athena.

---

## Overview

This project demonstrates how to build a simple but realistic cloud data platform using AWS free-tier friendly services and modern data engineering tooling.

The pipeline uses:
- Terraform for infrastructure provisioning
- AWS Glue for ingestion and schema discovery
- Amazon S3 as the data lake
- dbt for layered SQL transformations
- Athena for querying transformed data

---

## Key Features

- Infrastructure provisioned using Terraform
- Serverless ELT pipeline using S3, Glue, Athena, and dbt
- Medallion-style data lake (raw → staging → marts)
- CSV to Parquet conversion for efficient querying
- dbt models for transformation (staging, intermediate, marts)
- Data quality testing with dbt (unique, not_null, relationships)
- Total estimated cost under $0.25

---

## Architecture

```text
Local Machine                          AWS Cloud
+--------------+                      +-----------------------------+
|  Terraform   |---- provisions ----> |  S3 Bucket (data lake)      |
|  (IaC)       |                      |    +-- raw/                  |
|              |                      |    +-- staging/              |
|  dbt Core    |---- queries -------> |    +-- marts/                |
|  (SQL models)|                      |                              |
|              |                      |  Glue Data Catalog           |
|  CSV seed    |---- upload --------> |    +-- banking_db            |
|  data        |                      |                              |
+--------------+                      |  Glue Crawler                |
                                      |    +-- schema discovery      |
                                      |                              |
                                      |  Glue ETL Job                |
                                      |    +-- CSV to Parquet        |
                                      |                              |
                                      |  Athena                      |
                                      |    +-- analytics queries     |
                                      |                              |
                                      |  IAM Roles + Policies        |
                                      +-----------------------------+
```

---

## Data Flow

CSV → S3 (raw) → Glue Crawler → Glue ETL → S3 (staging) → dbt → S3 (marts) → Athena

---

## Why This Project Matters

This project reflects practical patterns used in modern data engineering:

- Infrastructure as Code for reproducibility
- Serverless data lake architecture
- Separation of ingestion and transformation layers
- Columnar storage (Parquet) for performance and cost efficiency
- SQL-based modelling with dbt
- Built-in data quality validation

---

## Technology Stack

| Component | Technology | Purpose |
|----------|-----------|--------|
| IaC | Terraform | Provision AWS resources |
| Data Lake | Amazon S3 | Store raw and processed data |
| Ingestion | AWS Glue | Crawlers and ETL jobs |
| Metadata | Glue Data Catalog | Schema management |
| Transformation | dbt Core + dbt-athena | Data modelling |
| Query Engine | Amazon Athena | SQL analytics |
| Language | Python / SQL | ETL and transformations |

---

## Data Scope

Synthetic core banking dataset:

| Table | Rows | Key Columns |
|------|------|------------|
| customers | ~200 | customer_id, email, country |
| accounts | ~500 | account_id, customer_id, balance |
| transactions | ~5,000 | txn_id, account_id, amount |

---

## dbt Model Layers

### Staging
- `stg_customers`
- `stg_accounts`
- `stg_transactions`

### Intermediate
- `int_customer_accounts`

### Marts
- `dim_customers`
- `fct_daily_transactions`

---

## Outputs

- AWS infrastructure via Terraform
- Raw data ingested into S3
- Schema discovery via Glue Crawler
- CSV transformed to Parquet via Glue
- dbt models (staging → marts)
- Data quality tests
- Athena-ready analytical tables

---

## How to Run

### 1. Provision infrastructure
```bash
cd terraform
terraform init
terraform apply
```

### 2. Upload data
```bash
aws s3 cp data/seed/ s3://<bucket>/raw/ --recursive
```

### 3. Run Glue
```bash
aws glue start-crawler --name <crawler>
aws glue start-job-run --job-name <job>
```

### 4. Run dbt
```bash
cd dbt_project
dbt run
dbt test
```

### 5. Query in Athena

Query:
- `dim_customers`
- `fct_daily_transactions`

### 6. Tear down
```bash
terraform destroy
```

---

## Estimated Cost

| Service | Cost |
|--------|------|
| S3 | ~$0.02 |
| Glue | ~$0.16 |
| Athena | ~$0.01 |
| **Total** | **< $0.25** |

---

## Project Structure

```text
module-3-project/
├── data/
├── terraform/
├── dbt_project/
├── scripts/
├── docs/
```

---

## Key Learnings

- Terraform-based infrastructure setup
- S3 data lake design
- Glue ingestion and schema discovery
- dbt transformation workflows
- Medallion architecture implementation
- Cost-efficient cloud development

---

## Future Improvements

- Add orchestration (Dagster or Airflow)
- Add CI/CD for Terraform and dbt
- Add data quality monitoring
- Optimize partitioning strategy
- Add dashboard layer (Power BI / Superset)

---

## References

- Terraform AWS Provider Docs  
- AWS Glue Docs  
- Amazon Athena Docs  
- dbt Docs  
