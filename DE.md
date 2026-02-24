# Mini-Projekt: Budgetfreundliche Banking Data Plattform

**Dauer:** 2 Tage x 3 Stunden = 6 Stunden gesamt
**Geschatzte AWS-Kosten:** < 0,25 $
**Niveau:** Junior Cloud Data Engineer

---

## Uberblick

Bauen Sie eine End-to-End Cloud-ELT-Pipeline fur eine Banking-Datenplattform mit AWS-Services im Free Tier. Sie provisionieren Infrastruktur mit Terraform, nehmen Daten mit AWS Glue auf, transformieren sie mit dbt und fragen sie mit Athena ab.

### Was Sie lernen werden

- **Infrastructure as Code:** AWS-Ressourcen mit Terraform provisionieren
- **Cloud-Datenaufnahme:** AWS Glue Crawlers und ETL-Jobs zur Schema-Erkennung und Datenverarbeitung nutzen
- **Data-Lake-Architektur:** Roh- und kuratierte Daten in S3 im Parquet-Format speichern
- **Datentransformation:** Medallion-Architektur (Staging / Intermediate / Marts) mit dbt aufbauen
- **Cloud-Analysen:** Transformierte Daten mit Amazon Athena abfragen
- **Kostenmanagement:** Alle Ressourcen mit `terraform destroy` am Ende abbauen

### Architektur

```
Lokale Maschine                        AWS Cloud (Free Tier)
+--------------+                      +-----------------------------+
|  Terraform   |---- provisioniert -> |  S3 Bucket (Data Lake)      |
|  (IaC)       |                      |    +-- raw/                  |
|              |                      |    +-- staging/              |
|  dbt Core    |                      |    +-- marts/                |
|  (Transforms)|---- Abfragen ------> |                              |
|              |                      |  Glue Data Catalog           |
|  CSV Seed-   |                      |    +-- banking_db            |
|  Daten       |---- Upload --------> |                              |
+--------------+                      |  Glue Crawler                |
                                      |    +-- Schema-Erkennung      |
                                      |                              |
                                      |  Glue ETL Job                |
                                      |    +-- Bereinigung + Parquet |
                                      |                              |
                                      |  Athena                      |
                                      |    +-- Kuratierte Daten      |
                                      |                              |
                                      |  IAM Rollen + Richtlinien    |
                                      +-----------------------------+
```

**Datenfluss:** CSV-Dateien -> S3 raw/ -> Glue Crawler (Schema) -> Glue ETL Job (Bereinigung zu Parquet) -> S3 staging/ -> dbt-athena (Transformation) -> S3 marts/ -> Athena (Abfrage)

---

## Voraussetzungen

- AWS-Konto mit Free-Tier-Zugang
- AWS CLI konfiguriert (`aws configure`)
- Terraform >= 1.5 installiert
- Python 3.9+ installiert
- dbt Core + dbt-athena-community installiert (`pip install dbt-athena-community`)

---

## Technologie-Stack

| Komponente | Technologie | Zweck |
|-----------|-----------|---------|
| **IaC** | Terraform | Provisionierung und Abbau aller AWS-Ressourcen |
| **Aufnahme** | AWS Glue 4.0 | Crawler fur Schema-Erkennung, ETL-Jobs fur Datenverarbeitung |
| **Data Lake** | Amazon S3 | Roh-CSV-Speicherung, Parquet-Staging, Mart-Ausgaben |
| **Metadaten** | AWS Glue Data Catalog | Zentrales Schema-Register |
| **Abfrage-Engine** | Amazon Athena | Serverlose SQL-Abfragen auf S3-Daten |
| **Transformation** | dbt Core + dbt-athena | SQL-basierte Medallion-Architektur |

---

## Datenumfang

3 Tabellen aus einer einzelnen Quelle (Kernbankensystem), mit synthetischen Seed-Daten:

