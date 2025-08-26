--
-- File generated with SQLiteStudio v3.4.17 on Mon Aug 25 23:52:13 2025
--
-- Text encoding used: System
--
PRAGMA foreign_keys = off;
BEGIN TRANSACTION;

-- Table: categories
CREATE TABLE IF NOT EXISTS categories (
    category_name             TEXT    NOT NULL,
    minimum_weeks             INTEGER NOT NULL,
    maximum_weeks             INTEGER NOT NULL,
    pertinent_role            TEXT    NOT NULL
                                      REFERENCES residency_role_options (resident_role) ON DELETE SET NULL
                                                                                        ON UPDATE CASCADE,
    track_specific            TEXT    REFERENCES resident_track_options (options) ON DELETE SET NULL
                                                                                  ON UPDATE CASCADE,
    specific_requirement_name TEXT    AS (CONCAT(category_name, ' - ', hard_due_year) ) 
                                      UNIQUE,
    soft_due_year             TEXT    REFERENCES residency_due_year_options (due_year) ON DELETE SET NULL
                                                                                       ON UPDATE CASCADE,
    hard_due_year                     REFERENCES residency_due_year_options (due_year) ON DELETE SET NULL
                                                                                       ON UPDATE CASCADE
);

INSERT INTO categories (category_name, minimum_weeks, maximum_weeks, pertinent_role, track_specific, soft_due_year, hard_due_year) VALUES ('HS Rounding Senior', 8, 8, 'IM-Senior', NULL, NULL, 'R3/End of Program');
INSERT INTO categories (category_name, minimum_weeks, maximum_weeks, pertinent_role, track_specific, soft_due_year, hard_due_year) VALUES ('Hospitalist', 4, 8, 'IM-Senior', NULL, NULL, 'R3/End of Program');
INSERT INTO categories (category_name, minimum_weeks, maximum_weeks, pertinent_role, track_specific, soft_due_year, hard_due_year) VALUES ('HS Admitting Senior', 8, 8, 'IM-Senior', NULL, NULL, 'R3/End of Program');
INSERT INTO categories (category_name, minimum_weeks, maximum_weeks, pertinent_role, track_specific, soft_due_year, hard_due_year) VALUES ('Primary Care Senior', 8, 8, 'IM-Senior', NULL, NULL, 'R3/End of Program');
INSERT INTO categories (category_name, minimum_weeks, maximum_weeks, pertinent_role, track_specific, soft_due_year, hard_due_year) VALUES ('Primary Care Intern', 8, 8, 'IM Intern', NULL, NULL, 'R1');
INSERT INTO categories (category_name, minimum_weeks, maximum_weeks, pertinent_role, track_specific, soft_due_year, hard_due_year) VALUES ('Night Senior', 3, 3, 'IM-Senior', NULL, NULL, 'R3/End of Program');
INSERT INTO categories (category_name, minimum_weeks, maximum_weeks, pertinent_role, track_specific, soft_due_year, hard_due_year) VALUES ('ICU Senior', 4, 8, 'IM-Senior', NULL, NULL, 'R3/End of Program');
INSERT INTO categories (category_name, minimum_weeks, maximum_weeks, pertinent_role, track_specific, soft_due_year, hard_due_year) VALUES ('Vacation', 3, 3, 'IM-Senior', NULL, NULL, 'R3/End of Program');
INSERT INTO categories (category_name, minimum_weeks, maximum_weeks, pertinent_role, track_specific, soft_due_year, hard_due_year) VALUES ('HS Rounding Intern', 8, 8, 'IM-Intern', NULL, NULL, 'R1');
INSERT INTO categories (category_name, minimum_weeks, maximum_weeks, pertinent_role, track_specific, soft_due_year, hard_due_year) VALUES ('ICU Intern', 8, 8, 'IM-Intern', NULL, NULL, 'R1');
INSERT INTO categories (category_name, minimum_weeks, maximum_weeks, pertinent_role, track_specific, soft_due_year, hard_due_year) VALUES ('HS Admitting Intern', 8, 8, 'IM-Intern', NULL, NULL, 'R1');
INSERT INTO categories (category_name, minimum_weeks, maximum_weeks, pertinent_role, track_specific, soft_due_year, hard_due_year) VALUES ('SHMC Night Intern', 4, 4, 'IM-Intern', NULL, NULL, 'R1');
INSERT INTO categories (category_name, minimum_weeks, maximum_weeks, pertinent_role, track_specific, soft_due_year, hard_due_year) VALUES ('Vacation', 3, 3, 'IM-Intern', NULL, NULL, 'R1');
INSERT INTO categories (category_name, minimum_weeks, maximum_weeks, pertinent_role, track_specific, soft_due_year, hard_due_year) VALUES ('Elective', 0, 53, 'IM-Senior', NULL, NULL, 'R3/End of Program');
INSERT INTO categories (category_name, minimum_weeks, maximum_weeks, pertinent_role, track_specific, soft_due_year, hard_due_year) VALUES ('GIM', 4, 4, 'IM-Senior', 'Primary Care', 'R3/End of Program', 'R3/End of Program');
INSERT INTO categories (category_name, minimum_weeks, maximum_weeks, pertinent_role, track_specific, soft_due_year, hard_due_year) VALUES ('Systems of Medicine', 2, 2, 'IM-Senior', NULL, 'R2', 'R3/End of Program');
INSERT INTO categories (category_name, minimum_weeks, maximum_weeks, pertinent_role, track_specific, soft_due_year, hard_due_year) VALUES ('Vacation', 3, 3, 'IM-Senior', NULL, NULL, 'R2');
INSERT INTO categories (category_name, minimum_weeks, maximum_weeks, pertinent_role, track_specific, soft_due_year, hard_due_year) VALUES ('Elective', 0, 53, 'IM-Senior', NULL, NULL, 'R2');
INSERT INTO categories (category_name, minimum_weeks, maximum_weeks, pertinent_role, track_specific, soft_due_year, hard_due_year) VALUES ('Elective', 0, 53, 'IM-Intern', NULL, NULL, 'R1');

