-- SILVER LAYER — staff
-- LEFT JOIN (not JOIN) on staff_profiles: the app always writes one at
-- signup, but silver shouldn't assume that holds for every row forever.
-- A staff user with no profile row still shows up here, just "Unspecified."

CREATE OR REPLACE VIEW `hospitalanalytics-504701.silver.staff` AS
SELECT
  u.hospital_id,
  u.user_id AS staff_user_id,
  u.first_name,
  u.last_name,
  u.full_name,
  u.email,
  COALESCE(sp.department, 'Unspecified') AS department,
  COALESCE(sp.title, 'Unspecified') AS title,
  u.created_at
FROM `hospitalanalytics-504701.silver.users` u
LEFT JOIN `hospitalanalytics-504701.raw.staff_profiles` sp
  ON sp.hospital_id = u.hospital_id AND sp.staff_user_id = u.user_id
WHERE u.role = 'staff';
