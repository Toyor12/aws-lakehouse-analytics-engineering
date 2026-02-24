# Mini-Project: Budget-Friendly Banking Data Platform

**Duration:** 2 days x 3 hours = 6 hours total
**Estimated AWS Cost:** < $0.25
**Level:** Junior Cloud Data Engineer

---

## Overview

Build an end-to-end cloud ELT pipeline for a banking data platform using AWS services on free tier. You will provision infrastructure with Terraform, ingest data with AWS Glue, transform it with dbt, and query it with Athena.

### What You Will Learn

- **Infrastructure as Code:** Provision AWS resources with Terraform
- **Cloud Ingestion:** Use AWS Glue Crawlers and ETL Jobs to discover schemas and process data
- **Data Lake Architecture:** Store raw and curated data in S3 using Parquet format
- **Data Transformation:** Build a medallion architecture (staging / intermediate / marts) with dbt
- **Cloud Analytics:** Query transformed data with Amazon Athena
- **Cost Management:** Tear down all resources with `terraform destroy` when done

### Architecture

```
Local Machine                          AWS Cloud (Free Tier)
+--------------+                      +-----------------------------+
|  Terraform   |---- provisions ----> |  S3 Bucket (data lake)      |
|  (IaC)       |                      |    +-- raw/                  |
|              |                      |    +-- staging/              |
|  dbt Core    |                      |    +-- marts/                |
|  (transforms)|---- queries -------> |                              |
|              |                      |  Glue Data Catalog           |
|  CSV seed    |                      |    +-- banking_db            |
|  data        |---- upload --------> |                              |
+--------------+                      |  Glue Crawler                |
                                      |    +-- auto-discover schema  |
                                      |                              |
                                      |  Glue ETL Job                |
                                      |    +-- clean + partition     |
                                      |                              |
                                      |  Athena                      |
                                      |    +-- query curated data    |
                                      |                              |
                                      |  IAM Roles + Policies        |
                                      +-----------------------------+
```

**Data Flow:** CSV files -> S3 raw/ -> Glue Crawler (schema) -> Glue ETL Job (clean to Parquet) -> S3 staging/ -> dbt-athena (transform) -> S3 marts/ -> Athena (query)

---

## Prerequisites

- AWS account with free tier access
- AWS CLI configured (`aws configure`)
- Terraform >= 1.5 installed
- Python 3.9+ installed
- dbt Core + dbt-athena-community installed (`pip install dbt-athena-community`)

---

## Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **IaC** | Terraform | Provision and teardown all AWS resources |
| **Ingestion** | AWS Glue 4.0 | Crawlers for schema discovery, ETL jobs for data processing |
| **Data Lake** | Amazon S3 | Raw CSV storage, Parquet staging, mart outputs |
| **Metadata** | AWS Glue Data Catalog | Centralized schema registry |
| **Query Engine** | Amazon Athena | Serverless SQL queries on S3 data |
| **Transformation** | dbt Core + dbt-athena | SQL-based medallion architecture |

---

## Data Scope

3 tables from a single source (Core Banking), using synthetic seed data:

| Table | Rows | Key Columns |
|-------|------|-------------|
| customers | ~200 | customer_id, first_name, last_name, email, country, kyc_status, created_at |
| accounts | ~500 | account_id, customer_id, account_type, balance, status, opened_date |
| transactions | ~5,000 | txn_id, account_id, amount, txn_type, txn_date, status |

---

## Schedule

### Day 1 (3 hours): Infrastructure + Ingestion

| Time | Activity | Details |
|------|----------|---------|
| 0:00-0:30 | Terraform tutorial | Learn providers, resources, variables, outputs, init/plan/apply/destroy |
| 0:30-1:15 | Write Terraform configs | S3 buckets, IAM role, Glue database, Crawler, ETL job, Athena workgroup |
| 1:15-1:30 | Deploy infrastructure | `terraform init && terraform plan && terraform apply` |
| 1:30-1:45 | Upload seed data | AWS CLI to copy CSVs to S3 raw/ |
| 1:45-2:15 | Run Glue Crawler | Discover schemas, verify tables in Data Catalog |
| 2:15-2:45 | Run Glue ETL Job | Clean data, convert to Parquet, add audit columns |
| 2:45-3:00 | Verify in Athena | Ad-hoc SQL queries to confirm data landed correctly |

