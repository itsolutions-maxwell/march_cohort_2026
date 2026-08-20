-- GOLD LAYER — dim_hospital
-- Nothing to clean here beyond raw, so gold sources it directly.

CREATE OR REPLACE VIEW `hospitalanalytics-504701.gold.dim_hospital` AS
SELECT hospital_id, name, address, phone
FROM `hospitalanalytics-504701.raw.hospital_info`;
