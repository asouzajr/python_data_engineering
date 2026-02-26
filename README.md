# Python Data Engineering Pipeline – JIRA SLA

## 1. Overview

This project implements a structured Data Engineering pipeline in Python based on the Medallion Architecture (Bronze and Silver layers).

The primary objective is to ingest raw JIRA issue data, preserve its original structure, and transform it into a clean, structured dataset prepared for business rule application in the Gold layer (SLA calculation – upcoming phase).

The implementation follows engineering best practices, including:

- ISO 8601 timestamp standardization (UTC)
- Structured logging
- Environment variable configuration
- Explicit structural validation between layers
- Modular execution using `python -m`
- Clear separation of responsibilities per layer

---

## 2. Architecture

The pipeline follows the Medallion Architecture pattern:

Raw JSON → Bronze → Silver → Gold (planned)

Each layer has clearly defined responsibilities and validation boundaries.

---

## 2.1 Bronze Layer – Raw Ingestion

### Responsibilities

- Read raw JSON input
- Preserve the original data structure
- Add ingestion metadata
- Persist data locally
- Log execution steps
- Validate file existence before ingestion

### Characteristics

- Raw payload stored under `raw_data`
- Metadata stored separately
- Ingestion timestamp in ISO 8601 UTC format
- No transformation applied
- Structured logging enabled
- Fail-fast behavior for missing files

### Output

```
data/bronze/bronze_jira_issues.json
```

### Bronze File Structure

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

## 2.2 Silver Layer – Data Cleaning and Structuring

### Responsibilities

- Read Bronze data
- Validate Bronze structural integrity
- Normalize nested JSON structures
- Explode nested lists
- Extract relevant business fields
- Convert timestamps to UTC datetime
- Remove invalid records
- Persist structured dataset in Parquet format
- Log transformation lifecycle

### Structural Validation

Before transformation, the Silver layer validates that:

- `raw_data` exists
- `raw_data.issues` exists

If the structure is invalid, execution fails explicitly with a descriptive error.

This prevents silent corruption between layers.

### Transformations Applied

- `assignee` list exploded
- `timestamps` list exploded
- Extraction of:
  - assignee_name
  - created_at
  - resolved_at
- Column renaming (`id` → `issue_id`)
- Datetime conversion using `pd.to_datetime(..., utc=True)`
- Removal of records with invalid `created_at`
- Explicit logging of record counts

### Output

```
data/silver/silver_issues.parquet
```

### Silver Schema

| Column        | Description                              |
|---------------|------------------------------------------|
| issue_id      | Unique issue identifier                  |
| issue_type    | Issue type                               |
| priority      | Issue priority                           |
| status        | Current issue status                     |
| assignee_name | Assigned analyst                         |
| created_at    | Issue creation timestamp (UTC)           |
| resolved_at   | Issue resolution timestamp (UTC)         |

---

## 3. Environment Configuration

The project supports environment variables via a `.env` file located at the project root.

Example:

```
JIRA_INPUT_PATH=resources/jira_issues_raw.json
JIRA_BRONZE_OUTPUT_PATH=data/bronze/bronze_jira_issues.json
JIRA_SILVER_OUTPUT_PATH=data/silver/silver_issues.parquet
LOG_LEVEL=INFO
```

The `.env` file is excluded from version control for security and portability reasons.

---

## 4. How to Execute

All commands must be executed from the project root directory.

### 4.1 Create Virtual Environment

Linux / macOS:

```bash
python -m venv venv
source venv/bin/activate
```

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

---

### 4.2 Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4.3 Execute Bronze Layer

```bash
python -m src.bronze.ingest_bronze
```

---

### 4.4 Execute Silver Layer

```bash
python -m src.silver.transform_silver
```

Execution via `-m` ensures proper package resolution and architectural consistency.

---

## 5. Technical Standards

### 5.1 Timestamp Standard

All timestamps follow ISO 8601 with explicit UTC designation:

```
YYYY-MM-DDTHH:MM:SSZ
```

