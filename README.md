# Python Data Engineering Pipeline – JIRA SLA

## 1. Overview

This project implements a structured Data Engineering pipeline in Python based on the Medallion Architecture (Bronze and Silver layers).

The primary objective is to ingest raw JIRA issue data, preserve its original structure, and transform it into a clean, structured dataset prepared for business rule application in the Gold layer (SLA calculation – upcoming phase).

The implementation follows engineering best practices, including:

- ISO 8601 timestamp standardization (UTC)
- Structured logging
- Environment variable configuration
- Modular execution using `python -m`
- Clear separation of responsibilities per layer

---

## 2. Architecture

The pipeline follows the Medallion Architecture pattern:

Raw JSON → Bronze → Silver → Gold (planned)

### 2.1 Bronze Layer – Raw Ingestion

#### Responsibilities

- Read raw JSON input
- Preserve the original data structure
- Add ingestion metadata
- Persist data locally

#### Characteristics

- Raw payload stored under `raw_data`
- Metadata stored separately
- Ingestion timestamp in ISO 8601 UTC format
- No transformation applied
- Structured logging enabled

#### Output

```
data/bronze/bronze_jira_issues.json
```

#### Bronze File Structure

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

### 2.2 Silver Layer – Data Cleaning and Structuring

#### Responsibilities

- Read Bronze data
- Normalize nested JSON structures
- Explode nested lists
- Extract relevant business fields
- Convert timestamps to UTC datetime
- Remove invalid records
- Persist structured dataset

#### Transformations Applied

- `assignee` list exploded
- `timestamps` list exploded
- Extraction of:
  - assignee name
  - created_at
  - resolved_at
- Datetime conversion using UTC
- Removal of records with invalid `created_at`

#### Output

```
data/silver/silver_issues.parquet
```

#### Silver Schema

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

---

### 5.2 Logging

Logging is structured and formatted to ensure traceability and observability of pipeline execution.

Example log entry:

```
2026-02-23T19:03:53 - INFO - Starting Silver layer transformation...
```

---

### 5.3 Modular Execution

Modules are executed using:

```bash
python -m package.module
```

This approach ensures proper package resolution and maintains architectural consistency.

---

## 6. Engineering Decisions

### 6.1 Medallion Architecture

The Medallion Architecture was selected to clearly separate responsibilities:

- Bronze: Raw ingestion and immutability
- Silver: Data cleansing and structuring
- Gold: Business logic and SLA calculation (planned)

This separation improves maintainability, traceability, and scalability.

---

### 6.2 Metadata in Bronze Layer

Metadata was introduced at the Bronze layer to:

- Track ingestion timestamp
- Preserve lineage information
- Improve observability

This ensures traceability without altering raw business data.

---

### 6.3 UTC Standardization

All timestamps are converted to UTC to eliminate timezone inconsistencies and ensure deterministic SLA calculations in the future Gold layer.

---

### 6.4 Parquet in Silver Layer

Parquet was selected for the Silver output because:

- It is columnar and efficient
- It supports schema consistency
- It is analytics-friendly
- It reduces storage footprint compared to raw JSON

---

### 6.5 Environment Variables

Configuration values are externalized via `.env` to:

- Decouple configuration from code
- Improve portability across environments
- Enable flexible deployment scenarios

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
- Would need migration to Spark for large-scale processing  

---

### 7.3 Minimal Dependency Strategy

Standard library was prioritized when possible.

**Trade-off:**  
- Reduces dependency overhead  
- Slightly more manual implementation effort  

---

## 8. Future Improvements

Planned enhancements include:

- Gold layer implementation (SLA calculation)
- Business hour calculation excluding weekends
- Integration with Brazilian public holiday API
- Aggregated reporting layer
- Automated validation tests
- Structured logging with file handlers

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

- Bronze layer implemented
- Silver layer implemented
- Gold layer (SLA calculation and reporting) planned

---

## 11. Conclusion

This project demonstrates:

- Structured data ingestion
- Controlled data transformation
- Layered architecture design
- Configuration management via environment variables
- Logging and operational transparency

The next phase will introduce SLA calculation logic and business metrics aggregation within the Gold layer.
