--
-- File generated with SQLiteStudio v3.4.17 on Sun Aug 17 21:07:53 2025
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
    elective                  TEXT    NOT NULL,
    specific_requirement_name TEXT    AS (CONCAT(category_name, ' - ', pertinent_role) ) 
                                      UNIQUE
);

INSERT INTO categories (category_name, minimum_weeks, maximum_weeks, pertinent_role, elective) VALUES ('HS Rounding Senior', 8, 8, 'IM-Senior', 'core');
INSERT INTO categories (category_name, minimum_weeks, maximum_weeks, pertinent_role, elective) VALUES ('HS Rounding Intern', 8, 8, 'TY', 'core');
INSERT INTO categories (category_name, minimum_weeks, maximum_weeks, pertinent_role, elective) VALUES ('Hospitalist', 4, 8, 'IM-Senior', 'elective');
INSERT INTO categories (category_name, minimum_weeks, maximum_weeks, pertinent_role, elective) VALUES ('ICU Intern', 8, 8, 'TY', 'core');
INSERT INTO categories (category_name, minimum_weeks, maximum_weeks, pertinent_role, elective) VALUES ('HS Admitting Senior', 8, 8, 'IM-Senior', 'core');
INSERT INTO categories (category_name, minimum_weeks, maximum_weeks, pertinent_role, elective) VALUES ('HS Admitting Intern', 8, 8, 'TY', 'core');
INSERT INTO categories (category_name, minimum_weeks, maximum_weeks, pertinent_role, elective) VALUES ('Endocrinology Specialty', 2, 8, 'IM-Senior', 'elective');
INSERT INTO categories (category_name, minimum_weeks, maximum_weeks, pertinent_role, elective) VALUES ('Pulmonology Specialty', 2, 8, 'IM-Senior', 'elective');
INSERT INTO categories (category_name, minimum_weeks, maximum_weeks, pertinent_role, elective) VALUES ('Rheumatology Speciality', 2, 8, 'IM-Senior', 'elective');
INSERT INTO categories (category_name, minimum_weeks, maximum_weeks, pertinent_role, elective) VALUES ('Primary Care Senior', 8, 8, 'IM-Senior', 'core');
INSERT INTO categories (category_name, minimum_weeks, maximum_weeks, pertinent_role, elective) VALUES ('Primary Care Intern', 8, 8, 'IM Intern', 'core');
INSERT INTO categories (category_name, minimum_weeks, maximum_weeks, pertinent_role, elective) VALUES ('Night Senior', 3, 3, 'IM-Senior', 'core');
INSERT INTO categories (category_name, minimum_weeks, maximum_weeks, pertinent_role, elective) VALUES ('SHMC Night Intern', 4, 4, 'TY', 'core');
INSERT INTO categories (category_name, minimum_weeks, maximum_weeks, pertinent_role, elective) VALUES ('Heme/Onc Specialty', 2, 8, 'IM-Senior', 'elective');
INSERT INTO categories (category_name, minimum_weeks, maximum_weeks, pertinent_role, elective) VALUES ('ICU Senior', 4, 8, 'IM-Senior', 'core');
INSERT INTO categories (category_name, minimum_weeks, maximum_weeks, pertinent_role, elective) VALUES ('Primary Care Track', 0, 12, 'IM-Senior', 'elective');
INSERT INTO categories (category_name, minimum_weeks, maximum_weeks, pertinent_role, elective) VALUES ('ICU Specialty', 4, 8, 'IM-Senior', 'elective');
INSERT INTO categories (category_name, minimum_weeks, maximum_weeks, pertinent_role, elective) VALUES ('Vacation', 6, 6, 'IM-Senior', 'core ');
INSERT INTO categories (category_name, minimum_weeks, maximum_weeks, pertinent_role, elective) VALUES ('TY Elective', 18, 24, 'TY', 'elective');
INSERT INTO categories (category_name, minimum_weeks, maximum_weeks, pertinent_role, elective) VALUES ('PMR Elective', 18, 24, 'PMR', 'elective');
INSERT INTO categories (category_name, minimum_weeks, maximum_weeks, pertinent_role, elective) VALUES ('HS Rounding Intern', 8, 8, 'IM-Intern', 'core');
INSERT INTO categories (category_name, minimum_weeks, maximum_weeks, pertinent_role, elective) VALUES ('HS Rounding Intern', 8, 8, 'PMR', 'core');
INSERT INTO categories (category_name, minimum_weeks, maximum_weeks, pertinent_role, elective) VALUES ('ICU Intern', 8, 8, 'IM-Intern', 'core');
INSERT INTO categories (category_name, minimum_weeks, maximum_weeks, pertinent_role, elective) VALUES ('ICU Intern', 8, 8, 'PMR', 'core');
INSERT INTO categories (category_name, minimum_weeks, maximum_weeks, pertinent_role, elective) VALUES ('HS Admitting Intern', 8, 8, 'IM-Intern', 'core');
INSERT INTO categories (category_name, minimum_weeks, maximum_weeks, pertinent_role, elective) VALUES ('HS Admitting Intern', 8, 8, 'PMR', 'core');
INSERT INTO categories (category_name, minimum_weeks, maximum_weeks, pertinent_role, elective) VALUES ('SHMC Night Intern', 4, 4, 'IM-Intern', 'core');
INSERT INTO categories (category_name, minimum_weeks, maximum_weeks, pertinent_role, elective) VALUES ('SHMC Night Intern', 4, 4, 'PMR', 'core');
INSERT INTO categories (category_name, minimum_weeks, maximum_weeks, pertinent_role, elective) VALUES ('Vacation', 3, 3, 'TY', 'core ');
INSERT INTO categories (category_name, minimum_weeks, maximum_weeks, pertinent_role, elective) VALUES ('Vacation', 3, 3, 'PMR', 'core ');
INSERT INTO categories (category_name, minimum_weeks, maximum_weeks, pertinent_role, elective) VALUES ('Vacation', 3, 3, 'IM-Intern', 'core ');

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

