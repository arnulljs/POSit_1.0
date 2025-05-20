USE sql12780094;

-- Modify users table
ALTER TABLE users 
    MODIFY created_at DATETIME NULL,
    MODIFY updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP;

-- Modify tickets table
ALTER TABLE tickets 
    MODIFY created_at DATETIME NULL,
    MODIFY updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP;

-- Modify transactions table
ALTER TABLE transactions 
    MODIFY created_at DATETIME NULL;

-- Modify transaction_items table
ALTER TABLE transaction_items 
    MODIFY created_at DATETIME NULL; 