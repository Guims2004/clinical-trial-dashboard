# Clinical Trial Compliance & Monitoring Dashboard

**Developer:** Olivia Ngueguim  
**Target Audience:** Institutional Review Board (IRB) Directors, Research Ethics Committees, University Research Administrators  

## 1. Project Overview

This project proposes the development of an interactive clinical trial compliance dashboard designed to support monitoring of FDA related reporting and transparency requirements for
clinical studies. Clinical trials involving human participants must follow strict ethical and regulatory standards established by organizations such as the FDA and Institutional Review Boards (IRBs). 
Many studies are required to regularly report:
• Recruitment status
• Enrollment information
• Protocol updates
• Safety-related information
Although this data is publicly available through the ClinicalTrials.gov API, it is often difficult to analyze quickly because the information exists in large raw datasets.
This project aims to build a centralized data engineering pipeline and dashboard that automatically collects, cleans, and visualizes clinical trial compliance data.

The dashboard helps users:
• Monitor clinical trial reporting activity
• Identify studies with delayed updates
• Track recruitment and enrollment trends
• Support faster compliance monitoring and oversight
The main problem is the lack of an automated system that transforms public clinical trial API data into clear operational compliance insights.
This project addresses that problem by creating an automated ETL pipeline and interactive dashboard for monitoring FDA-related clinical trial reporting activity.

The system integrates:
- Data extraction from structured datasets (ClinicalTrials.gov)
- ETL processing and cleaning using Python
- A real time interactive dashboard built with Dash and Plotly


## 2. Problem Statement

Clinical trial data is publicly available but difficult to interpret due to:
- Large and complex raw datasets
- Inconsistent formatting across sources
- Lack of centralized monitoring tools

This project solves this by building an automated system that:
- Cleans and structures clinical trial data
- Tracks compliance and recruitment activity
- Visualizes trial distribution and sponsor activity
- Enables drill down inspection of individual studies


## 3. Technology Stack

- Python
- Dash (Plotly Dash)
- Dash Bootstrap Components
- Pandas
- Plotly Express
- ClinicalTrials.gov-style structured datasets (CSV-based ETL output)

## The ERD is found in the Screenshot documents

## 4. System Architecture (ETL Pipeline)

### 4.1 Data Sources
-ClinicalTrials.gov

The system uses clinical trial datasets stored locally:
- `trials.csv`
- `enrollment.csv`
- `sponsors.csv`
- `locations.csv`

### 4.2 ETL Process
#### Extract
- Load CSV datasets from the `/output` directory
- Simulated structured ingestion pipeline

#### Transform
- Merge datasets using:
- `nct_id` (clinical trial identifier)
- `sponsor_id` (organization reference)

Data cleaning operations:
- Remove duplicates
- Handle missing values
- Normalize enrollment fields
- Standardize sponsor classification
- Assign U.S. state mapping for geographic visualization

#### Load
- Processed dataset stored in memory for dashboard rendering
- Used directly as the analytical data layer for visualizations


## 5. Dashboard Features

Interactive filtering by:
- Recruitment status
- Sponsor class
- Enrollment scale


### 5.1 Geographic Analysis (Map Visualization)

- U.S. choropleth map (Plotly)
- Displays trial distribution by state
- Click to filter interaction enabled
- Reset button clears selection

### 5.2 Sponsor Analysis

- Donut chart showing enrollment distribution by sponsor class
- Highlights dominance of sponsor categories


### 5.3 Master Trial Ledger

Interactive table showing:
- Protocol ID (NCT ID)
- Study title
- Recruitment status

### 5.4 Drilldown Inspection Panel

Displays full clinical trial profile:
- Enrollment count and scale tier
- Sponsor name and classification
- Recruitment status


## 6. Data Engineering Design

### Key Transformations
- Flattening merged datasets into analytical structure
- Deduplication of clinical trial records
- Synthetic geographic distribution mapping (state-level balancing)
- Missing value handling with safe defaults

### Business Logic Layer
- Enrollment aggregation
- Sponsor classification grouping
- Geographic filtering logic
- State-based segmentation engine


## 7. Database Design (Conceptual Model)

Although this project is implemented using Pandas and CSV files, it is designed around a normalized relational database structure to ensure scalability and data integrity.

The **Sponsors entity** stores information about organizations funding clinical trials, with each sponsor uniquely identified and classified by type (e.g., industry or NIH). Each sponsor can fund multiple clinical trials, establishing a one-to-many relationship with the Clinical Trials entity.

The **Clinical Trials entity** contains the core study metadata, including the unique `nct_id`, title, recruitment status, sponsor reference, and study dates. Each trial is linked to one sponsor but can generate multiple related records in other tables.

The **Locations entity** stores geographic information such as facility name, city, state, and country, enabling spatial analysis of where trials are conducted.

The **Enrollment Metrics entity** tracks participant counts and enrollment scale for each trial, linked through `nct_id`, supporting performance and compliance monitoring.

Finally, a junction structure between Clinical Trials and Locations resolves the many-to-many relationship, allowing each trial to occur at multiple sites while each site can host multiple trials.

Overall, the model follows standard relational design principles, ensuring clean data organization, reduced redundancy, and future compatibility with relational database systems such as PostgreSQL.


## 8. Key Outcomes

This system delivers:
- Automated clinical trial data processing pipeline
- Clean and structured analytical dataset
- Interactive compliance monitoring dashboard
- Geographic visualization of trial distribution
- Sponsor-level analytics
- Drill-down inspection system for individual trials


## 9. Project Value

This project demonstrates:
- Data engineering (ETL pipeline design)
- Dashboard development (Dash + Plotly)
- Healthcare analytics modeling
- Compliance monitoring logic design
- Full-stack Python data application development

## 9. Challenges

### Power BI Integration
I initially planned to use Power BI for the dashboard, but I experienced difficulties connecting and working with the data. As a result, I decided to use Dash and Plotly, which provided greater flexibility for development.

### Complex Dataset
The ClinicalTrials.gov data is large and complex. To simplify data processing and dashboard development, I limited the project to approximately 50 clinical trials.

### ERD Modifications
My original ERD included the number of deaths per clinical trial. However, due to data availability and implementation challenges, this feature was removed from the final design.

### Time Constraints
Limited project time required focusing on the core ETL pipeline and dashboard functionality. Some planned features were postponed for future development.

## Future Improvements

Future versions of the dashboard could include:

- Integration with the ClinicalTrials.gov API for real-time updates.
- Analysis of a larger clinical trial dataset.
- Additional variables such as adverse events and study outcomes.
- Automated compliance alerts and notifications.
- Storage using a relational database such as PostgreSQL.
- More advanced filtering and dashboard visualizations.
