-- SILVER LAYER — billing
-- One row per charge, enriched with the department/payer/encounter type it
-- belongs to. Rolling this up against payments into "outstanding" is an
-- aggregate question, so that math lives in gold, not here — silver stays
-- at the same grain as the source (one row per charge).

CREATE OR REPLACE VIEW `hospitalanalytics-504701.silver.billing` AS
SELECT
  b.hospital_id,
  b.charge_id,
  b.encounter_id,
  b.patient_user_id,
  p.payer_type,
  e.department,
  e.encounter_type,
  b.charge_type,
  COALESCE(NULLIF(TRIM(b.description), ''), INITCAP(b.charge_type)) AS description,
  b.amount,
  b.created_at
FROM `hospitalanalytics-504701.raw.billing_charges` b
LEFT JOIN `hospitalanalytics-504701.silver.patients` p
  ON p.hospital_id = b.hospital_id AND p.patient_user_id = b.patient_user_id
LEFT JOIN `hospitalanalytics-504701.silver.encounters` e
  ON e.hospital_id = b.hospital_id AND e.encounter_id = b.encounter_id
WHERE b.amount IS NOT NULL AND b.amount > 0;
