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



-- Table for Water Levels --> created based on the possible attributes that can be found in the second link
DROP TABLE IF EXISTS Water_Levels;

-- Create a simple Water_Levels table for testing
CREATE TABLE Water_Levels (
    id SERIAL PRIMARY KEY,  -- Primary key expected by Django
    location_id INTEGER,
    value_at_time NUMERIC(10, 2),
    unit VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

DROP TABLE IF EXISTS Accounts;

-- Create the Accounts table
CREATE TABLE Accounts (
    id SERIAL PRIMARY KEY,       -- Primary key
    username VARCHAR(50) UNIQUE NOT NULL, -- Unique username
    email VARCHAR(255) UNIQUE NOT NULL,   -- Unique email
    password VARCHAR(255) NOT NULL,       -- Password (hashed for security)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Timestamp of account creation
);


-- Table for Locations
-- CREATE TABLE IF NOT EXISTS Locations (
--     location_id SERIAL PRIMARY KEY,
--     dbmsnr INTEGER UNIQUE, -- Internal database number
--     hzbnr INTEGER UNIQUE, -- Measuring point number of the hydrographic service
--     water_body_name VARCHAR(255), -- water body name
--     mp_operator VARCHAR(255), -- Operator of the measuring point
--     lat NUMERIC(2, 6), -- up to 9 digits and up to 6 decimal places --> Y coordinates
--     lon NUMERIC(3, 6), -- X coordinates
--     internet TEXT, -- Direct link to the measuring point on the operator's website
--     country TEXT DEFAULT "Austria", -- Country information for measuring points outside Austria
--     -- Do we even need the "country" attribute??
--     mp_geometry GEOMETRY(Polygon, 4326), -- mp stands for measuring point (MAYBE NEED TO USE: mp_geometry POLYGON)
--     -- Geometry as Polygon, using SRID 4326 for WGS84
--     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
-- );



-- CREATE TABLE IF NOT EXISTS Water_Level_History (
--     entry_id SERIAL PRIMARY KEY,
--     location_id INTEGER REFERENCES Locations(location_id) ON DELETE CASCADE,  -- Links to location if applicable
--     category_label VARCHAR(255),           -- Category label (e.g., CRS or projection system)
--     category_term TEXT,                    -- Category term (e.g., EPSG code)
--     title TEXT,                            -- Title of the dataset
--     summary TEXT,                          -- Summary of dataset description (german...)
--     last_updated TIMESTAMP,                -- Timestamp of last dataset update
--     geom GEOMETRY(POLYGON, 4326),          -- Polygon coordinates (stored as GEOMETRY type for spatial use)
--     hq30 GEOMETRY(POLYGON, 4326),          -- HQ30 (30-year flood value), as an example value
--     all_time_high NUMERIC(10, 2),          -- All-time high water level
--     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
-- );


-- Table for Water Levels
CREATE TABLE IF NOT EXISTS Users (
    user_id SERIAL PRIMARY KEY,                     -- Unique identifier for each user
    email VARCHAR(255) UNIQUE NOT NULL,             -- Email address, unique and required
    hashed_passw VARCHAR(255) NOT NULL,             -- Hashed password (255 to accommodate long hashes)
    phone_num VARCHAR(15),                          -- Phone number (optional, allows for country codes)
    user_address TEXT,                              -- User's address (text for flexibility in length, can use VARCHAR(255) if needed)
    perm_level VARCHAR(15) DEFAULT 'user' CHECK (perm_level IN ('user', 'admin')),        -- Permission level (right now it can be user or admin)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- Timestamp of user creation --> may be used for statistics (if not, it can be easily deleted)
)