| Tabelle | Zeilen | Wichtige Spalten |
|---------|--------|-----------------|
| customers | ~200 | customer_id, first_name, last_name, email, country, kyc_status, created_at |
| accounts | ~500 | account_id, customer_id, account_type, balance, status, opened_date |
| transactions | ~5.000 | txn_id, account_id, amount, txn_type, txn_date, status |

---

## Zeitplan

### Tag 1 (3 Stunden): Infrastruktur + Aufnahme

| Zeit | Aktivitat | Details |
|------|----------|---------|
| 0:00-0:30 | Terraform-Tutorial | Provider, Ressourcen, Variablen, Outputs, init/plan/apply/destroy lernen |
| 0:30-1:15 | Terraform-Konfigurationen schreiben | S3-Buckets, IAM-Rolle, Glue-Datenbank, Crawler, ETL-Job, Athena-Workgroup |
| 1:15-1:30 | Infrastruktur deployen | `terraform init && terraform plan && terraform apply` |
| 1:30-1:45 | Seed-Daten hochladen | AWS CLI zum Kopieren von CSVs nach S3 raw/ |
| 1:45-2:15 | Glue Crawler ausfuhren | Schemas erkennen, Tabellen im Data Catalog verifizieren |
| 2:15-2:45 | Glue ETL Job ausfuhren | Daten bereinigen, in Parquet konvertieren, Audit-Spalten hinzufugen |
| 2:45-3:00 | In Athena verifizieren | Ad-hoc SQL-Abfragen zur Bestatigung der korrekten Datenlandung |

### Tag 2 (3 Stunden): Transformation + Analysen

| Zeit | Aktivitat | Details |
|------|----------|---------|
| 0:00-0:30 | dbt-Projekt einrichten | dbt-athena installieren, profiles.yml konfigurieren, Quellen definieren |
| 0:30-1:30 | dbt-Modelle bauen | Staging (3 Views), Intermediate (1 Join), Marts (1 Fakt + 1 Dimension) |
| 1:30-2:00 | dbt-Tests hinzufugen | unique, not_null, relationships Tests; Test-Suite ausfuhren |
| 2:00-2:15 | dbt-Dokumentation generieren | `dbt docs generate && dbt docs serve` |
| 2:15-2:45 | Marts in Athena abfragen | Analytische Abfragen auf dim_customers und fct_daily_transactions |
| 2:45-3:00 | Abbau | `terraform destroy` zum Entfernen aller AWS-Ressourcen |

---

## dbt Medallion-Architektur

### Staging (Views)
- `stg_customers` — leichte Bereinigung, Typ-Casting
- `stg_accounts` — Status -> account_status umbenennen, Balance auf decimal(18,2) casten
- `stg_transactions` — Status -> txn_status umbenennen, Amount auf decimal(18,2) casten

### Intermediate (Tabellen)
- `int_customer_accounts` — Kunden mit Konten verknupfen

### Marts (Tabellen)
- `dim_customers` — Angereicherte Kundendimension mit Kontoanzahl, Gesamtsaldo, aktiven Konten
- `fct_daily_transactions` — Tagliche Transaktionsaggregate pro Konto (Belastungen, Gutschriften, Nettobetrag)

---

## Terraform-Ressourcen

| Ressource | Zweck |
|----------|---------|
| `aws_s3_bucket.data_lake` | Roh-, Staging- und Mart-Datenspeicherung |
| `aws_s3_bucket.athena_results` | Athena-Abfrageergebnis-Ausgabe |
| `aws_s3_bucket.glue_scripts` | Glue ETL PySpark-Skripte speichern |
| `aws_iam_role.glue_role` | Glue-Service-Rolle mit S3-Zugriff |
| `aws_glue_catalog_database` | Data-Catalog-Datenbank fur Banking-Tabellen |
| `aws_glue_crawler` | Schemas aus CSV-Rohdateien in S3 erkennen |
| `aws_glue_job` | PySpark ETL: CSV -> Parquet mit Audit-Spalten |
| `aws_athena_workgroup` | Abfrage-Workgroup mit konfiguriertem Ergebnisort |

