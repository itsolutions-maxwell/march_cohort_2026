-- GOLD LAYER — fact_bed_occupancy
-- One row per physical room, across all hospitals. Powers: total/occupied/
-- available beds, occupancy %, occupancy by room type, occupancy by
-- department. A room is "occupied" if it's the current room (per
-- silver.encounters' already-resolved logic) of an encounter that hasn't
-- been discharged.

CREATE OR REPLACE VIEW `hospitalanalytics-504701.gold.fact_bed_occupancy` AS
SELECT
  r.hospital_id,
  r.room_id,
  r.room_number,
  r.room_type,
  r.room_type_label,
  r.floor,
  e.encounter_id IS NOT NULL AS is_occupied,
  e.encounter_id AS current_encounter_id,
  e.patient_name AS current_patient_name,
  e.department AS current_department
FROM `hospitalanalytics-504701.silver.rooms` r
LEFT JOIN `hospitalanalytics-504701.silver.encounters` e
  ON e.hospital_id = r.hospital_id
  AND e.current_room_id = r.room_id
  AND e.is_discharged = FALSE;
