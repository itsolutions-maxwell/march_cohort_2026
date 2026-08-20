-- RAW LAYER — rooms

CREATE OR REPLACE VIEW `hospitalanalytics-504701.raw.rooms` AS
SELECT 'hospital_a' AS hospital_id, room_id, room_number, room_type, floor, created_at
FROM `hospitalanalytics-504701.hospital_a.rooms`

UNION ALL

SELECT 'hospital_b' AS hospital_id, room_id, room_number, room_type, floor, created_at
FROM `hospitalanalytics-504701.hospital_b.rooms`

UNION ALL

SELECT 'hospital_c' AS hospital_id, room_id, room_number, room_type, floor, created_at
FROM `hospitalanalytics-504701.hospital_c.rooms`;
