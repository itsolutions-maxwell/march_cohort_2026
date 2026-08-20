-- GOLD LAYER — fact_billing
-- One row per charge (same grain as silver.billing) — this is the shape
-- you group by department/service/date for revenue breakdowns. For the
-- charged-vs-paid-vs-outstanding rollup, see fact_receivables.

CREATE OR REPLACE VIEW `hospitalanalytics-504701.gold.fact_billing` AS
SELECT
  hospital_id,
  charge_id,
  encounter_id,
  patient_user_id,
  payer_type,
  department,
  encounter_type,
  charge_type,
  description,
  amount,
  created_at,
  DATE(created_at) AS charge_date
FROM `hospitalanalytics-504701.silver.billing`;
