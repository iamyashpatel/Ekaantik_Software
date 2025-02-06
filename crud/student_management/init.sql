-- Step 1: Create the database if it doesn't already exist
DO
$$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_database WHERE datname = 'student_management') THEN
        CREATE DATABASE student_management;
    END IF;
END
$$;

-- Step 2: Connect to the 'student_management' database
\c student_management;

-- Step 3: Drop tables if they already exist to avoid conflicts
DROP TABLE IF EXISTS marks CASCADE;
DROP TABLE IF EXISTS subjects CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Step 4: Create the 'users' table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('Student', 'Teacher'))
);

-- Step 5: Create the 'subjects' table
CREATE TABLE subjects (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    teacher_id INTEGER REFERENCES users(id) ON DELETE SET NULL
);

-- Step 6: Create the 'marks' table
CREATE TABLE marks (
    id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    subject_id INTEGER REFERENCES subjects(id) ON DELETE CASCADE,
    marks INTEGER NOT NULL CHECK (marks >= 0 AND marks <= 100)
);

-- Step 7: Grant permissions
-- Grant all privileges on the database to the postgres user
GRANT ALL PRIVILEGES ON DATABASE student_management TO postgres;

-- Grant permissions on tables to the postgres user
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;

-- Grant permissions on sequences to the postgres user
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;

-- Grant permissions on functions to the postgres user
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO postgres;
