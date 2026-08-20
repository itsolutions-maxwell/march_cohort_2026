-- SILVER LAYER — users
-- This is where real cleaning happens:
--   1. Drop junk rows (missing email/name — shouldn't exist given the app's
--      NOT NULL columns, but silver shouldn't assume raw is trustworthy).
--   2. Normalize email (trim + lowercase) so joins/dedup are reliable.
--   3. Dedupe on (hospital, email) — the app's signup check already
--      prevents this, but a silver layer defends against bad data from
--      *any* source, not just this one app.
--   4. Split full_name into first_name/last_name. The app only ever
--      collects one "full name" field at signup, so this is a derived
--      split, not a real source column — good talking point for students
--      on why silver often *adds* structure raw never had.
-- password_hash is intentionally dropped here — nothing past bronze needs
-- it, and analytics layers shouldn't carry auth secrets forward.

CREATE OR REPLACE VIEW `hospitalanalytics-504701.silver.users` AS
WITH cleaned AS (
  SELECT
    hospital_id,
    user_id,
    LOWER(TRIM(email)) AS email,
    role,
    TRIM(full_name) AS full_name,
    created_at,
    ROW_NUMBER() OVER (
      PARTITION BY hospital_id, LOWER(TRIM(email))
      ORDER BY created_at
    ) AS row_num
  FROM `hospitalanalytics-504701.raw.users`
  WHERE email IS NOT NULL
    AND TRIM(email) != ''
    AND full_name IS NOT NULL
    AND TRIM(full_name) != ''
)
SELECT
  hospital_id,
  user_id,
  email,
  role,
  full_name,
  SPLIT(full_name, ' ')[SAFE_OFFSET(0)] AS first_name,
  CASE
    WHEN ARRAY_LENGTH(SPLIT(full_name, ' ')) > 1
      THEN SPLIT(full_name, ' ')[SAFE_OFFSET(ARRAY_LENGTH(SPLIT(full_name, ' ')) - 1)]
    ELSE NULL
  END AS last_name,
  created_at
FROM cleaned
WHERE row_num = 1;