-- Table: preferences
CREATE TABLE IF NOT EXISTS preferences (
    full_name     TEXT,
    [ rotation]   TEXT,
    [ week]       INTEGER,
    [ preference] INTEGER,
    CONSTRAINT preferences_residents_FK FOREIGN KEY (
        full_name
    )
    REFERENCES residents (full_name) ON DELETE SET NULL
                                     ON UPDATE RESTRICT
);


-- Table: prerequisites
CREATE TABLE IF NOT EXISTS prerequisites (
    blocked_category      TEXT    REFERENCES categories (specific_requirement_name) ON DELETE RESTRICT
                                                                                    ON UPDATE CASCADE,
    prerequisite_category TEXT    REFERENCES categories (specific_requirement_name) ON DELETE RESTRICT
                                                                                    ON UPDATE CASCADE,
    weeks                 INTEGER NOT NULL
);

INSERT INTO prerequisites (blocked_category, prerequisite_category, weeks) VALUES ('HS Rounding Senior - R3/End of Program', 'HS Admitting Senior - R3/End of Program', 4);

-- Table: requirements
CREATE TABLE IF NOT EXISTS requirements (
    requirement_name   TEXT    NOT NULL,
    weeks_required     INTEGER NOT NULL,
    role               TEXT    REFERENCES residency_role_options (resident_role) ON DELETE SET NULL
                                                                                 ON UPDATE CASCADE,
    hard_due_year      TEXT    REFERENCES residency_due_year_options (due_year) ON DELETE RESTRICT
                                                                                ON UPDATE CASCADE,
    suggested_due_year TEXT    REFERENCES residency_due_year_options (due_year) ON DELETE RESTRICT
                                                                                ON UPDATE CASCADE
);