### Day 2 (3 hours): Transformation + Analytics

| Time | Activity | Details |
|------|----------|---------|
| 0:00-0:30 | dbt project setup | Install dbt-athena, configure profiles.yml, define sources |
| 0:30-1:30 | Build dbt models | Staging (3 views), Intermediate (1 join), Marts (1 fact + 1 dimension) |
| 1:30-2:00 | Add dbt tests | unique, not_null, relationships tests; run test suite |
| 2:00-2:15 | Generate dbt docs | `dbt docs generate && dbt docs serve` |
| 2:15-2:45 | Query marts in Athena | Analytical queries on dim_customers and fct_daily_transactions |
| 2:45-3:00 | Teardown | `terraform destroy` to remove all AWS resources |

---

## dbt Medallion Architecture

### Staging (views)
- `stg_customers` — light cleaning, type casting
- `stg_accounts` — rename status -> account_status, cast balance to decimal(18,2)
- `stg_transactions` — rename status -> txn_status, cast amount to decimal(18,2)

### Intermediate (tables)
- `int_customer_accounts` — join customers with accounts

### Marts (tables)
- `dim_customers` — enriched customer dimension with account count, total balance, active accounts
- `fct_daily_transactions` — daily transaction aggregates per account (debits, credits, net amount)

---

## Terraform Resources

| Resource | Purpose |
|----------|---------|
| `aws_s3_bucket.data_lake` | Raw, staging, and mart data storage |
| `aws_s3_bucket.athena_results` | Athena query result output |
| `aws_s3_bucket.glue_scripts` | Store Glue ETL PySpark scripts |
| `aws_iam_role.glue_role` | Glue service role with S3 access |
| `aws_glue_catalog_database` | Data Catalog database for banking tables |
| `aws_glue_crawler` | Discover schemas from raw CSV files in S3 |
| `aws_glue_job` | PySpark ETL: CSV -> Parquet with audit columns |
| `aws_athena_workgroup` | Query workgroup with result location configured |

---

## Key Commands

```bash
# Terraform
cd terraform
terraform init                    # initialize providers
terraform plan                    # preview changes
terraform apply                   # deploy resources
terraform destroy                 # teardown everything
terraform output                  # show resource names/IDs

# AWS CLI (data upload)
aws s3 cp data/seed/ s3://BUCKET/raw/ --recursive

# Glue
aws glue start-crawler --name CRAWLER_NAME
aws glue get-crawler --name CRAWLER_NAME --query 'Crawler.State'
aws glue start-job-run --job-name JOB_NAME
aws glue get-job-runs --job-name JOB_NAME --query 'JobRuns[0].JobRunState'

# dbt
cd dbt_project
dbt debug                         # test connection
dbt run                           # run all models
dbt run --select staging          # run staging layer only
dbt test                          # run all tests
dbt docs generate && dbt docs serve
```

---

## Estimated Cost

| Service | Usage | Cost |
|---------|-------|------|
| S3 | <1 GB storage | ~$0.02 |
| Glue Data Catalog | <1M objects (free tier) | $0.00 |
| Glue Crawler | 1-2 runs | ~$0.01 |
| Glue ETL Job | 2-3 DPU-minutes | ~$0.15 |
| Athena | <100 MB scanned | ~$0.01 |
| **Total** | | **< $0.25** |

**IMPORTANT:** Run `terraform destroy` when finished to avoid ongoing charges.

---

## Deliverables

- [ ] Terraform configs provisioning S3, Glue, Athena, IAM
- [ ] Synthetic seed data (3 CSV files)
- [ ] Glue Crawler discovering schema in Data Catalog
- [ ] Glue ETL Job converting CSV to Parquet with audit columns
- [ ] dbt staging models (3 views)
- [ ] dbt intermediate model (1 join table)
- [ ] dbt mart models (1 fact, 1 dimension)
- [ ] dbt tests passing (unique, not_null, relationships)
- [ ] dbt docs generated
- [ ] Athena queries on mart tables
- [ ] Clean teardown via `terraform destroy`

---

## Terraform Tutorial

### What is Terraform?

