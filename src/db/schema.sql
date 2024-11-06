-- Create the AFM database if it doesn't already exist
DO
$do$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_database WHERE datname = 'AFM') THEN
      PERFORM dblink_exec('dbname=postgres', 'CREATE DATABASE AFM');
   END IF;
END
$do$;

-- Switch to the AFM database
\c AFM;

-- Table for Locations
CREATE TABLE IF NOT EXISTS Locations (
    location_id SERIAL PRIMARY KEY,
    dbmsnr INTEGER UNIQUE,                       
    hzbnr INTEGER UNIQUE,                        
    name VARCHAR(255) NOT NULL,                  
    water_body_name VARCHAR(255),                      
    mp_operator VARCHAR(255), -- mp stands for measuring point
    lat NUMERIC(9, 6), -- up to 9 digits and up to 6 decimal places
    lon NUMERIC(9, 6),
    internet TEXT,
    country TEXT,
    mp_geometry GEOMETRY, -- mp stands for measuring point
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table for Water Levels --> created based on the possible attributes that can be found in the second link
CREATE TABLE IF NOT EXISTS Water_Levels (
    water_level_id SERIAL PRIMARY KEY,
    location_id INTEGER NOT NULL REFERENCES Locations(location_id) ON DELETE CASCADE,
    measurement_time TIMESTAMP NOT NULL,
    value_at_time NUMERIC(10, 2) NOT NULL,
    unit VARCHAR(50) NOT NULL,
    parameter VARCHAR(100),
    forecast BOOLEAN DEFAULT FALSE,
    total_code INTEGER,
    alert_level VARCHAR(20),
    hq30 BOOLEAN DEFAULT FALSE,
    hq100 BOOLEAN DEFAULT FALSE,
    all_time_high BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- I am not sure if this is needed
);

