-- Create notifications table for transaction approval/rejection status
-- Simple table to show recent approvals/rejections on sidebar for all users

CREATE TABLE IF NOT EXISTS notifications (
    notification_id INT AUTO_INCREMENT PRIMARY KEY,
    entry_id VARCHAR(50) NOT NULL,
    status ENUM('approved', 'rejected') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_entry_id (entry_id),
    INDEX idx_created_at (created_at)
);