INSERT INTO requirements (requirement_name, weeks_required, role, hard_due_year, suggested_due_year) VALUES ('HS Rounding Intern - TY', 8, 'TY', 'R1', 'R1');
INSERT INTO requirements (requirement_name, weeks_required, role, hard_due_year, suggested_due_year) VALUES ('Night Senior - IM-Senior', 8, 'IM-Senior', NULL, NULL);
INSERT INTO requirements (requirement_name, weeks_required, role, hard_due_year, suggested_due_year) VALUES ('HS Rounding Senior - IM-Senior', 12, 'IM-Senior', NULL, NULL);
INSERT INTO requirements (requirement_name, weeks_required, role, hard_due_year, suggested_due_year) VALUES ('Hospitalist - IM-Senior', 2, 'IM-Senior', NULL, NULL);

-- Table: residency_due_year_options
CREATE TABLE IF NOT EXISTS residency_due_year_options (
    due_year TEXT UNIQUE
                NOT NULL
);

INSERT INTO residency_due_year_options (due_year) VALUES ('R3/End of Program');
INSERT INTO residency_due_year_options (due_year) VALUES ('R2');
INSERT INTO residency_due_year_options (due_year) VALUES ('R1');

-- Table: residency_role_options
CREATE TABLE IF NOT EXISTS residency_role_options (
    resident_role TEXT PRIMARY KEY
                     UNIQUE
                     NOT NULL
);

INSERT INTO residency_role_options (resident_role) VALUES ('IM-Senior');
INSERT INTO residency_role_options (resident_role) VALUES ('IM-Intern');
INSERT INTO residency_role_options (resident_role) VALUES ('PMR');
INSERT INTO residency_role_options (resident_role) VALUES ('TY');

-- Table: resident_track_options
CREATE TABLE IF NOT EXISTS resident_track_options (
    options TEXT UNIQUE
               NOT NULL
);

INSERT INTO resident_track_options (options) VALUES ('Rural');
INSERT INTO resident_track_options (options) VALUES ('Primary Care');
INSERT INTO resident_track_options (options) VALUES ('Hospitalist');
INSERT INTO resident_track_options (options) VALUES ('Fellowship');

-- Table: resident_year_options
CREATE TABLE IF NOT EXISTS resident_year_options (
    resident_year TEXT UNIQUE
                     NOT NULL
                     PRIMARY KEY
);

INSERT INTO resident_year_options (resident_year) VALUES ('R3');
INSERT INTO resident_year_options (resident_year) VALUES ('R2');
INSERT INTO resident_year_options (resident_year) VALUES ('R1');
INSERT INTO resident_year_options (resident_year) VALUES ('PMR1');
INSERT INTO resident_year_options (resident_year) VALUES ('TY1');
INSERT INTO resident_year_options (resident_year) VALUES ('R3 Extension');

-- Table: residents
CREATE TABLE IF NOT EXISTS residents (
    full_name TEXT PRIMARY KEY
                   UNIQUE
                   NOT NULL,
    year      TEXT NOT NULL
                   REFERENCES resident_year_options (resident_year) ON DELETE RESTRICT
                                                                    ON UPDATE CASCADE,
    role      TEXT NOT NULL
                   REFERENCES residency_role_options (resident_role) ON DELETE RESTRICT
                                                                     ON UPDATE CASCADE,
    track     TEXT REFERENCES resident_track_options (options) ON DELETE RESTRICT
                                                               ON UPDATE CASCADE
);

