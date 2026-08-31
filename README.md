# Airbnb End-to-End Data Engineering Project

## Overview
This project implements a complete **end-to-end data engineering pipeline** for Airbnb data using modern cloud technologies. It demonstrates best practices in data warehousing, transformation, and analytics using:

- Snowflake
- dbt (Data Build Tool)
- AWS S3
- Python

The pipeline processes Airbnb **listings, bookings, and hosts** data through a **Medallion Architecture (Bronze → Silver → Gold)** with:

- Incremental loading
- Slowly Changing Dimensions (SCD Type 2)
- Analytics-ready datasets

---

## Architecture

### Data Flow
```
CSV → AWS S3 → Snowflake Staging → Bronze → Silver → Gold → Analytics
```

| Layer | Purpose |
|------|--------|
Bronze | Raw ingested data |
Silver | Cleaned & validated |
Gold | Analytics-ready |

---

## Technology Stack

| Category | Tool |
|--------|------|
Data Warehouse | Snowflake |
Transformation | dbt |
Storage | AWS S3 |
Language | Python 3.12+ |
Version Control | Git |

### dbt Features Used
- Incremental models  
- Snapshots (SCD Type 2)  
- Custom macros  
- Jinja templating  
- Testing and documentation  

---

## Data Model

### Bronze Layer
Raw tables:
- `bronze_bookings`
- `bronze_hosts`
- `bronze_listings`

---

### Silver Layer
Cleaned tables:
- `silver_bookings`
- `silver_hosts`
- `silver_listings`

---

### Gold Layer
Analytics-ready tables:
- `fact`
- `obt (One Big Table)`
- Ephemeral intermediate models

---

### Snapshots (SCD Type 2)
Historical tracking tables:
- `dim_bookings`
- `dim_hosts`
- `dim_listings`

Tracks:
- Record history
- Valid timestamps
- Point-in-time analysis

---

## Project Structure
```
AWS_DBT_Snowflake/
│
├── README.md
├── pyproject.toml
├── main.py
│
├── SourceData/
│   ├── bookings.csv
│   ├── hosts.csv
│   └── listings.csv
│
├── DDL/
│   ├── ddl.sql
│   └── resources.sql
│
└── aws_dbt_snowflake_project/
    ├── dbt_project.yml
    ├── ExampleProfiles.yml
    │
    ├── models/
    │   ├── sources/
    │   ├── bronze/
    │   ├── silver/
    │   └── gold/
    │
    ├── macros/
    ├── analyses/
    ├── snapshots/
    ├── tests/
    └── seeds/
```

---

## Getting Started

### Prerequisites
- Snowflake account
- AWS account
- Python 3.12+

---

### Installation

#### Clone Repository
```bash
git clone <repo-url>
cd AWS_DBT_Snowflake
```

#### Create Virtual Environment
```bash
python -m venv .venv
.venv\Scripts\activate
```

#### Install Dependencies
```bash
pip install -r requirements.txt
```

---

### Configure Snowflake
Create file:

```
~/.dbt/profiles.yml
```

```yaml
aws_dbt_snowflake_project:
  outputs:
    dev:
      account: <account>
      database: AIRBNB
      password: <password>
      role: ACCOUNTADMIN
      schema: dbt_schema
      threads: 4
      type: snowflake
      user: <username>
      warehouse: COMPUTE_WH
  target: dev
```

---

### Create Tables
Run:
```
DDL/ddl.sql
```
inside Snowflake.

---

### Load Source Data
Upload CSV files into:

```
AIRBNB.STAGING
```

---

## dbt Commands

| Command | Purpose |
|--------|---------|
dbt debug | Test connection |
dbt deps | Install packages |
dbt run | Run models |
dbt test | Run tests |
dbt snapshot | Run SCD snapshots |
dbt docs serve | View docs |
dbt build | Run everything |

Run specific layer:
```bash
dbt run --select bronze.*
dbt run --select silver.*
dbt run --select gold.*
```

---

## Key Features

### Incremental Loading
```sql
{{ config(materialized='incremental') }}
{% if is_incremental() %}
WHERE CREATED_AT > (
 SELECT COALESCE(MAX(CREATED_AT),'1900-01-01')
 FROM {{ this }}
)
{% endif %}
```

---

### Custom Macro Example
```sql
{{ tag('CAST(PRICE_PER_NIGHT AS INT)') }}
```

Categorizes prices into:
- low
- medium
- high

---

### Schema Organization
| Layer | Schema |
|------|--------|
Bronze | AIRBNB.BRONZE |
Silver | AIRBNB.SILVER |
Gold | AIRBNB.GOLD |

---

## Data Quality

Testing includes:
- Unique key validation
- Not null checks
- Referential integrity
- Business rule tests

dbt automatically provides:
- Lineage graphs
- Dependency tracking
- Impact analysis

---

## Best Practices

### Security
- Never commit credentials
- Use environment variables
- Apply RBAC roles

### Performance
- Incremental models
- Ephemeral models
- Snowflake clustering

---

## Troubleshooting

**Connection Errors**
- Verify credentials
- Check warehouse state
- Run `dbt debug`

**Compilation Errors**
- Validate Jinja syntax
- Check dependencies

**Incremental Issues**
```bash
dbt run --full-refresh
```

---

## Future Enhancements
- Data quality dashboards  
- CI/CD pipeline  
- BI integration  
- Monitoring & alerting  
- Data masking for PII  
- Advanced testing suite  

---

## Author
**Mahadevu M P**  
Data Engineering Portfolio Project  

Technologies:
```
Snowflake | dbt | AWS | Python
```