INSERT INTO preferences (full_name, " rotation", " week", " preference") VALUES (NULL, NULL, NULL, NULL);

-- Table: requirements
CREATE TABLE IF NOT EXISTS requirements (
    requirement_name TEXT    REFERENCES categories (specific_requirement_name) ON DELETE SET NULL
                                                                               ON UPDATE CASCADE
                             NOT NULL,
    weeks_required   INTEGER NOT NULL,
    role             TEXT    REFERENCES residency_role_options (resident_role) ON DELETE SET NULL
                                                                               ON UPDATE CASCADE
);

INSERT INTO requirements (requirement_name, weeks_required, role) VALUES ('HS Rounding Intern - TY', 8, 'TY');
INSERT INTO requirements (requirement_name, weeks_required, role) VALUES ('Night Senior - IM-Senior', 8, 'IM-Senior');
INSERT INTO requirements (requirement_name, weeks_required, role) VALUES ('HS Rounding Senior - IM-Senior', 12, 'IM-Senior');
INSERT INTO requirements (requirement_name, weeks_required, role) VALUES ('Hospitalist - IM-Senior', 2, 'IM-Senior');

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

-- Table: residents
CREATE TABLE IF NOT EXISTS residents (
    full_name TEXT NOT NULL
                   PRIMARY KEY
                   UNIQUE,
    year      TEXT NOT NULL
                   REFERENCES resident_year_options (resident_year) ON DELETE SET NULL
                                                                    ON UPDATE CASCADE,
    role      TEXT NOT NULL
                   REFERENCES residency_role_options (resident_role) ON DELETE SET NULL
                                                                     ON UPDATE CASCADE
);