INSERT INTO residents (full_name, year, role, track) VALUES ('Alex Carroll MD', 'R3', 'IM-Senior', 'Hospitalist');
INSERT INTO residents (full_name, year, role, track) VALUES ('Michelle Smith MD', 'R3', 'IM-Senior', 'Primary Care Track');
INSERT INTO residents (full_name, year, role, track) VALUES ('Rebekah Lewis MD', 'R3', 'IM-Senior', 'Primary Care Track');
INSERT INTO residents (full_name, year, role, track) VALUES ('Stefanie Barrett MD', 'R3', 'IM-Senior', 'Fellowship');
INSERT INTO residents (full_name, year, role, track) VALUES ('Lauren Joseph DO', 'R3', 'IM-Senior', 'Fellowship');
INSERT INTO residents (full_name, year, role, track) VALUES ('James Griffin DO', 'R3', 'IM-Senior', 'Fellowship');
INSERT INTO residents (full_name, year, role, track) VALUES ('Brittney Martin MD', 'R3', 'IM-Senior', 'Primary Care');
INSERT INTO residents (full_name, year, role, track) VALUES ('John Moore DO', 'R3', 'IM-Senior', 'Rural');
INSERT INTO residents (full_name, year, role, track) VALUES ('Kyle Jefferson MD', 'R3', 'IM-Senior', 'Primary Care');
INSERT INTO residents (full_name, year, role, track) VALUES ('Wanda Schmidt MD', 'R3', 'IM-Senior', 'Hospitalist');
INSERT INTO residents (full_name, year, role, track) VALUES ('Deborah Ford MD', 'R3 Extended', 'IM-Senior', 'Hospitalist');
INSERT INTO residents (full_name, year, role, track) VALUES ('Stephanie Baker MD', 'R3 Extended', 'IM-Senior', 'Hospitalist');
INSERT INTO residents (full_name, year, role, track) VALUES ('John Bauer MD', 'R2', 'IM-Senior', 'Hospitalist');
INSERT INTO residents (full_name, year, role, track) VALUES ('Wendy Roberts DO', 'R2', 'IM-Senior', 'Hospitalist');
INSERT INTO residents (full_name, year, role, track) VALUES ('Kathleen Francis DO', 'R2', 'IM-Senior', 'Primary Care Track');
INSERT INTO residents (full_name, year, role, track) VALUES ('Tyler Willis DO', 'R2', 'IM-Senior', 'Primary Care');
INSERT INTO residents (full_name, year, role, track) VALUES ('Anita Rowe DO', 'R2', 'IM-Senior', 'Primary Care');
INSERT INTO residents (full_name, year, role, track) VALUES ('Alexander Craig MD', 'R2', 'IM-Senior', 'Rural');
INSERT INTO residents (full_name, year, role, track) VALUES ('Ronald Savage MD', 'R2', 'IM-Senior', 'Hospitalist');
INSERT INTO residents (full_name, year, role, track) VALUES ('Donald Riddle DO', 'R2', 'IM-Senior', 'Hospitalist');
INSERT INTO residents (full_name, year, role, track) VALUES ('Pamela Kelly DO', 'R2', 'IM-Senior', 'Hospitalist');
INSERT INTO residents (full_name, year, role, track) VALUES ('Eric Norman MD', 'R2', 'IM-Senior', 'Fellowship');

-- Table: rotations
CREATE TABLE IF NOT EXISTS rotations (
    rotation                   TEXT    UNIQUE
                                       NOT NULL,
    category                   TEXT    NOT NULL,
    required_role              TEXT    NOT NULL,
    minimum_weeks              INTEGER NOT NULL,
    maximum_weeks              INTEGER NOT NULL,
    minimum_residents_assigned INTEGER NOT NULL,
    maximum_residents_assigned INTEGER NOT NULL,
    minimum_contiguous_weeks   INTEGER,
    max_contiguous_weeks       INTEGER
);

