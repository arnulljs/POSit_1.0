-- Create the database if it doesn't exist
CREATE DATABASE IF NOT EXISTS posit_db;
USE posit_db;

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('admin', 'user') NOT NULL DEFAULT 'user',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Create tickets table
CREATE TABLE IF NOT EXISTS tickets (
    ticket_id VARCHAR(20) PRIMARY KEY,
    event VARCHAR(100) NOT NULL,
    tier VARCHAR(50) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    availability INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Create transactions table
CREATE TABLE IF NOT EXISTS transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    transaction_id VARCHAR(50) UNIQUE NOT NULL,
    user_id INT,
    total_amount DECIMAL(10, 2) NOT NULL,
    tax_amount DECIMAL(10, 2) NOT NULL,
    discount_amount DECIMAL(10, 2) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Create transaction_items table
CREATE TABLE IF NOT EXISTS transaction_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    transaction_id INT NOT NULL,
    ticket_id VARCHAR(20) NOT NULL,
    quantity INT NOT NULL,
    price_at_sale DECIMAL(10, 2) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (transaction_id) REFERENCES transactions(id),
    FOREIGN KEY (ticket_id) REFERENCES tickets(ticket_id)
);

-- Insert default admin user if not exists
INSERT IGNORE INTO users (username, password, role)
VALUES ('admin', 'admin123', 'admin');

-- Insert sample ticket data
INSERT IGNORE INTO tickets (ticket_id, event, tier, price, availability) VALUES
('EVT-001', 'Coldplay', 'Standard Seating', 2500.00, 120),
('EVT-002', 'Coldplay', 'Silver Seating', 4000.00, 80),
('EVT-003', 'Coldplay', 'Gold Seating', 7000.00, 30),
('EVT-004', 'Rex Orange County', 'Standard Seating', 1800.00, 100),
('EVT-005', 'Rex Orange County', 'Silver Seating', 3200.00, 60),
('EVT-006', 'Rex Orange County', 'Gold Seating', 6000.00, 20),
('EVT-007', 'Apo Hiking Society', 'Standard Seating', 1500.00, 150),
('EVT-008', 'Apo Hiking Society', 'Silver Seating', 2500.00, 90),
('EVT-009', 'Apo Hiking Society', 'Gold Seating', 4000.00, 25),
('EVT-010', 'Queen', 'Standard Seating', 3000.00, 110),
('EVT-011', 'Queen', 'Silver Seating', 5000.00, 70),
('EVT-012', 'Queen', 'Gold Seating', 9000.00, 15); 