INSERT INTO residents (full_name, year, role) VALUES ('Matthew Duncan DO', 'TY1', 'TY');
INSERT INTO residents (full_name, year, role) VALUES ('Jimmy Brown MD', 'TY1', 'TY');
INSERT INTO residents (full_name, year, role) VALUES ('Tracy Mcdaniel MD', 'TY1', 'TY');
INSERT INTO residents (full_name, year, role) VALUES ('Victoria Hunter DO', 'TY1', 'TY');
INSERT INTO residents (full_name, year, role) VALUES ('Jennifer Gill DO', 'TY1', 'TY');
INSERT INTO residents (full_name, year, role) VALUES ('Eric Mcguire MD', 'TY1', 'TY');
INSERT INTO residents (full_name, year, role) VALUES ('Rebecca Santiago DO', 'TY1', 'TY');
INSERT INTO residents (full_name, year, role) VALUES ('Vincent Peterson DO', 'TY1', 'TY');
INSERT INTO residents (full_name, year, role) VALUES ('Shannon Pierce DO', 'PMR1', 'PMR');
INSERT INTO residents (full_name, year, role) VALUES ('William Adkins MD', 'PMR1', 'PMR');
INSERT INTO residents (full_name, year, role) VALUES ('Donna Martin DO', 'PMR1', 'PMR');
INSERT INTO residents (full_name, year, role) VALUES ('Ann Sawyer DO', 'PMR1', 'PMR');
INSERT INTO residents (full_name, year, role) VALUES ('Dakota Brown MD', 'PMR1', 'PMR');
INSERT INTO residents (full_name, year, role) VALUES ('Todd Davis DO', 'PMR1', 'PMR');
INSERT INTO residents (full_name, year, role) VALUES ('Frank Hall MD', 'PMR1', 'PMR');
INSERT INTO residents (full_name, year, role) VALUES ('Michael Williamson DO', 'PMR1', 'PMR');
INSERT INTO residents (full_name, year, role) VALUES ('Cynthia Perez MD', 'R1', 'IM-Intern');
INSERT INTO residents (full_name, year, role) VALUES ('James Alvarez DO', 'R1', 'IM-Intern');
INSERT INTO residents (full_name, year, role) VALUES ('Susan Schwartz MD', 'R1', 'IM-Intern');
INSERT INTO residents (full_name, year, role) VALUES ('Michael Stewart MD', 'R1', 'IM-Intern');
INSERT INTO residents (full_name, year, role) VALUES ('Tara Brown DO', 'R1', 'IM-Intern');
INSERT INTO residents (full_name, year, role) VALUES ('Ann Brown MD', 'R1', 'IM-Intern');
INSERT INTO residents (full_name, year, role) VALUES ('Janet Hernandez MD', 'R1', 'IM-Intern');
INSERT INTO residents (full_name, year, role) VALUES ('Rebekah Morgan DO', 'R1', 'IM-Intern');
INSERT INTO residents (full_name, year, role) VALUES ('Pamela Kelly DO', 'R1', 'IM-Intern');
INSERT INTO residents (full_name, year, role) VALUES ('Eric Norman MD', 'R1', 'IM-Intern');
INSERT INTO residents (full_name, year, role) VALUES ('Alex Carroll MD', 'R2', 'IM-Senior');
INSERT INTO residents (full_name, year, role) VALUES ('Michelle Smith MD', 'R2', 'IM-Senior');
INSERT INTO residents (full_name, year, role) VALUES ('Rebekah Lewis MD', 'R2', 'IM-Senior');
INSERT INTO residents (full_name, year, role) VALUES ('Stefanie Barrett MD', 'R2', 'IM-Senior');
INSERT INTO residents (full_name, year, role) VALUES ('Lauren Joseph DO', 'R2', 'IM-Senior');
INSERT INTO residents (full_name, year, role) VALUES ('James Griffin DO', 'R2', 'IM-Senior');
INSERT INTO residents (full_name, year, role) VALUES ('Brittney Martin MD', 'R2', 'IM-Senior');
INSERT INTO residents (full_name, year, role) VALUES ('John Moore DO', 'R2', 'IM-Senior');
INSERT INTO residents (full_name, year, role) VALUES ('Kyle Jefferson MD', 'R2', 'IM-Senior');
INSERT INTO residents (full_name, year, role) VALUES ('Wanda Schmidt MD', 'R2', 'IM-Senior');
INSERT INTO residents (full_name, year, role) VALUES ('Deborah Ford MD', 'R3', 'IM-Senior');
INSERT INTO residents (full_name, year, role) VALUES ('Stephanie Baker MD', 'R3', 'IM-Senior');
INSERT INTO residents (full_name, year, role) VALUES ('John Bauer MD', 'R3', 'IM-Senior');
INSERT INTO residents (full_name, year, role) VALUES ('Wendy Roberts DO', 'R3', 'IM-Senior');
INSERT INTO residents (full_name, year, role) VALUES ('Kathleen Francis DO', 'R3', 'IM-Senior');
INSERT INTO residents (full_name, year, role) VALUES ('Tyler Willis DO', 'R3', 'IM-Senior');
INSERT INTO residents (full_name, year, role) VALUES ('Anita Rowe DO', 'R3', 'IM-Senior');
INSERT INTO residents (full_name, year, role) VALUES ('Alexander Craig MD', 'R3', 'IM-Senior');
INSERT INTO residents (full_name, year, role) VALUES ('Ronald Savage MD', 'R3', 'IM-Senior');
INSERT INTO residents (full_name, year, role) VALUES ('Donald Riddle DO', 'R3', 'IM-Senior');