INSERT INTO rotations (rotation, category, required_role, minimum_weeks, maximum_weeks, minimum_residents_assigned, maximum_residents_assigned, minimum_contiguous_weeks, max_contiguous_weeks) VALUES ('Green HS Senior', 'HS Rounding Senior', 'Senior', 0, 8, 1, 1, 2, NULL);
INSERT INTO rotations (rotation, category, required_role, minimum_weeks, maximum_weeks, minimum_residents_assigned, maximum_residents_assigned, minimum_contiguous_weeks, max_contiguous_weeks) VALUES ('Orange HS Senior', 'HS Rounding Senior', 'Senior', 0, 8, 1, 1, 2, NULL);
INSERT INTO rotations (rotation, category, required_role, minimum_weeks, maximum_weeks, minimum_residents_assigned, maximum_residents_assigned, minimum_contiguous_weeks, max_contiguous_weeks) VALUES ('SHMC Consults', 'Hospitalist', 'Senior', 0, 4, 0, 1, 1, NULL);
INSERT INTO rotations (rotation, category, required_role, minimum_weeks, maximum_weeks, minimum_residents_assigned, maximum_residents_assigned, minimum_contiguous_weeks, max_contiguous_weeks) VALUES ('SHMC Admitting', 'Hospitalist', 'Senior', 0, 4, 0, 1, 1, NULL);
INSERT INTO rotations (rotation, category, required_role, minimum_weeks, maximum_weeks, minimum_residents_assigned, maximum_residents_assigned, minimum_contiguous_weeks, max_contiguous_weeks) VALUES ('Orange HS Intern', 'HS Rounding Intern', 'Any Intern', 0, 8, 2, 2, 4, NULL);
INSERT INTO rotations (rotation, category, required_role, minimum_weeks, maximum_weeks, minimum_residents_assigned, maximum_residents_assigned, minimum_contiguous_weeks, max_contiguous_weeks) VALUES ('Green HS Intern', 'HS Rounding Intern', 'Any Intern', 0, 8, 2, 2, 4, NULL);
INSERT INTO rotations (rotation, category, required_role, minimum_weeks, maximum_weeks, minimum_residents_assigned, maximum_residents_assigned, minimum_contiguous_weeks, max_contiguous_weeks) VALUES ('Purple HS Senior', 'HS Admitting Senior', 'Senior', 8, 8, 1, 1, 1, 1);
INSERT INTO rotations (rotation, category, required_role, minimum_weeks, maximum_weeks, minimum_residents_assigned, maximum_residents_assigned, minimum_contiguous_weeks, max_contiguous_weeks) VALUES ('Purple HS Intern', 'HS Admitting Intern', 'Any Intern', 4, 4, 1, 1, 1, NULL);
INSERT INTO rotations (rotation, category, required_role, minimum_weeks, maximum_weeks, minimum_residents_assigned, maximum_residents_assigned, minimum_contiguous_weeks, max_contiguous_weeks) VALUES ('DH Rounding', 'Hospitalist', 'Senior', 0, 4, 0, 1, 1, NULL);
INSERT INTO rotations (rotation, category, required_role, minimum_weeks, maximum_weeks, minimum_residents_assigned, maximum_residents_assigned, minimum_contiguous_weeks, max_contiguous_weeks) VALUES ('SHMC Rounding', 'Hospitalist', 'Senior', 0, 4, 0, 2, 1, NULL);
INSERT INTO rotations (rotation, category, required_role, minimum_weeks, maximum_weeks, minimum_residents_assigned, maximum_residents_assigned, minimum_contiguous_weeks, max_contiguous_weeks) VALUES ('STHC Intern', 'Primary Care Intern', 'IM Intern', 8, 8, 0, 5, 1, NULL);
INSERT INTO rotations (rotation, category, required_role, minimum_weeks, maximum_weeks, minimum_residents_assigned, maximum_residents_assigned, minimum_contiguous_weeks, max_contiguous_weeks) VALUES ('STHC Senior Non-Ambulatory', 'Primary Care Senior', 'Senior', 4, 4, 0, 5, 1, NULL);
INSERT INTO rotations (rotation, category, required_role, minimum_weeks, maximum_weeks, minimum_residents_assigned, maximum_residents_assigned, minimum_contiguous_weeks, max_contiguous_weeks) VALUES ('SHMC Night Senior', 'Night Senior', 'Senior', 8, 8, 1, 2, 2, NULL);
INSERT INTO rotations (rotation, category, required_role, minimum_weeks, maximum_weeks, minimum_residents_assigned, maximum_residents_assigned, minimum_contiguous_weeks, max_contiguous_weeks) VALUES ('SHMC Night Intern', 'SHMC Night Intern', 'Any Intern', 4, 4, 2, 2, 4, NULL);
INSERT INTO rotations (rotation, category, required_role, minimum_weeks, maximum_weeks, minimum_residents_assigned, maximum_residents_assigned, minimum_contiguous_weeks, max_contiguous_weeks) VALUES ('Multicare Heme/Onc', 'Heme/Onc Specialty', 'Senior', 0, 4, 0, 1, 1, NULL);
INSERT INTO rotations (rotation, category, required_role, minimum_weeks, maximum_weeks, minimum_residents_assigned, maximum_residents_assigned, minimum_contiguous_weeks, max_contiguous_weeks) VALUES ('DH ICU Senior', 'ICU Senior', 'Senior', 0, 0, 1, 1, 4, NULL);
INSERT INTO rotations (rotation, category, required_role, minimum_weeks, maximum_weeks, minimum_residents_assigned, maximum_residents_assigned, minimum_contiguous_weeks, max_contiguous_weeks) VALUES ('SHMC CICU', 'ICU Senior', 'Senior', 0, 4, 0, 1, 1, NULL);
INSERT INTO rotations (rotation, category, required_role, minimum_weeks, maximum_weeks, minimum_residents_assigned, maximum_residents_assigned, minimum_contiguous_weeks, max_contiguous_weeks) VALUES ('STHC Senior Ambulatory', 'Primary Care Senior', 'Senior', 4, 4, 1, 1, 1, NULL);
INSERT INTO rotations (rotation, category, required_role, minimum_weeks, maximum_weeks, minimum_residents_assigned, maximum_residents_assigned, minimum_contiguous_weeks, max_contiguous_weeks) VALUES ('Multicare Endocrinology', 'Endocrinology Specialty', 'Senior', 0, 4, 0, 2, 2, NULL);
INSERT INTO rotations (rotation, category, required_role, minimum_weeks, maximum_weeks, minimum_residents_assigned, maximum_residents_assigned, minimum_contiguous_weeks, max_contiguous_weeks) VALUES ('Vacation', 'Vacation', 'Any', 3, 3, 0, 5, 1, NULL);

