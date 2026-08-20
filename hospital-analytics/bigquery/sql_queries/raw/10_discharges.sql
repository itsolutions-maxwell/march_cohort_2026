-- RAW LAYER — discharges

CREATE OR REPLACE VIEW `hospitalanalytics-504701.raw.discharges` AS
SELECT 'hospital_a' AS hospital_id, discharge_id, encounter_id, staff_user_id, discharge_notes, discharged_at
FROM `hospitalanalytics-504701.hospital_a.discharges`

UNION ALL

SELECT 'hospital_b' AS hospital_id, discharge_id, encounter_id, staff_user_id, discharge_notes, discharged_at
FROM `hospitalanalytics-504701.hospital_b.discharges`

UNION ALL

SELECT 'hospital_c' AS hospital_id, discharge_id, encounter_id, staff_user_id, discharge_notes, discharged_at
FROM `hospitalanalytics-504701.hospital_c.discharges`;
