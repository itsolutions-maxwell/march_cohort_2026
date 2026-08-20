-- GOLD LAYER — fact_encounters
-- Powers: admissions/discharges today, current inpatient count, LOS,
-- readmission rate, ER-today, emergency vs. scheduled, patients by
-- department/age group. Adds dashboard-shaped buckets (age group,
-- is_emergency, days_since_admission for still-active stays) on top of
-- silver.encounters' already-resolved current state.

CREATE OR REPLACE VIEW `hospitalanalytics-504701.gold.fact_encounters` AS
SELECT
  hospital_id,
  encounter_id,
  patient_user_id,
  patient_name,
  CASE
    WHEN patient_age IS NULL THEN 'Unknown'
    WHEN patient_age < 18 THEN '0-17'
    WHEN patient_age < 35 THEN '18-34'
    WHEN patient_age < 50 THEN '35-49'
    WHEN patient_age < 65 THEN '50-64'
    ELSE '65+'
  END AS patient_age_group,
  attending_staff_user_id,
  attending_staff_name,
  department,
  encounter_type,
  encounter_type = 'emergency' AS is_emergency,
  reason,
  admitted_at,
  DATE(admitted_at) AS admitted_date,
  expected_discharge_date,
  current_room_id,
  current_room_number,
  current_room_type,
  current_room_type_label,
  discharged_at,
  DATE(discharged_at) AS discharged_date,
  discharge_notes,
  is_discharged,
  length_of_stay_days,
  IF(NOT is_discharged, TIMESTAMP_DIFF(CURRENT_TIMESTAMP(), admitted_at, HOUR) / 24.0, NULL) AS days_since_admission
FROM `hospitalanalytics-504701.silver.encounters`;
