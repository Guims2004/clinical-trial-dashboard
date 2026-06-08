# clinical-trial-dashboard
Clinical Trial Compliance Monitoring Dashboard using Python, PostgreSQL, Dash and Plotly.

# Clinical Trials ETL Pipeline
## Overview
This project builds a full ETL pipeline using Python to extract clinical trials data from the ClinicalTrials.gov API, transform and clean the data, validate it, and load it into a PostgreSQL database for analytics use.

## Features
- API data extraction with pagination support
- Data cleaning and normalization
- Derived metrics (enrollment tiers)
- Data validation checks (nulls, duplicates, negative values)
- Relational database design (4 tables)
- CSV export for Power BI / Tableau
- Logging and error handling

## Database Schema

### Tables
- sponsors (dimension table)
- clinical_trials (fact table)
- locations (dimension table)
- enrollment_metrics (fact table)

## Tech Stack
- Python
- Pandas
- SQLAlchemy
- PostgreSQL
- Requests API


