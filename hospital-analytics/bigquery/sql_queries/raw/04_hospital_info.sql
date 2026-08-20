-- RAW LAYER — hospital_info
-- This table already has its own hospital_id column (set to the dataset
-- name when it was seeded), so unlike the other raw views we don't need to
-- tag rows with a literal — we just combine.

CREATE OR REPLACE VIEW `hospitalanalytics-504701.raw.hospital_info` AS
SELECT hospital_id, name, address, phone, created_at
FROM `hospitalanalytics-504701.hospital_a.hospital_info`

UNION ALL

SELECT hospital_id, name, address, phone, created_at
FROM `hospitalanalytics-504701.hospital_b.hospital_info`

UNION ALL

SELECT hospital_id, name, address, phone, created_at
FROM `hospitalanalytics-504701.hospital_c.hospital_info`;
