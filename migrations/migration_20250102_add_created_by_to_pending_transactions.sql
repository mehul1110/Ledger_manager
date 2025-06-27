-- Add created_by column to pending_transactions table to track which user created each transaction
-- This is needed for the notification system to know which accountant to notify

ALTER TABLE pending_transactions 
ADD COLUMN created_by INT NULL,
ADD INDEX idx_created_by (created_by),
ADD FOREIGN KEY (created_by) REFERENCES users(user_id) ON DELETE SET NULL;

-- Update existing records to set created_by based on current session if possible
-- For now, existing records will have NULL created_by
-- Future entries will have this field populated when they are created
