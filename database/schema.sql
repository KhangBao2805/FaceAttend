-- FaceAttend schema (SQLite). Chạy idempotent: dùng IF NOT EXISTS.
CREATE TABLE IF NOT EXISTS users(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL, email TEXT DEFAULT '',
  password_hash TEXT NOT NULL, role TEXT NOT NULL DEFAULT 'teacher',
  full_name TEXT, linked_student_code TEXT, avatar_color TEXT DEFAULT '',
  created_at TEXT);
CREATE TABLE IF NOT EXISTS students(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  code TEXT UNIQUE NOT NULL, full_name TEXT NOT NULL,
  class_name TEXT NOT NULL, grade TEXT DEFAULT '12',
  dob TEXT DEFAULT '', gender TEXT DEFAULT '', email TEXT DEFAULT '',
  parent_phone TEXT DEFAULT '', phone TEXT DEFAULT '',
  enroll_date TEXT DEFAULT '', face_registered INTEGER DEFAULT 0,
  created_at TEXT);
CREATE TABLE IF NOT EXISTS teachers(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  code TEXT UNIQUE, full_name TEXT, subject TEXT, phone TEXT, email TEXT DEFAULT '');
CREATE TABLE IF NOT EXISTS classes(
  id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE,
  grade TEXT DEFAULT '12', homeroom TEXT DEFAULT '',
  room TEXT DEFAULT '', capacity INTEGER DEFAULT 45);
CREATE TABLE IF NOT EXISTS subjects(
  id INTEGER PRIMARY KEY AUTOINCREMENT, code TEXT UNIQUE, name TEXT, color TEXT DEFAULT '');
CREATE TABLE IF NOT EXISTS periods(
  period INTEGER PRIMARY KEY, label TEXT,
  start_time TEXT, end_time TEXT, session TEXT);
CREATE TABLE IF NOT EXISTS schedules(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  weekday INTEGER, period INTEGER, subject TEXT,
  teacher TEXT, room TEXT, class_name TEXT DEFAULT '12A1',
  start_time TEXT, end_time TEXT);
CREATE TABLE IF NOT EXISTS attendance(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  date TEXT NOT NULL, period INTEGER NOT NULL, subject TEXT DEFAULT '',
  student_code TEXT NOT NULL, class_name TEXT DEFAULT '',
  time TEXT DEFAULT '', status TEXT DEFAULT 'Có mặt', method TEXT DEFAULT 'face',
  UNIQUE(date, period, student_code));
CREATE TABLE IF NOT EXISTS face_profiles(
  student_code TEXT UNIQUE NOT NULL, embedding TEXT NOT NULL,
  consent INTEGER DEFAULT 0, created_at TEXT);
-- Bảng cũ face_data được giữ để tương thích, service đọc cả hai.
CREATE TABLE IF NOT EXISTS face_data(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  student_code TEXT UNIQUE NOT NULL, embedding TEXT NOT NULL,
  consent INTEGER DEFAULT 0, created_at TEXT);
CREATE TABLE IF NOT EXISTS notifications(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT, body TEXT DEFAULT '', type TEXT DEFAULT 'info',
  is_read INTEGER DEFAULT 0, created_at TEXT);
