# =====================================================
# ETL PIPELINE - CLINICAL TRIALS DATA
# =====================================================

import os
import json
import logging
import requests
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# =====================================================
# CONFIG
# =====================================================
BASE_URL = "https://clinicaltrials.gov/api/v2/studies"

DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "Admin")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "6053")
DB_NAME = os.getenv("DB_NAME", "clinical_db")

DB_URL = (
    f"postgresql://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# =====================================================
# LOGGING
# =====================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("etl_pipeline.log"),
        logging.StreamHandler()
    ]
)

# =====================================================
# EXTRACT
# =====================================================

def extract_data():
    logging.info("EXTRACT START")

    params = {
        "pageSize": 50,
        "query.term": "cancer"
    }

    try:
        response = requests.get(BASE_URL, params=params, timeout=30)
        response.raise_for_status()

        data = response.json()
        studies = data.get("studies", [])

        if not studies:
            raise ValueError("No studies returned from API")

        os.makedirs("data", exist_ok=True)

        with open("data/raw.json", "w", encoding="utf-8") as f:
            json.dump(studies, f, indent=2)

        logging.info(f"Extracted {len(studies)} records")
        return studies

    except Exception as e:
        logging.error(f"Extraction failed: {e}")
        raise

# =====================================================
# TRANSFORM
# =====================================================

def transform_data(studies):

    logging.info("TRANSFORM START")

    sponsors = []
    trials = []
    locations = []
    enrollment = []

    sponsor_lookup = {}
    sponsor_id = 1

    location_set = set()

    for study in studies:

        try:
            protocol = study.get("protocolSection", {})

            identification = protocol.get("identificationModule", {})
            status = protocol.get("statusModule", {})
            sponsor_module = protocol.get("sponsorCollaboratorsModule", {})
            design = protocol.get("designModule", {})
            loc_module = protocol.get("contactsLocationsModule", {})

            nct_id = identification.get("nctId")
            if not nct_id:
                continue

            # =========================
            # SPONSOR (DIM TABLE)
            # =========================
            sponsor_info = sponsor_module.get("leadSponsor", {})
            sponsor_name = sponsor_info.get("name", "UNKNOWN").strip()
            sponsor_class = sponsor_info.get("class", "OTHER")

            if sponsor_name not in sponsor_lookup:
                sponsor_lookup[sponsor_name] = sponsor_id

                sponsors.append({
                    "sponsor_id": sponsor_id,
                    "sponsor_name": sponsor_name,
                    "sponsor_class": sponsor_class
                })

                sponsor_id += 1

            sid = sponsor_lookup[sponsor_name]

            # =========================
            # TRIALS (FACT TABLE)
            # =========================
            trials.append({
                "nct_id": nct_id,
                "title": identification.get("officialTitle")
                         or identification.get("briefTitle")
                         or "Untitled",
                "recruitment_status": status.get("overallStatus", "UNKNOWN"),
                "sponsor_id": sid,
                "start_date": status.get("startDateStruct", {}).get("date"),
                "completion_date": status.get("primaryCompletionDateStruct", {}).get("date")
            })

            # =========================
            # ENROLLMENT (FACT TABLE)
            # =========================
            enroll_info = design.get("enrollmentInfo", {})
            count = enroll_info.get("count", 0)

            try:
                count = int(count)
            except:
                count = 0

            if count < 0:
                count = 0

            tier = (
                "Small" if count < 50 else
                "Medium" if count <= 300 else
                "Large"
            )

            enrollment.append({
                "nct_id": nct_id,
                "enrollment_count": count,
                "scale_tier": tier
            })

            # =========================
            # LOCATIONS (DIM TABLE)
            # =========================
            locs = loc_module.get("locations", []) or []

            if not locs:
                locs = [{
                    "facility": "Not Provided",
                    "city": None,
                    "state": None,
                    "country": None
                }]

            for loc in locs:
                facility = loc.get("facility", "Unknown")
                city = loc.get("city")
                state = loc.get("state")
                country = loc.get("country")

                key = f"{facility}_{city}_{state}_{country}"

                if key not in location_set:
                    location_set.add(key)

                    locations.append({
                        "facility_name": facility,
                        "city": city,
                        "state": state,
                        "country": country
                    })

        except Exception as e:
            logging.warning(f"Skipped record due to error: {e}")

    # DATAFRAMES
    trials_df = pd.DataFrame(trials).drop_duplicates()
    sponsors_df = pd.DataFrame(sponsors).drop_duplicates()
    locations_df = pd.DataFrame(locations).drop_duplicates()
    enrollment_df = pd.DataFrame(enrollment).drop_duplicates()

    logging.info("TRANSFORM COMPLETE")

    return trials_df, sponsors_df, locations_df, enrollment_df

