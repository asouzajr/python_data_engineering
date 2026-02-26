# Validation Utilities – JIRA Data Pipeline

## 1. Overview

This directory contains validation utilities designed to inspect and debug the Bronze and Silver layers of the JIRA Data Engineering pipeline.

These scripts are intended for:

- Structural inspection
- Schema verification
- Record-level investigation
- Debugging transformation behavior
- Ensuring consistency between layers

Validation scripts are not part of the production pipeline.  
They are diagnostic tools used during development and analysis.

---

## 2. Objectives

The validation layer provides:

- Transparent inspection of raw and structured data
- Controlled filtering by `issue_id`
- Visibility into schema and data types
- Inspection of null values
- Record-level comparison between layers

This improves:

- Observability
- Debugging efficiency
- Confidence in transformation logic

---

## 3. Bronze Validation

### Responsibilities

- Inspect Bronze file structure
- Display metadata
- Show total issue count
- Filter by specific `issue_id`
- Display full JSON payload for targeted issue

### Capabilities

- Shows root-level keys
- Displays ingestion timestamp
- Counts total issues
- Allows CLI parameter input
- Supports interactive mode when no parameter is passed

### Execution

From the project root:

```bash
python validation/validate_bronze_issue.py JIRA-1000
```

Or interactive mode:

```bash
python validation/validate_bronze_issue.py
```

---

## 4. Silver Validation

### Responsibilities

- Inspect Silver dataset structure
- Display schema and data types
- Analyze timezone awareness
- Count null values per column
- Filter by `issue_id`
- Display structured records

### Capabilities

- Shows total record count
- Displays total column count
- Prints column data types
- Identifies UTC-aware datetime columns
- Provides filtered record inspection
- Supports CLI parameter input
- Supports interactive mode

### Execution

From the project root:

```bash
python validation/validate_silver.py JIRA-1000
```

Or interactive mode:

```bash
python validation/validate_silver.py
```

---

## 5. Validation Philosophy

The validation scripts follow these principles:

### 5.1 Read-Only Behavior

Validation scripts:

- Do not modify data
- Do not persist outputs
- Do not alter pipeline state

They are strictly observational.

---

### 5.2 Targeted Inspection

Allowing filtering by `issue_id` enables:

- Focused debugging
- Cross-layer comparison (Bronze vs Silver)
- Transformation traceability
- Verification of explode logic
- Verification of datetime conversion

---

### 5.3 CLI-Based Design

Validation utilities accept parameters via command-line arguments:

```
python script.py <issue_id>
```

If no parameter is provided, scripts may prompt for input interactively.

This provides flexibility without adding complexity.

---

## 6. Engineering Rationale

Validation utilities are separated from production pipeline code to:

- Maintain clean architectural boundaries
- Avoid mixing debugging logic with transformation logic
- Preserve production code simplicity
- Improve maintainability

This separation aligns with professional data engineering practices.

---

## 7. Future Enhancements

Potential improvements for this validation layer include:

- Automated schema validation tests
- Bronze vs Silver automated comparison tool
- Data quality checks (null thresholds, duplication checks)
- CLI argument parsing using `argparse`
- Integration into CI pipeline
- Structured output formatting

---

## 8. Directory Structure

```
validation/
│
├── validate_bronze_issue.py
├── validate_silver.py
└── VALIDATION.md
```

---

## 9. Current Status

- Bronze validation implemented
- Silver validation implemented
- CLI parameter support enabled
- Interactive fallback mode supported

These tools enhance transparency and improve confidence in the pipeline's correctness.
