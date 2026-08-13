WITH patients AS (
  SELECT
    'Hospital A' AS Hospital_Name,
    full_name,
    role,
    email,
    ROW_NUMBER() OVER (
      PARTITION BY LOWER(TRIM(full_name))
      ORDER BY email
    ) AS rn
  FROM `hospitalanalytics-504701.hospital_a.users`

  UNION ALL

  SELECT
    'Hospital B' AS Hospital_Name,
    full_name,
    role,
    email,
    ROW_NUMBER() OVER (
      PARTITION BY LOWER(TRIM(full_name))
      ORDER BY email
    ) AS rn
  FROM `hospitalanalytics-504701.hospital_b.users`
),

-- Keep only unique patients within each hospital
deduped_patients AS (
  SELECT
    Hospital_Name,
    full_name,
    role,
    email
  FROM patients
  WHERE role = 'patient'
    AND rn = 1
),

-- Find patients appearing in more than one hospital
duplicate_patients AS (
  SELECT
    LOWER(TRIM(full_name)) AS normalized_name,
    COUNT(DISTINCT Hospital_Name) AS hospital_count
  FROM deduped_patients
  GROUP BY LOWER(TRIM(full_name))
  HAVING COUNT(DISTINCT Hospital_Name) > 1
)

SELECT
  p.Hospital_Name,
  p.full_name,
  p.role,
  p.email
FROM deduped_patients p
JOIN duplicate_patients d
  ON LOWER(TRIM(p.full_name)) = d.normalized_name
ORDER BY
  d.normalized_name,
  p.Hospital_Name;