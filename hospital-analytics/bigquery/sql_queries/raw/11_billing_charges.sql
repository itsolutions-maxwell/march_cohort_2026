-- RAW LAYER — billing_charges

CREATE OR REPLACE VIEW `hospitalanalytics-504701.raw.billing_charges` AS
SELECT 'hospital_a' AS hospital_id, charge_id, encounter_id, patient_user_id, charge_type, description, amount, created_at
FROM `hospitalanalytics-504701.hospital_a.billing_charges`

UNION ALL

SELECT 'hospital_b' AS hospital_id, charge_id, encounter_id, patient_user_id, charge_type, description, amount, created_at
FROM `hospitalanalytics-504701.hospital_b.billing_charges`

UNION ALL

SELECT 'hospital_c' AS hospital_id, charge_id, encounter_id, patient_user_id, charge_type, description, amount, created_at
FROM `hospitalanalytics-504701.hospital_c.billing_charges`;
