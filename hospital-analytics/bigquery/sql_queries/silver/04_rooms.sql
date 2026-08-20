-- SILVER LAYER — rooms
-- Adds a display-friendly room_type_label. room_type itself stays as the
-- raw slug (icu, er, operating_room, ...) since gold/dashboard grouping
-- should key off a stable value, not a string meant for humans.

CREATE OR REPLACE VIEW `hospitalanalytics-504701.silver.rooms` AS
SELECT
  hospital_id,
  room_id,
  room_number,
  room_type,
  CASE room_type
    WHEN 'general' THEN 'General'
    WHEN 'private' THEN 'Private'
    WHEN 'semi_private' THEN 'Semi-Private'
    WHEN 'icu' THEN 'ICU'
    WHEN 'er' THEN 'Emergency'
    WHEN 'operating_room' THEN 'Operating Room'
    ELSE INITCAP(REPLACE(room_type, '_', ' '))
  END AS room_type_label,
  floor,
  created_at
FROM `hospitalanalytics-504701.raw.rooms`
WHERE room_type IS NOT NULL;