---

## Wichtige Befehle

```bash
# Terraform
cd terraform
terraform init                    # Provider-Plugins herunterladen (einmal ausfuhren)
terraform plan                    # Anderungen vorschauen
terraform apply                   # Ressourcen in AWS erstellen
terraform destroy                 # Alles abbauen
terraform output                  # Ressourcennamen/IDs anzeigen

# AWS CLI (Daten-Upload)
aws s3 cp data/seed/ s3://BUCKET/raw/ --recursive

# Glue
aws glue start-crawler --name CRAWLER_NAME
aws glue get-crawler --name CRAWLER_NAME --query 'Crawler.State'
aws glue start-job-run --job-name JOB_NAME
aws glue get-job-runs --job-name JOB_NAME --query 'JobRuns[0].JobRunState'

# dbt
cd dbt_project
dbt debug                         # Verbindung testen
dbt run                           # Alle Modelle ausfuhren
dbt run --select staging          # Nur Staging-Schicht ausfuhren
dbt test                          # Alle Tests ausfuhren
dbt docs generate && dbt docs serve
```

---

## Geschatzte Kosten

| Service | Nutzung | Kosten |
|---------|---------|--------|
| S3 | <1 GB Speicher | ~0,02 $ |
| Glue Data Catalog | <1M Objekte (Free Tier) | 0,00 $ |
| Glue Crawler | 1-2 Durchlaufe | ~0,01 $ |
| Glue ETL Job | 2-3 DPU-Minuten | ~0,15 $ |
| Athena | <100 MB gescannt | ~0,01 $ |
| **Gesamt** | | **< 0,25 $** |

**WICHTIG:** Fuhren Sie `terraform destroy` am Ende aus, um laufende Kosten zu vermeiden.

---

## Abgaben

- [ ] Terraform-Konfigurationen fur S3, Glue, Athena, IAM
- [ ] Synthetische Seed-Daten (3 CSV-Dateien)
- [ ] Glue Crawler erkennt Schema im Data Catalog
- [ ] Glue ETL Job konvertiert CSV zu Parquet mit Audit-Spalten
- [ ] dbt Staging-Modelle (3 Views)
- [ ] dbt Intermediate-Modell (1 Join-Tabelle)
- [ ] dbt Mart-Modelle (1 Fakt, 1 Dimension)
- [ ] dbt-Tests bestanden (unique, not_null, relationships)
- [ ] dbt-Dokumentation generiert
- [ ] Athena-Abfragen auf Mart-Tabellen
- [ ] Sauberer Abbau uber `terraform destroy`

---

## Terraform-Tutorial

### Was ist Terraform?

Terraform ist ein Infrastructure-as-Code (IaC)-Tool von HashiCorp. Anstatt durch die AWS-Konsole zu klicken um Ressourcen zu erstellen, schreiben Sie Konfigurationsdateien, die beschreiben was Sie mochten, und Terraform erstellt es fur Sie. Dies ist wiederholbar, versionskontrolliert und einfach abzubauen.

### Kernkonzepte

| Konzept | Beschreibung | Beispiel |
|---------|-------------|---------|
| **Provider** | Cloud-Plattform-Plugin | `aws`, `google`, `azurerm` |
| **Resource** | Ein einzelnes Infrastrukturobjekt | `aws_s3_bucket`, `aws_glue_job` |
| **Variable** | Parametrisierte Eingabe | `var.aws_region` |
| **Output** | Exportierter Wert nach Apply | Bucket-Name, Rollen-ARN |
| **State** | Terraforms Aufzeichnung was existiert | `terraform.tfstate` (automatisch verwaltet) |

### Dateistruktur

```
terraform/
  main.tf          # Alle Ressourcendefinitionen
  variables.tf     # Eingabevariablen mit Standardwerten
  outputs.tf       # Nach Apply zu exportierende Werte
  glue_scripts/
    etl_job.py     # PySpark-Skript, das nach S3 hochgeladen wird
```