Terraform is an Infrastructure as Code (IaC) tool by HashiCorp. Instead of clicking through the AWS Console to create resources, you write configuration files that describe what you want, and Terraform creates it for you. This is repeatable, version-controlled, and easy to tear down.

### Core Concepts

| Concept | Description | Example |
|---------|-------------|---------|
| **Provider** | Cloud platform plugin | `aws`, `google`, `azurerm` |
| **Resource** | A single infrastructure object | `aws_s3_bucket`, `aws_glue_job` |
| **Variable** | Parameterized input | `var.aws_region` |
| **Output** | Exported value after apply | Bucket name, role ARN |
| **State** | Terraform's record of what exists | `terraform.tfstate` (auto-managed) |

### File Structure

```
terraform/
  main.tf          # All resource definitions
  variables.tf     # Input variables with defaults
  outputs.tf       # Values to export after apply
  glue_scripts/
    etl_job.py     # PySpark script uploaded to S3
```

### The Terraform Workflow

```
terraform init     # Download provider plugins (run once)
       |
       v
terraform plan     # Preview what will be created/changed
       |
       v
terraform apply    # Actually create the resources in AWS
       |
       v
terraform output   # Show resource names, bucket IDs, etc.
       |
       v
terraform destroy  # Delete everything when done
```

### Example: Creating an S3 Bucket

```hcl
# 1. Tell Terraform which provider to use
provider "aws" {
  region = "us-east-1"
}

# 2. Define a resource
resource "aws_s3_bucket" "my_bucket" {
  bucket        = "my-unique-bucket-name"
  force_destroy = true    # allows terraform destroy to delete non-empty buckets

  tags = {
    Project = "banking-mini"
  }
}

# 3. Export the bucket name
output "bucket_name" {
  value = aws_s3_bucket.my_bucket.bucket
}
```

### Variables

```hcl
# variables.tf — define a variable with a default
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

# main.tf — use the variable
provider "aws" {
  region = var.aws_region
}
```

### Resource References

Terraform automatically figures out the order to create resources based on references:

```hcl
# This bucket is created first...
resource "aws_s3_bucket" "data" {
  bucket = "my-data-bucket"
}

# ...because this resource references it
resource "aws_glue_crawler" "my_crawler" {
  s3_target {
    path = "s3://${aws_s3_bucket.data.bucket}/raw/"
  }
}
```

### Tips

- Always run `terraform plan` before `terraform apply` to review changes
- Always run `terraform destroy` when you are done to avoid costs
- Add `terraform.tfstate` and `.terraform/` to `.gitignore`
- Use `force_destroy = true` on S3 buckets so they can be deleted even when non-empty
- Use `random_id` resources to generate unique bucket name suffixes (S3 bucket names are globally unique)

---

## Project Structure

```
module-3-project/
  README.md                              # This file (English)
  README_DE.md                           # German version
  GEMINI.md                              # AI assistant context
  budget.md                              # Cost comparison document
  data/
    seed/
      customers.csv                      # 200 synthetic customers
      accounts.csv                       # 500 synthetic accounts
      transactions.csv                   # 5,000 synthetic transactions
  scripts/
    generate_seed_data.py                # Seed data generator
  terraform/
    main.tf                              # All AWS resource definitions
    variables.tf                         # Input variables
    outputs.tf                           # Exported resource values
    glue_scripts/
      etl_job.py                         # PySpark ETL script for Glue
  dbt_project/
    dbt_project.yml                      # dbt configuration
    profiles.yml                         # Athena connection config
    models/
      sources.yml                        # Source definitions
      staging/
        stg_customers.sql
        stg_accounts.sql
        stg_transactions.sql
        schema.yml
      intermediate/
        int_customer_accounts.sql
        schema.yml
      marts/
        dim_customers.sql
        fct_daily_transactions.sql
        schema.yml
  docs/
    plans/                               # Design and implementation plans
```

---

## References

- [Terraform AWS Provider Docs](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [AWS Glue Documentation](https://docs.aws.amazon.com/glue/)
- [Amazon Athena Documentation](https://docs.aws.amazon.com/athena/)
- [dbt Documentation](https://docs.getdbt.com/)
- [dbt-athena Adapter](https://github.com/dbt-athena/dbt-athena)
