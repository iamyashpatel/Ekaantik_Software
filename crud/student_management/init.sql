-- Check if the database exists before creating it
DO
$$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_database WHERE datname = 'student_management') THEN
      CREATE DATABASE student_management;
   END IF;
END
$$;

-- Connect to the 'student_management' database
\c student_management;

-- Drop tables if they already exist to avoid conflicts
DROP TABLE IF EXISTS marks;
DROP TABLE IF EXISTS subjects;
DROP TABLE IF EXISTS users;

-- Create the 'users' table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    role VARCHAR(20) CHECK (role IN ('Student', 'Teacher'))
);

-- Create the 'subjects' table
CREATE TABLE subjects (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    teacher_id INTEGER REFERENCES users(id)
);

-- Create the 'marks' table
CREATE TABLE marks (
    id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES users(id),
    subject_id INTEGER REFERENCES subjects(id),
    marks INTEGER
);
