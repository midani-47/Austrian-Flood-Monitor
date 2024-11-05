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
    gewaesser VARCHAR(255),                      
    hydrodienst VARCHAR(255),                    
    lat NUMERIC(9, 6),                           
    lon NUMERIC(9, 6),                           
    geometry GEOMETRY,                           
    country VARCHAR(50),                         
    internet TEXT,                               
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table for Water Levels --> created based on the possible attributes that can be found in the second link
CREATE TABLE IF NOT EXISTS Water_Levels (
    water_level_id SERIAL PRIMARY KEY,
    location_id INTEGER NOT NULL REFERENCES Locations(location_id) ON DELETE CASCADE,
    measurement_time TIMESTAMP NOT NULL,
    value NUMERIC(10, 2) NOT NULL,               
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

-- Table for Users
CREATE TABLE IF NOT EXISTS Users (
    user_id SERIAL PRIMARY KEY,               -- Unique user ID, auto-incremented
    email VARCHAR(255) UNIQUE NOT NULL,       -- Email address, must be unique
    username VARCHAR(100) UNIQUE NOT NULL,    -- Username, must be unique
    password_hash TEXT NOT NULL,              -- Hashed password
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- I am not sure if this is needed
);

-- Table for Emergency Reports



-- Table for emergency response planning