-- Table: rotations_completed
CREATE TABLE IF NOT EXISTS rotations_completed (
    resident   TEXT    REFERENCES residents (full_name) ON DELETE SET NULL
                                                        ON UPDATE CASCADE
                       NOT NULL,
    weeks      INTEGER NOT NULL,
    rotation   TEXT    REFERENCES rotations (rotation) ON DELETE SET NULL
                                                       ON UPDATE CASCADE
                       NOT NULL,
    start_date TEXT    CHECK ( (date(start_date) NOT NULL) OR
                               (start_date IS NULL) ) 
);

INSERT INTO rotations_completed (resident, weeks, rotation, start_date) VALUES ('Alex Carroll MD', 4, 'Green HS Senior', NULL);

-- Table: weeks
CREATE TABLE IF NOT EXISTS weeks (
    monday_date            TEXT    NOT NULL
                                   UNIQUE,
    week                   INTEGER NOT NULL,
    starting_academic_year INTEGER NOT NULL,
    ending_academic_year   INTEGER NOT NULL
);

INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('7/1/2024', 1, 2024, 2025);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('7/8/2024', 2, 2024, 2025);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('7/15/2024', 3, 2024, 2025);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('7/22/2024', 4, 2024, 2025);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('7/29/2024', 5, 2024, 2025);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('8/5/2024', 6, 2024, 2025);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('8/12/2024', 7, 2024, 2025);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('8/19/2024', 8, 2024, 2025);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('8/26/2024', 9, 2024, 2025);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('9/2/2024', 10, 2024, 2025);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('9/9/2024', 11, 2024, 2025);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('9/16/2024', 12, 2024, 2025);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('9/23/2024', 13, 2024, 2025);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('9/30/2024', 14, 2024, 2025);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('10/7/2024', 15, 2024, 2025);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('10/14/2024', 16, 2024, 2025);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('10/21/2024', 17, 2024, 2025);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('10/28/2024', 18, 2024, 2025);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('11/4/2024', 19, 2024, 2025);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('11/11/2024', 20, 2024, 2025);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('11/18/2024', 21, 2024, 2025);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('11/25/2024', 22, 2024, 2025);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('12/2/2024', 23, 2024, 2025);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('12/9/2024', 24, 2024, 2025);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('12/16/2024', 25, 2024, 2025);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('12/23/2024', 26, 2024, 2025);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('12/30/2024', 27, 2024, 2025);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('1/6/2025', 28, 2024, 2025);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('1/13/2025', 29, 2024, 2025);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('1/20/2025', 30, 2024, 2025);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('1/27/2025', 31, 2024, 2025);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2/3/2025', 32, 2024, 2025);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2/10/2025', 33, 2024, 2025);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2/17/2025', 34, 2024, 2025);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2/24/2025', 35, 2024, 2025);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('3/3/2025', 36, 2024, 2025);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('3/10/2025', 37, 2024, 2025);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('3/17/2025', 38, 2024, 2025);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('3/24/2025', 39, 2024, 2025);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('3/31/2025', 40, 2024, 2025);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('4/7/2025', 41, 2024, 2025);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('4/14/2025', 42, 2024, 2025);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('4/21/2025', 43, 2024, 2025);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('4/28/2025', 44, 2024, 2025);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('5/5/2025', 45, 2024, 2025);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('5/12/2025', 46, 2024, 2025);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('5/19/2025', 47, 2024, 2025);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('5/26/2025', 48, 2024, 2025);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('6/2/2025', 49, 2024, 2025);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('6/9/2025', 50, 2024, 2025);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('6/16/2025', 51, 2024, 2025);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('6/23/2025', 52, 2024, 2025);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('6/30/2025', 1, 2025, 2026);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('7/7/2025', 2, 2025, 2026);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('7/14/2025', 3, 2025, 2026);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('7/21/2025', 4, 2025, 2026);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('7/28/2025', 5, 2025, 2026);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('8/4/2025', 6, 2025, 2026);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('8/11/2025', 7, 2025, 2026);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('8/18/2025', 8, 2025, 2026);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('8/25/2025', 9, 2025, 2026);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('9/1/2025', 10, 2025, 2026);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('9/8/2025', 11, 2025, 2026);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('9/15/2025', 12, 2025, 2026);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('9/22/2025', 13, 2025, 2026);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('9/29/2025', 14, 2025, 2026);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('10/6/2025', 15, 2025, 2026);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('10/13/2025', 16, 2025, 2026);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('10/20/2025', 17, 2025, 2026);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('10/27/2025', 18, 2025, 2026);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('11/3/2025', 19, 2025, 2026);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('11/10/2025', 20, 2025, 2026);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('11/17/2025', 21, 2025, 2026);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('11/24/2025', 22, 2025, 2026);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('12/1/2025', 23, 2025, 2026);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('12/8/2025', 24, 2025, 2026);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('12/15/2025', 25, 2025, 2026);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('12/22/2025', 26, 2025, 2026);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('12/29/2025', 27, 2025, 2026);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('1/5/2026', 28, 2025, 2026);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('1/12/2026', 29, 2025, 2026);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('1/19/2026', 30, 2025, 2026);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('1/26/2026', 31, 2025, 2026);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2/2/2026', 32, 2025, 2026);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2/9/2026', 33, 2025, 2026);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2/16/2026', 34, 2025, 2026);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2/23/2026', 35, 2025, 2026);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('3/2/2026', 36, 2025, 2026);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('3/9/2026', 37, 2025, 2026);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('3/16/2026', 38, 2025, 2026);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('3/23/2026', 39, 2025, 2026);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('3/30/2026', 40, 2025, 2026);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('4/6/2026', 41, 2025, 2026);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('4/13/2026', 42, 2025, 2026);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('4/20/2026', 43, 2025, 2026);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('4/27/2026', 44, 2025, 2026);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('5/4/2026', 45, 2025, 2026);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('5/11/2026', 46, 2025, 2026);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('5/18/2026', 47, 2025, 2026);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('5/25/2026', 48, 2025, 2026);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('6/1/2026', 49, 2025, 2026);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('6/8/2026', 50, 2025, 2026);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('6/15/2026', 51, 2025, 2026);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('6/22/2026', 52, 2025, 2026);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('6/29/2026', 53, 2025, 2026);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('7/6/2026', 1, 2026, 2027);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('7/13/2026', 2, 2026, 2027);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('7/20/2026', 3, 2026, 2027);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('7/27/2026', 4, 2026, 2027);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('8/3/2026', 5, 2026, 2027);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('8/10/2026', 6, 2026, 2027);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('8/17/2026', 7, 2026, 2027);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('8/24/2026', 8, 2026, 2027);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('8/31/2026', 9, 2026, 2027);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('9/7/2026', 10, 2026, 2027);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('9/14/2026', 11, 2026, 2027);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('9/21/2026', 12, 2026, 2027);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('9/28/2026', 13, 2026, 2027);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('10/5/2026', 14, 2026, 2027);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('10/12/2026', 15, 2026, 2027);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('10/19/2026', 16, 2026, 2027);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('10/26/2026', 17, 2026, 2027);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('11/2/2026', 18, 2026, 2027);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('11/9/2026', 19, 2026, 2027);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('11/16/2026', 20, 2026, 2027);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('11/23/2026', 21, 2026, 2027);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('11/30/2026', 22, 2026, 2027);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('12/7/2026', 23, 2026, 2027);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('12/14/2026', 24, 2026, 2027);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('12/21/2026', 25, 2026, 2027);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('12/28/2026', 26, 2026, 2027);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('1/4/2027', 27, 2026, 2027);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('1/11/2027', 28, 2026, 2027);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('1/18/2027', 29, 2026, 2027);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('1/25/2027', 30, 2026, 2027);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2/1/2027', 31, 2026, 2027);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2/8/2027', 32, 2026, 2027);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2/15/2027', 33, 2026, 2027);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2/22/2027', 34, 2026, 2027);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('3/1/2027', 35, 2026, 2027);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('3/8/2027', 36, 2026, 2027);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('3/15/2027', 37, 2026, 2027);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('3/22/2027', 38, 2026, 2027);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('3/29/2027', 39, 2026, 2027);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('4/5/2027', 40, 2026, 2027);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('4/12/2027', 41, 2026, 2027);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('4/19/2027', 42, 2026, 2027);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('4/26/2027', 43, 2026, 2027);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('5/3/2027', 44, 2026, 2027);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('5/10/2027', 45, 2026, 2027);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('5/17/2027', 46, 2026, 2027);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('5/24/2027', 47, 2026, 2027);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('5/31/2027', 48, 2026, 2027);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('6/7/2027', 49, 2026, 2027);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('6/14/2027', 50, 2026, 2027);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('6/21/2027', 51, 2026, 2027);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('6/28/2027', 52, 2026, 2027);

COMMIT TRANSACTION;
PRAGMA foreign_keys = on;