-- Table: rotations
CREATE TABLE IF NOT EXISTS rotations (
    rotation                   TEXT    UNIQUE
                                       NOT NULL,
    category                   TEXT    REFERENCES categories (category_name) ON DELETE SET NULL
                                                                             ON UPDATE CASCADE,
    required_role              TEXT    REFERENCES residency_role_options (resident_role) ON DELETE NO ACTION
                                                                                         ON UPDATE CASCADE,
    minimum_weeks              INTEGER NOT NULL,
    maximum_weeks              INTEGER NOT NULL,
    minimum_residents_assigned INTEGER NOT NULL,
    maximum_residents_assigned INTEGER NOT NULL,
    minimum_contiguous_weeks   INTEGER NOT NULL
);

INSERT INTO rotations (rotation, category, required_role, minimum_weeks, maximum_weeks, minimum_residents_assigned, maximum_residents_assigned, minimum_contiguous_weeks) VALUES ('Green HS Senior', 'HS Rounding Senior', 'Senior', 0, 8, 1, 1, 2);
INSERT INTO rotations (rotation, category, required_role, minimum_weeks, maximum_weeks, minimum_residents_assigned, maximum_residents_assigned, minimum_contiguous_weeks) VALUES ('Orange HS Senior', 'HS Rounding Senior', 'Senior', 0, 8, 1, 1, 2);
INSERT INTO rotations (rotation, category, required_role, minimum_weeks, maximum_weeks, minimum_residents_assigned, maximum_residents_assigned, minimum_contiguous_weeks) VALUES ('SHMC Consults', 'Hospitalist', 'Senior', 0, 4, 0, 1, 1);
INSERT INTO rotations (rotation, category, required_role, minimum_weeks, maximum_weeks, minimum_residents_assigned, maximum_residents_assigned, minimum_contiguous_weeks) VALUES ('SHMC Admitting', 'Hospitalist', 'Senior', 0, 4, 0, 1, 1);
INSERT INTO rotations (rotation, category, required_role, minimum_weeks, maximum_weeks, minimum_residents_assigned, maximum_residents_assigned, minimum_contiguous_weeks) VALUES ('Orange HS Intern', 'HS Rounding Intern', 'Any Intern', 0, 8, 2, 2, 4);
INSERT INTO rotations (rotation, category, required_role, minimum_weeks, maximum_weeks, minimum_residents_assigned, maximum_residents_assigned, minimum_contiguous_weeks) VALUES ('Green HS Intern', 'HS Rounding Intern', 'Any Intern', 0, 8, 2, 2, 4);
INSERT INTO rotations (rotation, category, required_role, minimum_weeks, maximum_weeks, minimum_residents_assigned, maximum_residents_assigned, minimum_contiguous_weeks) VALUES ('Purple HS Senior', 'HS Admitting Senior', 'Senior', 8, 8, 1, 1, 1);
INSERT INTO rotations (rotation, category, required_role, minimum_weeks, maximum_weeks, minimum_residents_assigned, maximum_residents_assigned, minimum_contiguous_weeks) VALUES ('Purple HS Intern', 'HS Admitting Intern', 'Any Intern', 4, 4, 1, 1, 1);
INSERT INTO rotations (rotation, category, required_role, minimum_weeks, maximum_weeks, minimum_residents_assigned, maximum_residents_assigned, minimum_contiguous_weeks) VALUES ('Providence Endocrinology', 'Endocrinology Specialty', 'Senior', 0, 4, 0, 1, 1);
INSERT INTO rotations (rotation, category, required_role, minimum_weeks, maximum_weeks, minimum_residents_assigned, maximum_residents_assigned, minimum_contiguous_weeks) VALUES ('DH Rounding', 'Hospitalist', 'Senior', 0, 4, 0, 1, 1);
INSERT INTO rotations (rotation, category, required_role, minimum_weeks, maximum_weeks, minimum_residents_assigned, maximum_residents_assigned, minimum_contiguous_weeks) VALUES ('SHMC Rounding', 'Hospitalist', 'Senior', 0, 4, 0, 2, 1);
INSERT INTO rotations (rotation, category, required_role, minimum_weeks, maximum_weeks, minimum_residents_assigned, maximum_residents_assigned, minimum_contiguous_weeks) VALUES ('Providence Pulmonology', 'Pulmonology Specialty', 'Senior', 0, 4, 0, 1, 1);
INSERT INTO rotations (rotation, category, required_role, minimum_weeks, maximum_weeks, minimum_residents_assigned, maximum_residents_assigned, minimum_contiguous_weeks) VALUES ('Rheum To Grow Rheumatology Modules', 'Rheumatology Speciality', 'Senior', 0, 2, 0, 4, 1);
INSERT INTO rotations (rotation, category, required_role, minimum_weeks, maximum_weeks, minimum_residents_assigned, maximum_residents_assigned, minimum_contiguous_weeks) VALUES ('STHC Intern', 'Primary Care Intern', 'IM Intern', 8, 8, 0, 5, 1);
INSERT INTO rotations (rotation, category, required_role, minimum_weeks, maximum_weeks, minimum_residents_assigned, maximum_residents_assigned, minimum_contiguous_weeks) VALUES ('STHC Senior Non-Ambulatory', 'Primary Care Senior', 'Senior', 4, 4, 0, 5, 1);
INSERT INTO rotations (rotation, category, required_role, minimum_weeks, maximum_weeks, minimum_residents_assigned, maximum_residents_assigned, minimum_contiguous_weeks) VALUES ('SHMC Night Senior', 'Night Senior', 'Senior', 8, 8, 1, 2, 2);
INSERT INTO rotations (rotation, category, required_role, minimum_weeks, maximum_weeks, minimum_residents_assigned, maximum_residents_assigned, minimum_contiguous_weeks) VALUES ('SHMC Night Intern', 'SHMC Night Intern', 'Any Intern', 4, 4, 2, 2, 4);
INSERT INTO rotations (rotation, category, required_role, minimum_weeks, maximum_weeks, minimum_residents_assigned, maximum_residents_assigned, minimum_contiguous_weeks) VALUES ('CCNW Heme/Onc', 'Heme/Onc Specialty', 'Senior', 0, 4, 0, 1, 1);
INSERT INTO rotations (rotation, category, required_role, minimum_weeks, maximum_weeks, minimum_residents_assigned, maximum_residents_assigned, minimum_contiguous_weeks) VALUES ('Multicare Heme/Onc', 'Heme/Onc Specialty', 'Senior', 0, 4, 0, 1, 1);
INSERT INTO rotations (rotation, category, required_role, minimum_weeks, maximum_weeks, minimum_residents_assigned, maximum_residents_assigned, minimum_contiguous_weeks) VALUES ('DH ICU Senior', 'ICU Senior', 'Senior', 0, 4, 1, 1, 4);
INSERT INTO rotations (rotation, category, required_role, minimum_weeks, maximum_weeks, minimum_residents_assigned, maximum_residents_assigned, minimum_contiguous_weeks) VALUES ('SHMC CICU', 'ICU Senior', 'Senior', 0, 4, 0, 1, 1);
INSERT INTO rotations (rotation, category, required_role, minimum_weeks, maximum_weeks, minimum_residents_assigned, maximum_residents_assigned, minimum_contiguous_weeks) VALUES ('STHC Senior Ambulatory', 'Primary Care Senior', 'Senior', 4, 4, 1, 1, 1);
INSERT INTO rotations (rotation, category, required_role, minimum_weeks, maximum_weeks, minimum_residents_assigned, maximum_residents_assigned, minimum_contiguous_weeks) VALUES ('Multicare Endocrinology', 'Endocrinology Specialty', 'Senior', 0, 4, 0, 2, 2);
INSERT INTO rotations (rotation, category, required_role, minimum_weeks, maximum_weeks, minimum_residents_assigned, maximum_residents_assigned, minimum_contiguous_weeks) VALUES ('Vacation', 'Vacation', 'Any', 3, 3, 0, 5, 1);
INSERT INTO rotations (rotation, category, required_role, minimum_weeks, maximum_weeks, minimum_residents_assigned, maximum_residents_assigned, minimum_contiguous_weeks) VALUES ('TY Elective', 'TY Elective', 'TY_Intern', 0, 23, 0, 8, 4);
INSERT INTO rotations (rotation, category, required_role, minimum_weeks, maximum_weeks, minimum_residents_assigned, maximum_residents_assigned, minimum_contiguous_weeks) VALUES ('PMR Elective', 'PMR Elective', 'PMR_Intern', 0, 23, 0, 8, 4);

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

