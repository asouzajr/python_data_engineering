# Python Data Engineering Pipeline – JIRA SLA

## 1. Overview

This project implements a structured Data Engineering pipeline in Python following the Medallion Architecture pattern (Bronze → Silver → Gold).

The pipeline ingests raw JIRA issue data, preserves the original structure, transforms it into a structured dataset, and applies SLA business rules considering:

- Business days only
- Exclusion of weekends
- Exclusion of Brazilian national holidays (via public API)
- SLA thresholds based on issue priority

The project demonstrates production-oriented engineering practices:

- Layered architecture (Bronze / Silver / Gold)
- Explicit structural validation between layers
- Fail-fast error handling
- Structured logging
- Environment-based configuration
- API consumption
- Parquet intermediate storage
- CSV analytical outputs
- Modular execution using `python -m`

---

## 2. Architecture

Raw JSON → Bronze → Silver → Gold

Each layer has a clearly defined responsibility and validation boundary.

---

## 3. Layer Responsibilities

### 3.1 Bronze Layer – Raw Ingestion

Responsibilities:

- Read raw JSON input
- Preserve original payload
- Add ingestion metadata
- Validate file existence
- Persist locally
- Log execution lifecycle

Characteristics:

- No transformation applied
- Raw payload stored under `raw_data`
- Metadata stored separately
- ISO 8601 UTC ingestion timestamp
- Fail-fast behavior for missing files

Output:

```
data/bronze/bronze_jira_issues.json
```

Bronze structure:

```json
{
  "metadata": {
    "ingested_at": "2026-02-23T19:03:00Z",
    "source": "local_json_file"
  },
  "raw_data": {
    "issues": [...]
  }
}
```

---

### 3.2 Silver Layer – Data Cleaning and Structuring

Responsibilities:

- Read Bronze data
- Validate Bronze structure
- Normalize nested JSON
- Explode nested lists
- Extract relevant business fields
- Convert timestamps to UTC
- Remove invalid records
- Persist as Parquet

Structural validation:

- `raw_data` must exist
- `raw_data.issues` must exist

Transformations applied:

- Extract `issue_id`
- Extract `issue_type`
- Extract `priority`
- Extract `status`
- Extract `assignee_name`
- Extract `created_at`
- Extract `resolved_at`
- Convert timestamps using `pd.to_datetime(..., utc=True)`
- Remove invalid datetime records

Output:

```
data/silver/silver_issues.parquet
```

Silver schema:

- issue_id
- issue_type
- priority
- status
- assignee_name
- created_at (UTC)
- resolved_at (UTC)

---

### 3.3 Gold Layer – SLA Calculation and Reporting

Responsibilities:

- Read Silver dataset
- Filter completed issues (Done, Resolved)
- Calculate resolution time in business hours
- Determine expected SLA by priority
- Check if SLA was met
- Generate aggregated reports
- Persist outputs as CSV

---

## 4. SLA Rules

| Priority | Expected SLA |
|-----------|--------------|
| High      | 24 hours     |
| Medium    | 72 hours     |
| Low       | 120 hours    |

The SLA calculation considers:

- Only business days
- Exclusion of weekends
- Exclusion of Brazilian national holidays

---

## 5. Holiday API

Brazilian national holidays are retrieved using a public API:

```
https://brasilapi.com.br/api/feriados/v1/{year}
```

The API is consumed dynamically during SLA calculation to ensure up-to-date holiday validation.

---

## 6. Gold Output

### 6.1 Final SLA Table

File:

```
data/gold/gold_sla_issues.csv
```

Columns:

- issue_id
- issue_type
- assignee_name
- priority
- created_at
- resolved_at
- resolution_hours
- sla_expected_hours
- is_sla_met

Only issues with status **Done** or **Resolved** are included.

---

### 6.2 Aggregated Reports (Required)

#### SLA Average by Analyst

```
data/gold/gold_sla_by_analyst.csv
```

Columns:

- assignee_name
- total_issues
- avg_sla_hours

---

#### SLA Average by Issue Type

```
data/gold/gold_sla_by_issue_type.csv
```

Columns:

- issue_type
- total_issues
- avg_sla_hours

---

## 7. Environment Configuration

The project uses a `.env` file at the project root.

Example:

```
JIRA_INPUT_PATH=resources/jira_issues_raw.json
JIRA_BRONZE_OUTPUT_PATH=data/bronze/bronze_jira_issues.json
JIRA_SILVER_OUTPUT_PATH=data/silver/silver_issues.parquet
JIRA_GOLD_OUTPUT_PATH=data/gold/gold_sla_issues.csv
JIRA_GOLD_ANALYST_REPORT_PATH=data/gold/gold_sla_by_analyst.csv
JIRA_GOLD_TYPE_REPORT_PATH=data/gold/gold_sla_by_issue_type.csv
LOG_LEVEL=INFO
```

`.env` is excluded from version control.

---

## 8. Setup Instructions

All commands must be executed from the project root.

### 8.1 Create Virtual Environment

Linux / macOS:

```bash
python3 -m venv venv
source venv/bin/activate
```

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

---

### 8.2 Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

Required direct dependencies:

- pandas
- numpy
- pyarrow
- requests
- python-dotenv

---

## 9. Execution

Bronze:

```bash
python -m src.bronze.ingest_bronze
```

Silver:

```bash
python -m src.silver.transform_silver
```

Gold:

```bash
python -m src.gold.build_gold
```

Execution via `-m` ensures proper package resolution and architectural consistency.

---

## 10. Technical Standards

### Timestamp Standard

All timestamps follow ISO 8601 UTC:

YYYY-MM-DDTHH:MM:SSZ

All datetime objects are timezone-aware.

---

### Logging

Structured logging provides traceability across layers.

Each layer logs:

- Execution start
- Structural validation
- Record counts
- Output persistence confirmation

---

### Error Handling

The pipeline follows a fail-fast principle:

- Missing files raise explicit exceptions
- Invalid Bronze structure raises errors
- Invalid datetime values are coerced and filtered

No silent data corruption is allowed.

---

## 11. Engineering Decisions

### Medallion Architecture

Chosen to ensure:

- Clear responsibility separation
- Traceability
- Maintainability
- Layer isolation

---

### Parquet in Silver

Benefits:

- Columnar storage
- Schema consistency
- Analytics efficiency
- Reduced storage footprint

---

### CSV in Gold

Chosen for:

- Business-friendly consumption
- Simplicity
- Easy integration with BI tools

---

### API-Based Holiday Validation

Ensures:

- Up-to-date national holiday data
- Real-world API integration
- Dynamic SLA validation

---

## 12. Project Structure

```
python_data_engineering/
│
├── src/
│   ├── bronze/
│   │   └── ingest_bronze.py
│   ├── silver/
│   │   └── transform_silver.py
│   ├── gold/
│   │   ├── build_gold.py
│   │   └── sla_calculation.py
│   └── utils/
│       └── env_loader.py
│
├── data/
│   ├── bronze/
│   ├── silver/
│   └── gold/
│
├── resources/
├── .env
├── requirements.txt
└── README.md
```

---

## 13. Current Status

- Bronze layer implemented
- Silver layer implemented with structural validation
- Gold layer implemented with SLA calculation
- Public holiday API integration
- Aggregated reports generated
- Logging standardized
- Environment-driven configuration
- Modular architecture enforced

---

## 14. Conclusion

This project demonstrates:

- Structured data ingestion
- Controlled transformation pipeline
- Business rule implementation (SLA)
- API integration
- Analytical reporting
- Clean architectural separation
- Production-oriented engineering discipline

It reflects practical Data Engineering principles using Python and Medallion Architecture.