### Der Terraform-Workflow

```
terraform init     # Provider-Plugins herunterladen (einmal ausfuhren)
       |
       v
terraform plan     # Vorschau was erstellt/geandert wird
       |
       v
terraform apply    # Ressourcen tatsachlich in AWS erstellen
       |
       v
terraform output   # Ressourcennamen, Bucket-IDs usw. anzeigen
       |
       v
terraform destroy  # Alles loschen wenn fertig
```

### Beispiel: Einen S3-Bucket erstellen

```hcl
# 1. Terraform mitteilen welchen Provider es nutzen soll
provider "aws" {
  region = "us-east-1"
}

# 2. Eine Ressource definieren
resource "aws_s3_bucket" "my_bucket" {
  bucket        = "my-unique-bucket-name"
  force_destroy = true    # Erlaubt terraform destroy auch nicht-leere Buckets zu loschen

  tags = {
    Project = "banking-mini"
  }
}

# 3. Den Bucket-Namen exportieren
output "bucket_name" {
  value = aws_s3_bucket.my_bucket.bucket
}
```

### Variablen

```hcl
# variables.tf — Variable mit Standardwert definieren
variable "aws_region" {
  description = "AWS-Region"
  type        = string
  default     = "us-east-1"
}

# main.tf — Variable verwenden
provider "aws" {
  region = var.aws_region
}
```

### Ressourcen-Referenzen

Terraform ermittelt automatisch die Reihenfolge zum Erstellen von Ressourcen basierend auf Referenzen:

```hcl
# Dieser Bucket wird zuerst erstellt...
resource "aws_s3_bucket" "data" {
  bucket = "my-data-bucket"
}

# ...weil diese Ressource darauf verweist
resource "aws_glue_crawler" "my_crawler" {
  s3_target {
    path = "s3://${aws_s3_bucket.data.bucket}/raw/"
  }
}
```

### Tipps

- Fuhren Sie immer `terraform plan` vor `terraform apply` aus, um Anderungen zu uberprufen
- Fuhren Sie immer `terraform destroy` aus wenn Sie fertig sind, um Kosten zu vermeiden
- Fugen Sie `terraform.tfstate` und `.terraform/` zu `.gitignore` hinzu
- Verwenden Sie `force_destroy = true` bei S3-Buckets, damit sie auch wenn nicht leer geloscht werden konnen
- Verwenden Sie `random_id`-Ressourcen um eindeutige Bucket-Namenssuffixe zu generieren (S3-Bucket-Namen sind global eindeutig)

---

## Projektstruktur

```
module-3-project/
  README.md                              # Englische Version
  README_DE.md                           # Diese Datei (Deutsch)
  GEMINI.md                              # KI-Assistent-Kontext
  budget.md                              # Kostenvergleichsdokument
  data/
    seed/
      customers.csv                      # 200 synthetische Kunden
      accounts.csv                       # 500 synthetische Konten
      transactions.csv                   # 5.000 synthetische Transaktionen
  scripts/
    generate_seed_data.py                # Seed-Daten-Generator
  terraform/
    main.tf                              # Alle AWS-Ressourcendefinitionen
    variables.tf                         # Eingabevariablen
    outputs.tf                           # Exportierte Ressourcenwerte
    glue_scripts/
      etl_job.py                         # PySpark ETL-Skript fur Glue
  dbt_project/
    dbt_project.yml                      # dbt-Konfiguration
    profiles.yml                         # Athena-Verbindungskonfiguration
    models/
      sources.yml                        # Quellendefinitionen
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
    plans/                               # Design- und Implementierungsplane
```

---

## Referenzen

- [Terraform AWS Provider Dokumentation](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [AWS Glue Dokumentation](https://docs.aws.amazon.com/glue/)
- [Amazon Athena Dokumentation](https://docs.aws.amazon.com/athena/)
- [dbt Dokumentation](https://docs.getdbt.com/)
- [dbt-athena Adapter](https://github.com/dbt-athena/dbt-athena)
