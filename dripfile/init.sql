CREATE DATABASE IF NOT EXISTS dripfile;
USE dripfile;

DROP TABLE IF EXISTS files;

CREATE TABLE IF NOT EXISTS files (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    extension VARCHAR(10),
    size VARCHAR(50),
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabel admin untuk login
DROP TABLE IF EXISTS admins;
CREATE TABLE IF NOT EXISTS admins (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);

-- Tambah admin default (username: admin, password: admin123)
INSERT INTO admins (username, password)
VALUES ('admin', SHA2('admin123', 256));

-- Tabel log akses pengguna
DROP TABLE IF EXISTS access_logs;
CREATE TABLE IF NOT EXISTS access_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(255),
    ip VARCHAR(100),
    user_agent TEXT,
    last_access TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
