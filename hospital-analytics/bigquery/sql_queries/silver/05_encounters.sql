-- SILVER LAYER — encounters
-- This is the important one: bronze never stores "is this encounter still
-- active" or "what room are they in right now" as a column — the app is
-- insert-only (no UPDATE on this BigQuery tier), so every state change is
-- its own row, and "current state" has to be derived from the latest one.
-- This view does that resolution ONCE, in SQL, so every dashboard query
-- downstream just reads a column instead of re-deriving it.

CREATE OR REPLACE VIEW `hospitalanalytics-504701.silver.encounters` AS
WITH latest_room AS (
  SELECT
    hospital_id, encounter_id, room_id,
    ROW_NUMBER() OVER (PARTITION BY hospital_id, encounter_id ORDER BY assigned_at DESC) AS rn
  FROM `hospitalanalytics-504701.raw.room_assignments`
),
current_room AS (
  SELECT hospital_id, encounter_id, room_id FROM latest_room WHERE rn = 1
),
latest_discharge AS (
  SELECT
    hospital_id, encounter_id, discharge_notes, discharged_at,
    ROW_NUMBER() OVER (PARTITION BY hospital_id, encounter_id ORDER BY discharged_at DESC) AS rn
  FROM `hospitalanalytics-504701.raw.discharges`
)
SELECT
  e.hospital_id,
  e.encounter_id,
  e.patient_user_id,
  p.full_name AS patient_name,
  p.age AS patient_age,
  e.attending_staff_user_id,
  s.full_name AS attending_staff_name,
  -- department is captured on the encounter itself going forward; for
  -- encounters created before that column existed, fall back to the
  -- attending physician's department rather than leaving it blank.
  COALESCE(e.department, s.department, 'Unspecified') AS department,
  e.encounter_type,
  e.reason,
  e.expected_discharge_date,
  e.created_at AS admitted_at,
  r.room_id AS current_room_id,
  r.room_number AS current_room_number,
  r.room_type AS current_room_type,
  r.room_type_label AS current_room_type_label,
  d.discharged_at,
  d.discharge_notes,
  d.discharged_at IS NOT NULL AS is_discharged,
  IF(
    d.discharged_at IS NOT NULL,
    TIMESTAMP_DIFF(d.discharged_at, e.created_at, HOUR) / 24.0,
    NULL
  ) AS length_of_stay_days
FROM `hospitalanalytics-504701.raw.encounters` e
LEFT JOIN `hospitalanalytics-504701.silver.patients` p
  ON p.hospital_id = e.hospital_id AND p.patient_user_id = e.patient_user_id
LEFT JOIN `hospitalanalytics-504701.silver.staff` s
  ON s.hospital_id = e.hospital_id AND s.staff_user_id = e.attending_staff_user_id
LEFT JOIN current_room cr
  ON cr.hospital_id = e.hospital_id AND cr.encounter_id = e.encounter_id
LEFT JOIN `hospitalanalytics-504701.silver.rooms` r
  ON r.hospital_id = cr.hospital_id AND r.room_id = cr.room_id
LEFT JOIN (SELECT * FROM latest_discharge WHERE rn = 1) d
  ON d.hospital_id = e.hospital_id AND d.encounter_id = e.encounter_id;