INSERT INTO rotations_completed (resident, weeks, rotation, start_date) VALUES ('Tyler Willis DO', 4, 'Green HS Senior', NULL);
INSERT INTO rotations_completed (resident, weeks, rotation, start_date) VALUES ('Tyler Willis DO', 4, 'SHMC Night Senior', '2025-06-06');
INSERT INTO rotations_completed (resident, weeks, rotation, start_date) VALUES ('Shannon Pierce DO', 4, 'SHMC Night Intern', '2025-01-01');

-- Table: weeks
CREATE TABLE IF NOT EXISTS weeks (
    monday_date            TEXT    NOT NULL
                                   UNIQUE,
    week                   INTEGER NOT NULL,
    starting_academic_year INTEGER NOT NULL,
    ending_academic_year   INTEGER NOT NULL
);

INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2025-06-23', 1, 2025, 2026);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2025-06-30', 2, 2025, 2026);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2025-07-07', 3, 2025, 2026);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2025-07-14', 4, 2025, 2026);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2025-07-21', 5, 2025, 2026);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2025-07-28', 6, 2025, 2026);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2025-08-04', 7, 2025, 2026);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2025-08-11', 8, 2025, 2026);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2025-08-18', 9, 2025, 2026);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2025-08-25', 10, 2025, 2026);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2025-09-01', 11, 2025, 2026);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2025-09-08', 12, 2025, 2026);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2025-09-15', 13, 2025, 2026);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2025-09-22', 14, 2025, 2026);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2025-09-29', 15, 2025, 2026);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2025-10-06', 16, 2025, 2026);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2025-10-13', 17, 2025, 2026);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2025-10-20', 18, 2025, 2026);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2025-10-27', 19, 2025, 2026);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2025-11-03', 20, 2025, 2026);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2025-11-10', 21, 2025, 2026);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2025-11-17', 22, 2025, 2026);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2025-11-24', 23, 2025, 2026);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2025-12-01', 24, 2025, 2026);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2025-12-08', 25, 2025, 2026);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2025-12-15', 26, 2025, 2026);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2025-12-22', 27, 2025, 2026);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2025-12-29', 28, 2025, 2026);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2026-01-05', 29, 2025, 2026);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2026-01-12', 30, 2025, 2026);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2026-01-19', 31, 2025, 2026);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2026-01-26', 32, 2025, 2026);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2026-02-02', 33, 2025, 2026);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2026-02-09', 34, 2025, 2026);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2026-02-16', 35, 2025, 2026);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2026-02-23', 36, 2025, 2026);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2026-03-02', 37, 2025, 2026);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2026-03-09', 38, 2025, 2026);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2026-03-16', 39, 2025, 2026);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2026-03-23', 40, 2025, 2026);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2026-03-30', 41, 2025, 2026);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2026-04-06', 42, 2025, 2026);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2026-04-13', 43, 2025, 2026);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2026-04-20', 44, 2025, 2026);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2026-04-27', 45, 2025, 2026);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2026-05-04', 46, 2025, 2026);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2026-05-11', 47, 2025, 2026);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2026-05-18', 48, 2025, 2026);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2026-05-25', 49, 2025, 2026);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2026-06-01', 50, 2025, 2026);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2026-06-08', 51, 2025, 2026);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2026-06-15', 52, 2025, 2026);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2026-06-22', 1, 2026, 2027);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2026-06-29', 2, 2026, 2027);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2026-07-06', 3, 2026, 2027);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2026-07-13', 4, 2026, 2027);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2026-07-20', 5, 2026, 2027);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2026-07-27', 6, 2026, 2027);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2026-08-03', 7, 2026, 2027);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2026-08-10', 8, 2026, 2027);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2026-08-17', 9, 2026, 2027);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2026-08-24', 10, 2026, 2027);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2026-08-31', 11, 2026, 2027);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2026-09-07', 12, 2026, 2027);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2026-09-14', 13, 2026, 2027);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2026-09-21', 14, 2026, 2027);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2026-09-28', 15, 2026, 2027);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2026-10-05', 16, 2026, 2027);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2026-10-12', 17, 2026, 2027);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2026-10-19', 18, 2026, 2027);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2026-10-26', 19, 2026, 2027);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2026-11-02', 20, 2026, 2027);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2026-11-09', 21, 2026, 2027);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2026-11-16', 22, 2026, 2027);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2026-11-23', 23, 2026, 2027);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2026-11-30', 24, 2026, 2027);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2026-12-07', 25, 2026, 2027);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2026-12-14', 26, 2026, 2027);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2026-12-21', 27, 2026, 2027);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2026-12-28', 28, 2026, 2027);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2027-01-04', 29, 2026, 2027);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2027-01-11', 30, 2026, 2027);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2027-01-18', 31, 2026, 2027);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2027-01-25', 32, 2026, 2027);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2027-02-01', 33, 2026, 2027);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2027-02-08', 34, 2026, 2027);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2027-02-15', 35, 2026, 2027);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2027-02-22', 36, 2026, 2027);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2027-03-01', 37, 2026, 2027);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2027-03-08', 38, 2026, 2027);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2027-03-15', 39, 2026, 2027);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2027-03-22', 40, 2026, 2027);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2027-03-29', 41, 2026, 2027);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2027-04-05', 42, 2026, 2027);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2027-04-12', 43, 2026, 2027);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2027-04-19', 44, 2026, 2027);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2027-04-26', 45, 2026, 2027);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2027-05-03', 46, 2026, 2027);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2027-05-10', 47, 2026, 2027);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2027-05-17', 48, 2026, 2027);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2027-05-24', 49, 2026, 2027);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2027-05-31', 50, 2026, 2027);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2027-06-07', 51, 2026, 2027);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2027-06-14', 52, 2026, 2027);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2027-06-21', 53, 2026, 2027);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2027-06-28', 1, 2027, 2028);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2027-07-05', 2, 2027, 2028);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2027-07-12', 3, 2027, 2028);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2027-07-19', 4, 2027, 2028);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2027-07-26', 5, 2027, 2028);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2027-08-02', 6, 2027, 2028);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2027-08-09', 7, 2027, 2028);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2027-08-16', 8, 2027, 2028);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2027-08-23', 9, 2027, 2028);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2027-08-30', 10, 2027, 2028);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2027-09-06', 11, 2027, 2028);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2027-09-13', 12, 2027, 2028);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2027-09-20', 13, 2027, 2028);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2027-09-27', 14, 2027, 2028);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2027-10-04', 15, 2027, 2028);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2027-10-11', 16, 2027, 2028);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2027-10-18', 17, 2027, 2028);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2027-10-25', 18, 2027, 2028);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2027-11-01', 19, 2027, 2028);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2027-11-08', 20, 2027, 2028);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2027-11-15', 21, 2027, 2028);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2027-11-22', 22, 2027, 2028);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2027-11-29', 23, 2027, 2028);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2027-12-06', 24, 2027, 2028);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2027-12-13', 25, 2027, 2028);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2027-12-20', 26, 2027, 2028);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2027-12-27', 27, 2027, 2028);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2028-01-03', 28, 2027, 2028);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2028-01-10', 29, 2027, 2028);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2028-01-17', 30, 2027, 2028);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2028-01-24', 31, 2027, 2028);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2028-01-31', 32, 2027, 2028);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2028-02-07', 33, 2027, 2028);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2028-02-14', 34, 2027, 2028);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2028-02-21', 35, 2027, 2028);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2028-02-28', 36, 2027, 2028);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2028-03-06', 37, 2027, 2028);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2028-03-13', 38, 2027, 2028);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2028-03-20', 39, 2027, 2028);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2028-03-27', 40, 2027, 2028);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2028-04-03', 41, 2027, 2028);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2028-04-10', 42, 2027, 2028);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2028-04-17', 43, 2027, 2028);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2028-04-24', 44, 2027, 2028);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2028-05-01', 45, 2027, 2028);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2028-05-08', 46, 2027, 2028);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2028-05-15', 47, 2027, 2028);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2028-05-22', 48, 2027, 2028);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2028-05-29', 49, 2027, 2028);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2028-06-05', 50, 2027, 2028);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2028-06-12', 51, 2027, 2028);
INSERT INTO weeks (monday_date, week, starting_academic_year, ending_academic_year) VALUES ('2028-06-19', 52, 2027, 2028);

-- View: get_active_reqs_as_categories
CREATE VIEW IF NOT EXISTS get_active_reqs_as_categories AS
    SELECT *
      FROM residents
           INNER JOIN
           categories ON residents.role = categories.pertinent_role;


-- View: requirements_vs_completions
CREATE VIEW IF NOT EXISTS requirements_vs_completions AS
    SELECT *
      FROM get_active_reqs_as_categories
           INNER JOIN
           resident_requirements_done ON get_active_reqs_as_categories.category_name = resident_requirements_done.category;


-- View: resident_requirements_done
CREATE VIEW IF NOT EXISTS resident_requirements_done AS
    SELECT *
      FROM rotations_completed
           INNER JOIN
           rotations ON rotations_completed.rotation = rotations.rotation/* INNER JOIN
       residents ON rotations_completed.resident = residents.full_name */;


COMMIT TRANSACTION;
PRAGMA foreign_keys = on;
