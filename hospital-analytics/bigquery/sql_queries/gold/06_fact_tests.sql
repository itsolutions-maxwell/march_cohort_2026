-- GOLD LAYER — fact_tests
-- Powers: tests performed today, pending tests, tests by category, average
-- turnaround. is_test separates lab/imaging/pathology (which get a
-- pending -> result lifecycle) from procedures/medications (logged as
-- already-done, no turnaround to measure).

CREATE OR REPLACE VIEW `hospitalanalytics-504701.gold.fact_tests` AS
SELECT
  hospital_id,
  treatment_id,
  encounter_id,
  staff_user_id,
  staff_name,
  treatment_type,
  category,
  category IN ('blood_work', 'x_ray', 'ct', 'mri', 'ultrasound', 'pathology') AS is_test,
  ordered_at,
  DATE(ordered_at) AS ordered_date,
  completed_at,
  is_pending,
  turnaround_hours
FROM `hospitalanalytics-504701.silver.treatments`;
