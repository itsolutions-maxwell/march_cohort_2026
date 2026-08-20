-- RAW LAYER — test_completions

CREATE OR REPLACE VIEW `hospitalanalytics-504701.raw.test_completions` AS
SELECT 'hospital_a' AS hospital_id, test_completion_id, treatment_id, staff_user_id, result_notes, completed_at
FROM `hospitalanalytics-504701.hospital_a.test_completions`

UNION ALL

SELECT 'hospital_b' AS hospital_id, test_completion_id, treatment_id, staff_user_id, result_notes, completed_at
FROM `hospitalanalytics-504701.hospital_b.test_completions`

UNION ALL

SELECT 'hospital_c' AS hospital_id, test_completion_id, treatment_id, staff_user_id, result_notes, completed_at
FROM `hospitalanalytics-504701.hospital_c.test_completions`;
