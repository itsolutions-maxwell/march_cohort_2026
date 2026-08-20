-- SILVER LAYER — treatments
-- Same "resolve current state" pattern as encounters: a treatment is
-- "pending" if no test_completions row exists yet for it. Turnaround time
-- only makes sense once it's resolved, so it's NULL until then.

CREATE OR REPLACE VIEW `hospitalanalytics-504701.silver.treatments` AS
SELECT
  t.hospital_id,
  t.treatment_id,
  t.encounter_id,
  t.staff_user_id,
  s.full_name AS staff_name,
  t.treatment_type,
  COALESCE(t.category, 'other') AS category,
  t.notes,
  t.administered_at AS ordered_at,
  c.completed_at,
  c.result_notes,
  c.completed_at IS NULL AS is_pending,
  IF(
    c.completed_at IS NOT NULL,
    TIMESTAMP_DIFF(c.completed_at, t.administered_at, MINUTE) / 60.0,
    NULL
  ) AS turnaround_hours
FROM `hospitalanalytics-504701.raw.treatments` t
LEFT JOIN `hospitalanalytics-504701.silver.staff` s
  ON s.hospital_id = t.hospital_id AND s.staff_user_id = t.staff_user_id
LEFT JOIN `hospitalanalytics-504701.raw.test_completions` c
  ON c.hospital_id = t.hospital_id AND c.treatment_id = t.treatment_id;
