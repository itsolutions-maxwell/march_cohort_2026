-- RAW LAYER — users
-- Just combines the three hospitals into one place and tags each row with
-- which hospital it came from. No cleaning, no dedup, no null handling —
-- that's the whole point of "raw": it's exactly what's in the source
-- tables, warts and all. Cleaning happens in silver/01_users.sql.

CREATE OR REPLACE VIEW `hospitalanalytics-504701.raw.users` AS
SELECT 'hospital_a' AS hospital_id, user_id, email, password_hash, role, full_name, created_at
FROM `hospitalanalytics-504701.hospital_a.users`

UNION ALL

SELECT 'hospital_b' AS hospital_id, user_id, email, password_hash, role, full_name, created_at
FROM `hospitalanalytics-504701.hospital_b.users`

UNION ALL

SELECT 'hospital_c' AS hospital_id, user_id, email, password_hash, role, full_name, created_at
FROM `hospitalanalytics-504701.hospital_c.users`;