Example:

```
2026-02-23T19:03:00Z
```

All Silver timestamps are timezone-aware and standardized to UTC.

---

### 5.2 Logging

Logging is structured and formatted to ensure traceability and observability of pipeline execution.

Example log entry:

```
2026-02-23T19:03:53 - INFO - Starting Silver layer transformation...
```

Each layer logs:

- Start of execution
- Record counts
- Structural validation results
- Output persistence confirmation

---

### 5.3 Error Handling Strategy

The pipeline follows a fail-fast principle:

- Missing files raise explicit exceptions
- Invalid Bronze structure raises `KeyError`
- Invalid datetime values are coerced and filtered

This prevents silent data corruption across layers.

---

## 6. Engineering Decisions

### 6.1 Medallion Architecture

The Medallion Architecture was selected to clearly separate responsibilities:

- Bronze: Raw ingestion and immutability
- Silver: Data cleansing, structuring, and schema enforcement
- Gold: Business logic and SLA calculation (planned)

This separation improves maintainability, traceability, and scalability.

---

### 6.2 Structural Validation Between Layers

The Silver layer explicitly validates Bronze structure before transformation.

This ensures:

- Layer isolation
- Strong contracts between layers
- Safer pipeline evolution

---

### 6.3 Metadata in Bronze Layer

Metadata was introduced at the Bronze layer to:

- Track ingestion timestamp
- Preserve lineage information
- Improve observability

This ensures traceability without altering raw business data.

---

### 6.4 UTC Standardization

All timestamps are converted to UTC to eliminate timezone inconsistencies and ensure deterministic SLA calculations in the future Gold layer.

---

### 6.5 Parquet in Silver Layer

Parquet was selected for the Silver output because:

- It is columnar and efficient
- It enforces schema consistency
- It is analytics-friendly
- It reduces storage footprint compared to raw JSON

---

### 6.6 Modular Execution Pattern

The project enforces execution via:

```bash
python -m package.module
```

This ensures:

- Proper package resolution
- Import consistency
- Avoidance of `ModuleNotFoundError`
- Architectural discipline

---

## 7. Trade-offs

### 7.1 Local Persistence

The project persists data locally instead of using cloud storage or databases.

**Trade-off:**

- Simpler setup  
- Reduced infrastructure complexity  
- Not horizontally scalable  

---

### 7.2 Pandas-Based Transformation

Pandas was chosen for transformation logic due to its simplicity and expressiveness.

**Trade-off:**

- Excellent for moderate datasets  
- Not distributed  
- Would require migration to Spark for large-scale processing  

---

### 7.3 Fail-Fast Error Handling

The pipeline stops execution on structural inconsistencies.

**Trade-off:**

- Safer data guarantees  
- Slightly stricter development process  

---

## 8. Future Improvements

Planned enhancements include:

- Gold layer implementation (SLA calculation)
- Business hour calculation excluding weekends
- Integration with Brazilian public holiday API
- Aggregated reporting layer
- Automated validation test suite
- CI pipeline with linting and formatting checks

---

## 9. Project Structure

```
python_data_engineering/
│
├── src/
│   ├── bronze/
│   │   └── ingest_bronze.py
│   ├── silver/
│   │   └── transform_silver.py
│   └── utils/
│       └── env_loader.py
│
├── data/
│   ├── bronze/
│   └── silver/
│
├── resources/
├── .env
├── requirements.txt
└── README.md
```

---

## 10. Current Status

- Bronze layer implemented and standardized
- Silver layer implemented with structural validation
- Logging standardized
- Modular execution enforced
- Linting applied
- Gold layer (SLA calculation and reporting) planned

---

## 11. Conclusion

This project demonstrates:

- Structured data ingestion
- Controlled data transformation
- Explicit inter-layer validation
- Layered architecture design
- Configuration management via environment variables
- Logging and operational transparency
- Clean code discipline (PEP8 / linting)

The next phase will introduce SLA calculation logic and business metrics aggregation within the Gold layer.
