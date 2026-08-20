-- RAW LAYER — encounters
-- department and expected_discharge_date are recently added columns — rows
-- created before that migration come through NULL, same as patients.payer_type.

CREATE OR REPLACE VIEW `hospitalanalytics-504701.raw.encounters` AS
SELECT
  'hospital_a' AS hospital_id, encounter_id, patient_user_id, attending_staff_user_id,
  encounter_type, reason, department, expected_discharge_date, created_at
FROM `hospitalanalytics-504701.hospital_a.encounters`

UNION ALL

SELECT
  'hospital_b' AS hospital_id, encounter_id, patient_user_id, attending_staff_user_id,
  encounter_type, reason, department, expected_discharge_date, created_at
FROM `hospitalanalytics-504701.hospital_b.encounters`

UNION ALL

SELECT
  'hospital_c' AS hospital_id, encounter_id, patient_user_id, attending_staff_user_id,
  encounter_type, reason, department, expected_discharge_date, created_at
FROM `hospitalanalytics-504701.hospital_c.encounters`;
