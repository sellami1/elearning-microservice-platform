-- PostgreSQL database initialization script for course-service
-- Creates tables, indices and constraints matching the Alembic initial migration

-- Drop existing objects (safe to re-run)
DROP INDEX IF EXISTS ix_enrollments_id;
DROP INDEX IF EXISTS ix_feedbacks_id;
DROP INDEX IF EXISTS ix_lessons_id;
DROP INDEX IF EXISTS ix_courses_id;

DROP TABLE IF EXISTS enrollments CASCADE;
DROP TABLE IF EXISTS feedbacks CASCADE;
DROP TABLE IF EXISTS lessons CASCADE;
DROP TABLE IF EXISTS courses CASCADE;

-- Create courses table
CREATE TABLE courses (
  id SERIAL PRIMARY KEY,
  title VARCHAR(255) NOT NULL,
  description TEXT,
  price DOUBLE PRECISION NOT NULL DEFAULT 0.0,
  instructor_id INTEGER NOT NULL,
  created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT now(),
  updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT now()
);
CREATE INDEX ix_courses_id ON courses (id);

-- Create lessons table
CREATE TABLE lessons (
  id SERIAL PRIMARY KEY,
  course_id INTEGER NOT NULL REFERENCES courses(id),
  title VARCHAR(255) NOT NULL,
  content TEXT,
  video_url VARCHAR(255),
  position INTEGER NOT NULL DEFAULT 0,
  created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT now(),
  updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT now()
);
CREATE INDEX ix_lessons_id ON lessons (id);

-- Create feedbacks table
CREATE TABLE feedbacks (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL,
  course_id INTEGER NOT NULL REFERENCES courses(id),
  rating INTEGER NOT NULL,
  comment TEXT,
  created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT now(),
  updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT now()
);
CREATE INDEX ix_feedbacks_id ON feedbacks (id);

-- Create enrollments table
CREATE TABLE enrollments (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL,
  course_id INTEGER NOT NULL REFERENCES courses(id),
  completion_percentage DOUBLE PRECISION NOT NULL DEFAULT 0.0,
  enrolled_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT now(),
  updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT now()
);
CREATE INDEX ix_enrollments_id ON enrollments (id);
