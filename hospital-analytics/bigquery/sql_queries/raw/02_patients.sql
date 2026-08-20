-- RAW LAYER — patients
-- payer_type is a recently added column: rows created before that migration
-- will just come through NULL here. That's expected and fine for raw —
-- silver is where we decide what to do about it.

CREATE OR REPLACE VIEW `hospitalanalytics-504701.raw.patients` AS
SELECT 'hospital_a' AS hospital_id, patient_user_id, date_of_birth, gender, phone, blood_type, payer_type, created_at
FROM `hospitalanalytics-504701.hospital_a.patients`

UNION ALL

SELECT 'hospital_b' AS hospital_id, patient_user_id, date_of_birth, gender, phone, blood_type, payer_type, created_at
FROM `hospitalanalytics-504701.hospital_b.patients`

UNION ALL

SELECT 'hospital_c' AS hospital_id, patient_user_id, date_of_birth, gender, phone, blood_type, payer_type, created_at
FROM `hospitalanalytics-504701.hospital_c.patients`;
