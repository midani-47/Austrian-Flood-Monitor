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
    dbmsnr INTEGER UNIQUE, -- Internal database number
    hzbnr INTEGER UNIQUE, -- Measuring point number of the hydrographic service
    water_body_name VARCHAR(255), -- water body name
    mp_operator VARCHAR(255), -- Operator of the measuring point
    lat NUMERIC(2, 6), -- up to 9 digits and up to 6 decimal places --> Y coordinates
    lon NUMERIC(3, 6), -- X coordinates
    internet TEXT, -- Direct link to the measuring point on the operator's website
    country TEXT DEFAULT "Austria", -- Country information for measuring points outside Austria
    -- Do we even need the "country" attribute??
    mp_geometry GEOMETRY(Polygon, 4326), -- mp stands for measuring point (MAYBE NEED TO USE: mp_geometry POLYGON)
    -- Geometry as Polygon, using SRID 4326 for WGS84
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table for Water Levels --> created based on the possible attributes that can be found in the second link
CREATE TABLE IF NOT EXISTS Water_Levels (
    water_level_id SERIAL PRIMARY KEY,
    location_id INTEGER NOT NULL REFERENCES Locations(location_id) ON DELETE CASCADE, -- foreign key, references the ID of the location (from the locations table)
    -- measurement_time TIMESTAMP NOT NULL, -- Depends on wertw_cm
    value_at_time NUMERIC(10, 2) NOT NULL, -- refers to wertw_cm 
    unit VARCHAR(50) NOT NULL, -- either cm, m, m^3/s
    parameter VARCHAR(100), -- measured value
    forecast BOOLEAN DEFAULT FALSE, -- (prognose) Indication of whether forecast data is available for the measuring point
    total_code INTEGER, -- Indicates the code for the correct categorization
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS Water_Level_History (
    entry_id SERIAL PRIMARY KEY,
    location_id INTEGER REFERENCES Locations(location_id) ON DELETE CASCADE,  -- Links to location if applicable
    category_label VARCHAR(255),           -- Category label (e.g., CRS or projection system)
    category_term TEXT,                    -- Category term (e.g., EPSG code)
    title TEXT,                            -- Title of the dataset
    summary TEXT,                          -- Summary of dataset description (german...)
    last_updated TIMESTAMP,                -- Timestamp of last dataset update
    geom GEOMETRY(POLYGON, 4326),          -- Polygon coordinates (stored as GEOMETRY type for spatial use)
    hq30 GEOMETRY(POLYGON, 4326),          -- HQ30 (30-year flood value), as an example value
    all_time_high NUMERIC(10, 2),          -- All-time high water level
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- Table for Water Levels
CREATE TABLE IF NOT EXISTS User (
    user_id SERIAL PRIMARY KEY,                     -- Unique identifier for each user
    email VARCHAR(255) UNIQUE NOT NULL,             -- Email address, unique and required
    hashed_passw VARCHAR(255) NOT NULL,             -- Hashed password (255 to accommodate long hashes)
    phone_num VARCHAR(15),                          -- Phone number (optional, allows for country codes)
    user_address TEXT,                              -- User's address (text for flexibility in length, can use VARCHAR(255) if needed)
    perm_level SMALLINT DEFAULT 1,                  -- Permission level (default 1, can adjust as needed) --> 1:"user", 2:"admin"
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- Timestamp of user creation --> may be used for statistics (if not, it can be easily deleted)
)
