-- Table: Sponsor
CREATE TABLE Sponsor (
    Sponsor_ID SERIAL PRIMARY KEY,
    Sponsor_name VARCHAR(255) UNIQUE NOT NULL,
    Sponsor_class VARCHAR(50)
);

-- Table: Clinical_trial
CREATE TABLE Clinical_trial (
    nct_ID VARCHAR(20) PRIMARY KEY,
    Sponsor_ID INTEGER,
    Study_title TEXT NOT NULL,
    Recruitment_status VARCHAR(50) NOT NULL,
    Start_date DATE,
    Completion_date DATE,
    CONSTRAINT fk_sponsor_lookup FOREIGN KEY (Sponsor_ID) 
        REFERENCES Sponsor(Sponsor_ID) 
        ON DELETE SET NULL
);

-- Table: Enrollment_tracking
CREATE TABLE Enrollment_tracking (
    Enrollment_ID SERIAL PRIMARY KEY,
    nct_ID VARCHAR(20) NOT NULL,
    Target_enrollment INTEGER CHECK (Target_enrollment >= 0),
    Actual_enrrollment INTEGER CHECK (Actual_enrrollment >= 0),
    Last_update DATE,
    Missing_verification BOOLEAN DEFAULT FALSE,
    CONSTRAINT fk_trial_enrollment FOREIGN KEY (nct_ID) 
        REFERENCES Clinical_trial(nct_ID) 
        ON DELETE CASCADE
);

-- Table: Locations
CREATE TABLE Location (
    Location_ID SERIAL PRIMARY KEY,
    Facility_name VARCHAR(255) NOT NULL,
    City VARCHAR(100),
    State VARCHAR(50),
    Country VARCHAR(100)
);

-- Table: Trial_Location_jonction (Bridge table)
CREATE TABLE Trial_Location_jonction (
    nct_ID VARCHAR(20) NOT NULL,
    Location_ID INTEGER NOT NULL,
    PRIMARY KEY (nct_ID, Location_ID),
    CONSTRAINT fk_junction_trial FOREIGN KEY (nct_ID) 
        REFERENCES Clinical_trial(nct_ID) 
        ON DELETE CASCADE,
    CONSTRAINT fk_junction_location FOREIGN KEY (Location_ID) 
        REFERENCES Location(Location_ID) 
        ON DELETE CASCADE
);
