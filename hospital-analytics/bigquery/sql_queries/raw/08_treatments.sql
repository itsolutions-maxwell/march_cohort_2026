-- RAW LAYER — treatments
-- category is a recently added column — older rows come through NULL.

CREATE OR REPLACE VIEW `hospitalanalytics-504701.raw.treatments` AS
SELECT
  'hospital_a' AS hospital_id, treatment_id, encounter_id, staff_user_id,
  treatment_type, category, notes, administered_at
FROM `hospitalanalytics-504701.hospital_a.treatments`

UNION ALL

SELECT
  'hospital_b' AS hospital_id, treatment_id, encounter_id, staff_user_id,
  treatment_type, category, notes, administered_at
FROM `hospitalanalytics-504701.hospital_b.treatments`

UNION ALL

SELECT
  'hospital_c' AS hospital_id, treatment_id, encounter_id, staff_user_id,
  treatment_type, category, notes, administered_at
FROM `hospitalanalytics-504701.hospital_c.treatments`;