# =====================================================
# VALIDATION
# =====================================================

def validate_data(trials_df, sponsors_df, locations_df, enrollment_df):

    logging.info("VALIDATION START")

    assert not trials_df.empty, "Trials empty"
    assert not sponsors_df.empty, "Sponsors empty"

    assert trials_df["nct_id"].notnull().all(), "Null NCT IDs found"
    assert not trials_df["nct_id"].duplicated().any(), "Duplicate NCT IDs"

    assert (enrollment_df["enrollment_count"] >= 0).all(), "Negative enrollment found"

    logging.info("VALIDATION PASSED")

# =====================================================
# LOAD (WITH INCREMENTAL LOGIC)
# =====================================================

def load_data(trials_df, sponsors_df, locations_df, enrollment_df):

    logging.info("LOAD START")

    engine = create_engine(DB_URL)

    try:
        with engine.begin() as conn:

            # =========================
            # TABLES (4 TABLES REQUIRED)
            # =========================

            conn.execute(text("""
            CREATE TABLE IF NOT EXISTS sponsors (
                sponsor_id INT PRIMARY KEY,
                sponsor_name TEXT UNIQUE,
                sponsor_class TEXT
            );
            """))

            conn.execute(text("""
            CREATE TABLE IF NOT EXISTS clinical_trials (
                nct_id TEXT PRIMARY KEY,
                title TEXT,
                recruitment_status TEXT,
                sponsor_id INT,
                start_date TEXT,
                completion_date TEXT
            );
            """))

            conn.execute(text("""
            CREATE TABLE IF NOT EXISTS locations (
                location_id SERIAL PRIMARY KEY,
                facility_name TEXT,
                city TEXT,
                state TEXT,
                country TEXT
            );
            """))

            conn.execute(text("""
            CREATE TABLE IF NOT EXISTS enrollment_metrics (
                nct_id TEXT PRIMARY KEY,
                enrollment_count INT,
                scale_tier TEXT
            );
            """))

            # =========================
            # INCREMENTAL STRATEGY
            # =========================
            # Remove duplicates before insert (simple safe ETL approach)

            sponsors_df = sponsors_df.drop_duplicates(subset=["sponsor_id"])
            trials_df = trials_df.drop_duplicates(subset=["nct_id"])
            enrollment_df = enrollment_df.drop_duplicates(subset=["nct_id"])
            locations_df = locations_df.drop_duplicates()

            # =========================
            # LOAD
            # =========================

            sponsors_df.to_sql("sponsors", conn, if_exists="append", index=False, method="multi")
            trials_df.to_sql("clinical_trials", conn, if_exists="append", index=False, method="multi")
            locations_df.to_sql("locations", conn, if_exists="append", index=False, method="multi")
            enrollment_df.to_sql("enrollment_metrics", conn, if_exists="append", index=False, method="multi")

        logging.info("LOAD COMPLETE")

    except SQLAlchemyError as e:
        logging.error(f"Database error: {e}")
        raise

# =====================================================
# CSV EXPORT (FOR POWER BI / DASHBOARD)
# =====================================================

def export_csv(trials_df, sponsors_df, locations_df, enrollment_df):

    os.makedirs("output", exist_ok=True)

    trials_df.to_csv("output/trials.csv", index=False)
    sponsors_df.to_csv("output/sponsors.csv", index=False)
    locations_df.to_csv("output/locations.csv", index=False)
    enrollment_df.to_csv("output/enrollment.csv", index=False)

    logging.info("CSV EXPORT COMPLETE")

# =====================================================
# MAIN
# =====================================================

def main():

    logging.info("PIPELINE START")

    studies = extract_data()

    trials_df, sponsors_df, locations_df, enrollment_df = transform_data(studies)

    validate_data(trials_df, sponsors_df, locations_df, enrollment_df)

    load_data(trials_df, sponsors_df, locations_df, enrollment_df)

    export_csv(trials_df, sponsors_df, locations_df, enrollment_df)

    logging.info("PIPELINE COMPLETED SUCCESSFULLY")


if __name__ == "__main__":
    main()