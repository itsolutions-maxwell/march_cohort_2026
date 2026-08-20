-- Run this once before anything else in raw/, silver/, or gold/.
-- Creates the three medallion datasets alongside the existing per-hospital
-- ones (hospital_a, hospital_b, hospital_c — those stay exactly as they
-- are; the app writes to them directly and nothing here touches them).

CREATE SCHEMA IF NOT EXISTS `hospitalanalytics-504701.raw`
OPTIONS (location = 'US');

CREATE SCHEMA IF NOT EXISTS `hospitalanalytics-504701.silver`
OPTIONS (location = 'US');

CREATE SCHEMA IF NOT EXISTS `hospitalanalytics-504701.gold`
OPTIONS (location = 'US');
