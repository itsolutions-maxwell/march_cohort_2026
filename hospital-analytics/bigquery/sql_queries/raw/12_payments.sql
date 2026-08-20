-- RAW LAYER — payments

CREATE OR REPLACE VIEW `hospitalanalytics-504701.raw.payments` AS
SELECT 'hospital_a' AS hospital_id, payment_id, encounter_id, patient_user_id, amount, paid_at
FROM `hospitalanalytics-504701.hospital_a.payments`

UNION ALL

SELECT 'hospital_b' AS hospital_id, payment_id, encounter_id, patient_user_id, amount, paid_at
FROM `hospitalanalytics-504701.hospital_b.payments`

UNION ALL

SELECT 'hospital_c' AS hospital_id, payment_id, encounter_id, patient_user_id, amount, paid_at
FROM `hospitalanalytics-504701.hospital_c.payments`;
