-- RAW LAYER — room_assignments

CREATE OR REPLACE VIEW `hospitalanalytics-504701.raw.room_assignments` AS
SELECT 'hospital_a' AS hospital_id, assignment_id, encounter_id, room_id, staff_user_id, assigned_at
FROM `hospitalanalytics-504701.hospital_a.room_assignments`

UNION ALL

SELECT 'hospital_b' AS hospital_id, assignment_id, encounter_id, room_id, staff_user_id, assigned_at
FROM `hospitalanalytics-504701.hospital_b.room_assignments`

UNION ALL

SELECT 'hospital_c' AS hospital_id, assignment_id, encounter_id, room_id, staff_user_id, assigned_at
FROM `hospitalanalytics-504701.hospital_c.room_assignments`;
