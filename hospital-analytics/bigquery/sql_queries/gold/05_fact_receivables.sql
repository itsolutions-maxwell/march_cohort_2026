-- GOLD LAYER — fact_receivables
-- One row per encounter: total charged, total paid, outstanding balance.
-- This is the encounter-level rollup fact_billing intentionally doesn't
-- do — charges and payments are recorded at different grains (per line
-- item vs. per encounter), so the aggregation belongs here in gold.

CREATE OR REPLACE VIEW `hospitalanalytics-504701.gold.fact_receivables` AS
WITH charges AS (
  SELECT hospital_id, encounter_id, patient_user_id, SUM(amount) AS total_charged
  FROM `hospitalanalytics-504701.silver.billing`
  GROUP BY hospital_id, encounter_id, patient_user_id
),
payments AS (
  SELECT hospital_id, encounter_id, SUM(amount) AS total_paid
  FROM `hospitalanalytics-504701.raw.payments`
  GROUP BY hospital_id, encounter_id
)
SELECT
  c.hospital_id,
  c.encounter_id,
  c.patient_user_id,
  c.total_charged,
  COALESCE(p.total_paid, 0) AS total_paid,
  c.total_charged - COALESCE(p.total_paid, 0) AS outstanding_balance
FROM charges c
LEFT JOIN payments p
  ON p.hospital_id = c.hospital_id AND p.encounter_id = c.encounter_id;
