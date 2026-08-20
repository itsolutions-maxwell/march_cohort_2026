-- RAW LAYER — staff_profiles

CREATE OR REPLACE VIEW `hospitalanalytics-504701.raw.staff_profiles` AS
SELECT 'hospital_a' AS hospital_id, staff_user_id, department, title, created_at
FROM `hospitalanalytics-504701.hospital_a.staff_profiles`

UNION ALL

SELECT 'hospital_b' AS hospital_id, staff_user_id, department, title, created_at
FROM `hospitalanalytics-504701.hospital_b.staff_profiles`

UNION ALL

SELECT 'hospital_c' AS hospital_id, staff_user_id, department, title, created_at
FROM `hospitalanalytics-504701.hospital_c.staff_profiles`;
