-- SILVER LAYER — data quality check: possible duplicate patients
-- This does NOT dedupe or merge anything. Hospitals are separate tenants
-- in this schema on purpose, so a same-named patient at two hospitals
-- might be two different real people, or genuinely the same person with
-- two separate charts. This view just surfaces the candidates for a human
-- (or a follow-up identity-matching rule) to review — that's the honest
-- thing a silver layer can do when it can't be sure two rows are the same
-- entity.
--
-- This is bigquery/sql_queries/duplicate_patients.sql's idea, fixed and
-- rebuilt on top of the medallion layers: the original only checked
-- hospital_a and hospital_b (hospital_c was missing entirely), and matched
-- against the raw users table directly. This version runs against all
-- three hospitals via silver.users, which is already deduped and cleaned.

CREATE OR REPLACE VIEW `hospitalanalytics-504701.silver.duplicate_patient_candidates` AS
WITH named_patients AS (
  SELECT
    hospital_id,
    user_id,
    email,
    full_name,
    LOWER(TRIM(full_name)) AS normalized_name
  FROM `hospitalanalytics-504701.silver.users`
  WHERE role = 'patient'
),
name_hospital_counts AS (
  SELECT
    normalized_name,
    COUNT(DISTINCT hospital_id) AS hospital_count
  FROM named_patients
  GROUP BY normalized_name
  HAVING COUNT(DISTINCT hospital_id) > 1
)
SELECT
  np.hospital_id,
  np.full_name,
  np.email,
  nhc.hospital_count AS hospitals_with_this_name
FROM named_patients np
JOIN name_hospital_counts nhc ON nhc.normalized_name = np.normalized_name
ORDER BY np.normalized_name, np.hospital_id;
