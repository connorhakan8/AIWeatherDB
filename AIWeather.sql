-- ====================================================================
-- WeatherData import script
-- ====================================================================

-- Optional: keep strict mode (recommended) so bad data doesn't slip in.
-- SHOW VARIABLES LIKE 'sql_mode';

-- --------------------------------------------------------------------
-- 1) Recreate tables
-- --------------------------------------------------------------------
DROP DATABASE weatherDB;
CREATE DATABASE weatherDB;
USE weatherDB;
DROP TABLE IF EXISTS Readings;
DROP TABLE IF EXISTS Station;

CREATE TABLE Station(
  stationID   VARCHAR(11) PRIMARY KEY,
  stationName VARCHAR(45) NOT NULL,
  location    POINT NOT NULL SRID 4326,
  elevation   DECIMAL(7,2)
);

-- Use a composite primary key: one row per (station, date)
CREATE TABLE Readings(
  stationID   VARCHAR(11) NOT NULL,
  readingDate DATE NOT NULL,
  dailyHigh   SMALLINT,  -- TMAX
  dailyLow    SMALLINT,  -- TMIN
  CONSTRAINT PK_READINGS PRIMARY KEY (stationID, readingDate),
  CONSTRAINT FK_READING_STATION
    FOREIGN KEY (stationID) REFERENCES Station(stationID)
    ON DELETE CASCADE
);

-- --------------------------------------------------------------------
-- 2) Staging table for raw CSV fields (all text; we clean on load)
-- --------------------------------------------------------------------
DROP TEMPORARY TABLE IF EXISTS tmp_weather;
CREATE TEMPORARY TABLE tmp_weather (
  stationID      VARCHAR(64),
  stationName    VARCHAR(255),
  latitude_txt   VARCHAR(64),
  longitude_txt  VARCHAR(64),
  elevation_txt  VARCHAR(64),
  date_txt       VARCHAR(64),
  tmax_txt       VARCHAR(64),
  tmin_txt       VARCHAR(64)
);

-- --------------------------------------------------------------------
-- 3) Load the CSV
--    - Handles quoted station names (e.g., "REDWOOD CITY, CA US")
--    - Strips carriage returns and non-breaking spaces from TMAX/TMIN
--    - Turns true blanks into NULL to avoid 1292 when casting
-- --------------------------------------------------------------------

# PUT YOUR OWN FILE PATH HERE (I kept getting file not found if I put it in a local directory and idk why)
LOAD DATA LOCAL INFILE 'WeatherData.csv'
INTO TABLE tmp_weather
FIELDS TERMINATED BY ',' ENCLOSED BY '"' ESCAPED BY '\\'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(@stationID, @stationName, @lat, @lon, @elev, @date, @tmax, @tmin)
SET
  stationID      = TRIM(@stationID),
  stationName    = TRIM(@stationName),
  latitude_txt   = TRIM(@lat),
  longitude_txt  = TRIM(@lon),
  elevation_txt  = NULLIF(TRIM(@elev), ''),
  date_txt       = NULLIF(TRIM(@date), ''),
  -- strip CR (\r) and non-breaking space (0xC2A0), then NULL out empties
  tmax_txt       = NULLIF(TRIM(REPLACE(REPLACE(@tmax, '\r',''), UNHEX('C2A0'), '')), ''),
  tmin_txt       = NULLIF(TRIM(REPLACE(REPLACE(@tmin, '\r',''), UNHEX('C2A0'), '')), '');

-- If your file truly uses Windows line endings, you may alternatively use:
-- LINES TERMINATED BY '\r\n'
-- (The REPLACE above already makes the loader robust either way.)

-- --------------------------------------------------------------------
-- 4) Insert unique stations
--    - POINT(longitude, latitude) with SRID 4326
--    - Elevation cast to DECIMAL(7,2)
-- --------------------------------------------------------------------
INSERT INTO Station (stationID, stationName, location, elevation)
SELECT
  tw.stationID,
  tw.stationName,
  ST_SRID(POINT(
    CAST(NULLIF(tw.longitude_txt, '') AS DECIMAL(10,6)),
    CAST(NULLIF(tw.latitude_txt,  '') AS DECIMAL(10,6))
  ), 4326) AS location,
  CAST(NULLIF(tw.elevation_txt, '') AS DECIMAL(7,2)) AS elevation
FROM tmp_weather tw
GROUP BY tw.stationID, tw.stationName, tw.longitude_txt, tw.latitude_txt, tw.elevation_txt;

-- --------------------------------------------------------------------
-- 5) Insert readings
--    - Safely handle missing or non-numeric TMAX/TMIN (→ NULL)
--    - Cast to integers; if decimals sneak in, ROUND before CAST
-- --------------------------------------------------------------------
INSERT INTO Readings (stationID, readingDate, dailyHigh, dailyLow)
SELECT
  tw.stationID,
  STR_TO_DATE(tw.date_txt, '%Y-%m-%d') AS readingDate,

  CASE
    WHEN tw.tmax_txt REGEXP '^-?[0-9]+(\\.[0-9]+)?$'
      THEN CAST(ROUND(CAST(tw.tmax_txt AS DECIMAL(10,2))) AS SIGNED)
    ELSE NULL
  END AS dailyHigh,

  CASE
    WHEN tw.tmin_txt REGEXP '^-?[0-9]+(\\.[0-9]+)?$'
      THEN CAST(ROUND(CAST(tw.tmin_txt AS DECIMAL(10,2))) AS SIGNED)
    ELSE NULL
  END AS dailyLow

FROM tmp_weather tw
WHERE tw.date_txt IS NOT NULL;