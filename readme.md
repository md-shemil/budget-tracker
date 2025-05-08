copy and paste this in mysql community server command line

-- Create Database
CREATE DATABASE IF NOT EXISTS budget_tracker;

-- Use the database
USE budget_tracker;

-- Create users table
CREATE TABLE IF NOT EXISTS users (
id INT AUTO_INCREMENT PRIMARY KEY,
username VARCHAR(100) NOT NULL,
user_id VARCHAR(100) NOT NULL UNIQUE,
password VARCHAR(100) NOT NULL
);

-- Create transactions table
CREATE TABLE IF NOT EXISTS transactions (
id INT AUTO_INCREMENT PRIMARY KEY,
user_id VARCHAR(100) NOT NULL,
date DATE NOT NULL,
description VARCHAR(255) NOT NULL,
amount DECIMAL(10, 2) NOT NULL,
type VARCHAR(50) NOT NULL,
FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);
CREATE TABLE expenses (
id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
user_id VARCHAR(100) NOT NULL,
expense_date DATE NOT NULL,
amount DECIMAL(10,2) NOT NULL,
category VARCHAR(100) NOT NULL,
description VARCHAR(255),
INDEX (user_id)
);

CREATE TABLE income (
id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
user_id VARCHAR(100) NOT NULL,
income_date DATE NOT NULL,
amount DECIMAL(10,2) NOT NULL,
source VARCHAR(255) NOT NULL,
INDEX (user_id)
);

CREATE TABLE loans (
id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
user_id VARCHAR(100),
lender_name VARCHAR(100),
amount DECIMAL(10,2),
remaining_amount DECIMAL(10,2),
interest_rate DECIMAL(5,2),
due_date DATE,
description TEXT,
INDEX (user_id)
);

CREATE TABLE notifications (
id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
user_id INT NOT NULL,
message TEXT NOT NULL,
timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
