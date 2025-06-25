-- Create users table for authentication and role management
-- Run this script to add user authentication to the BAHI-KHATA system

CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    role ENUM('admin', 'accountant', 'viewer') NOT NULL DEFAULT 'viewer',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL,
    created_by INT,
    
    INDEX idx_username (username),
    INDEX idx_role (role),
    INDEX idx_active (is_active),
    
    FOREIGN KEY (created_by) REFERENCES users(user_id) ON DELETE SET NULL
);

-- Insert default admin user (password: admin123)
-- Note: In production, use a stronger password and hash it properly
INSERT INTO users (username, password_hash, full_name, role, is_active) 
VALUES (
    'admin', 
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewRuQNwvM5w6eKKe', -- admin123
    'System Administrator', 
    'admin', 
    TRUE
) ON DUPLICATE KEY UPDATE username = username;

-- Create audit table for user activities
CREATE TABLE IF NOT EXISTS user_audit_log (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    action VARCHAR(100) NOT NULL,
    details TEXT,
    ip_address VARCHAR(45),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_user_id (user_id),
    INDEX idx_timestamp (timestamp),
    INDEX idx_action (action),
    
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Grant appropriate permissions (adjust as needed for your MySQL setup)
-- GRANT SELECT, INSERT, UPDATE ON users TO 'your_app_user'@'localhost';
-- GRANT SELECT, INSERT ON user_audit_log TO 'your_app_user'@'localhost';
