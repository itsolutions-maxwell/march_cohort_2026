-- SILVER LAYER — patients
-- Joins the cleaned identity (silver.users) to the patient profile, fills
-- in sensible defaults for the nulls raw is full of (old rows predate
-- payer_type; blood_type/gender are sometimes left blank), and derives age
-- from date_of_birth since nothing captures age directly.

CREATE OR REPLACE VIEW `hospitalanalytics-504701.silver.patients` AS
SELECT
  u.hospital_id,
  u.user_id AS patient_user_id,
  u.first_name,
  u.last_name,
  u.full_name,
  u.email,
  p.date_of_birth,
  DATE_DIFF(CURRENT_DATE(), p.date_of_birth, YEAR) AS age,
  COALESCE(NULLIF(LOWER(TRIM(p.gender)), ''), 'unknown') AS gender,
  p.phone,
  COALESCE(p.blood_type, 'unknown') AS blood_type,
  -- payer_type didn't exist before this schema revision; treat unlabeled
  -- historical patients as self-pay rather than silently dropping them.
  COALESCE(p.payer_type, 'self_pay') AS payer_type,
  p.created_at
FROM `hospitalanalytics-504701.silver.users` u
JOIN `hospitalanalytics-504701.raw.patients` p
  ON p.hospital_id = u.hospital_id AND p.patient_user_id = u.user_id
WHERE u.role = 'patient';
