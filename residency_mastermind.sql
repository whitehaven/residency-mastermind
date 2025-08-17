--
-- File generated with SQLiteStudio v3.4.17 on Sat Aug 16 18:42:23 2025
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
INSERT INTO categories (category_name, minimum_weeks, maximum_weeks, pertinent_role, elective) VALUES ('TY Elective', 0, 23, 'TY', 'elective');
INSERT INTO categories (category_name, minimum_weeks, maximum_weeks, pertinent_role, elective) VALUES ('PMR Elective', 0, 23, 'PMR', 'elective');
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
    week             INTEGER UNIQUE,
    week_monday_date TEXT    UNIQUE
                             CHECK (date(week_monday_date) NOT NULL) 
                             PRIMARY KEY
);

INSERT INTO weeks (week, week_monday_date) VALUES (0, '2025-07-07');
INSERT INTO weeks (week, week_monday_date) VALUES (1, '2025-07-14');
INSERT INTO weeks (week, week_monday_date) VALUES (2, '2025-07-21');
INSERT INTO weeks (week, week_monday_date) VALUES (3, '2025-07-28');
INSERT INTO weeks (week, week_monday_date) VALUES (4, '2025-08-04');
INSERT INTO weeks (week, week_monday_date) VALUES (5, '2025-08-11');
INSERT INTO weeks (week, week_monday_date) VALUES (6, '2025-08-18');
INSERT INTO weeks (week, week_monday_date) VALUES (7, '2025-08-25');
INSERT INTO weeks (week, week_monday_date) VALUES (8, '2025-09-01');
INSERT INTO weeks (week, week_monday_date) VALUES (9, '2025-09-08');
INSERT INTO weeks (week, week_monday_date) VALUES (10, '2025-09-15');
INSERT INTO weeks (week, week_monday_date) VALUES (11, '2025-09-22');
INSERT INTO weeks (week, week_monday_date) VALUES (12, '2025-09-29');
INSERT INTO weeks (week, week_monday_date) VALUES (13, '2025-10-06');
INSERT INTO weeks (week, week_monday_date) VALUES (14, '2025-10-13');
INSERT INTO weeks (week, week_monday_date) VALUES (15, '2025-10-20');
INSERT INTO weeks (week, week_monday_date) VALUES (16, '2025-10-27');
INSERT INTO weeks (week, week_monday_date) VALUES (17, '2025-11-03');
INSERT INTO weeks (week, week_monday_date) VALUES (18, '2025-11-10');
INSERT INTO weeks (week, week_monday_date) VALUES (19, '2025-11-17');
INSERT INTO weeks (week, week_monday_date) VALUES (20, '2025-11-24');
INSERT INTO weeks (week, week_monday_date) VALUES (21, '2025-12-01');
INSERT INTO weeks (week, week_monday_date) VALUES (22, '2025-12-08');
INSERT INTO weeks (week, week_monday_date) VALUES (23, '2025-12-15');
INSERT INTO weeks (week, week_monday_date) VALUES (24, '2025-12-22');
INSERT INTO weeks (week, week_monday_date) VALUES (25, '2025-12-29');
INSERT INTO weeks (week, week_monday_date) VALUES (26, '2026-01-05');
INSERT INTO weeks (week, week_monday_date) VALUES (27, '2026-01-12');
INSERT INTO weeks (week, week_monday_date) VALUES (28, '2026-01-19');
INSERT INTO weeks (week, week_monday_date) VALUES (29, '2026-01-26');
INSERT INTO weeks (week, week_monday_date) VALUES (30, '2026-02-02');
INSERT INTO weeks (week, week_monday_date) VALUES (31, '2026-02-09');
INSERT INTO weeks (week, week_monday_date) VALUES (32, '2026-02-16');
INSERT INTO weeks (week, week_monday_date) VALUES (33, '2026-02-23');
INSERT INTO weeks (week, week_monday_date) VALUES (34, '2026-03-02');
INSERT INTO weeks (week, week_monday_date) VALUES (35, '2026-03-09');
INSERT INTO weeks (week, week_monday_date) VALUES (36, '2026-03-16');
INSERT INTO weeks (week, week_monday_date) VALUES (37, '2026-03-23');
INSERT INTO weeks (week, week_monday_date) VALUES (38, '2026-03-30');
INSERT INTO weeks (week, week_monday_date) VALUES (39, '2026-04-06');
INSERT INTO weeks (week, week_monday_date) VALUES (40, '2026-04-13');
INSERT INTO weeks (week, week_monday_date) VALUES (41, '2026-04-20');
INSERT INTO weeks (week, week_monday_date) VALUES (42, '2026-04-27');
INSERT INTO weeks (week, week_monday_date) VALUES (43, '2026-05-04');
INSERT INTO weeks (week, week_monday_date) VALUES (44, '2026-05-11');
INSERT INTO weeks (week, week_monday_date) VALUES (45, '2026-05-18');
INSERT INTO weeks (week, week_monday_date) VALUES (46, '2026-05-25');
INSERT INTO weeks (week, week_monday_date) VALUES (47, '2026-06-01');
INSERT INTO weeks (week, week_monday_date) VALUES (48, '2026-06-08');
INSERT INTO weeks (week, week_monday_date) VALUES (49, '2026-06-15');
INSERT INTO weeks (week, week_monday_date) VALUES (50, '2026-06-22');
INSERT INTO weeks (week, week_monday_date) VALUES (51, '2026-06-29');

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
