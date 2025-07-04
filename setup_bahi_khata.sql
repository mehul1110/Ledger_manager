-- BAHI-KHATA Database Setup Script
-- This script creates all tables, foreign keys, triggers, and pre-fills essential data.

-- 1. Table: account_types
CREATE TABLE IF NOT EXISTS account_types (
  account_type VARCHAR(50) NOT NULL,
  PRIMARY KEY (account_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO account_types (account_type) VALUES
  ('Bank'), ('Cash'), ('custom'), ('Main Fund'), ('payee'), ('payer'), ('Printer'), ('Salary'), ('Unit')
ON DUPLICATE KEY UPDATE account_type=account_type;

-- 2. Table: accounts
CREATE TABLE IF NOT EXISTS accounts (
  account_name VARCHAR(100) NOT NULL,
  account_type VARCHAR(50) DEFAULT NULL,
  PRIMARY KEY (account_name),
  KEY account_type (account_type),
  CONSTRAINT accounts_ibfk_1 FOREIGN KEY (account_type) REFERENCES account_types (account_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO accounts (account_name, account_type) VALUES
  ('PNB', 'Bank'),
  ('Cash', 'Cash'),
  ('Property', 'custom'),
  ('main fund', 'Main Fund'),
  ('AAA', 'Salary')
ON DUPLICATE KEY UPDATE account_name=account_name;

-- 3. Table: fd_details
CREATE TABLE IF NOT EXISTS fd_details (
  fd_id INT NOT NULL AUTO_INCREMENT,
  payment_id VARCHAR(20) DEFAULT NULL,
  bank_account VARCHAR(100) DEFAULT NULL,
  amount DECIMAL(15,2) NOT NULL,
  duration VARCHAR(50) NOT NULL,
  interest_rate VARCHAR(20) NOT NULL,
  narration TEXT,
  fd_date DATE NOT NULL,
  maturity_date DATE DEFAULT NULL,
  status VARCHAR(20) DEFAULT 'Active',
  maturity_amount DECIMAL(15,2) DEFAULT NULL,
  PRIMARY KEY (fd_id),
  KEY payment_id (payment_id),
  KEY bank_account (bank_account),
  CONSTRAINT fd_details_ibfk_1 FOREIGN KEY (payment_id) REFERENCES payments (payment_id),
  CONSTRAINT fd_details_ibfk_2 FOREIGN KEY (bank_account) REFERENCES accounts (account_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 4. Table: journal_entries
CREATE TABLE IF NOT EXISTS journal_entries (
  id INT NOT NULL AUTO_INCREMENT,
  entry_id VARCHAR(20) NOT NULL,
  account_name VARCHAR(100) DEFAULT NULL,
  entry_type ENUM('Bank','Fund') NOT NULL,
  amount DECIMAL(10,2) DEFAULT NULL,
  narration TEXT,
  mop VARCHAR(50) DEFAULT NULL,
  entry_date DATE NOT NULL,
  fd DECIMAL(15,2) DEFAULT NULL,
  sundry DECIMAL(15,2) DEFAULT NULL,
  property DECIMAL(15,2) DEFAULT NULL,
  fund DECIMAL(15,2) DEFAULT NULL,
  PRIMARY KEY (entry_id),
  UNIQUE KEY id (id),
  KEY journal_entries_ibfk_1 (account_name),
  CONSTRAINT journal_entries_ibfk_1 FOREIGN KEY (account_name) REFERENCES accounts (account_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 5. Table: monthly_main_fund_balance
CREATE TABLE IF NOT EXISTS monthly_main_fund_balance (
  month VARCHAR(7) NOT NULL,
  opening DECIMAL(12,2) DEFAULT NULL,
  closing DECIMAL(12,2) DEFAULT NULL,
  PRIMARY KEY (month)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 6. Table: monthly_sundry_outstanding
CREATE TABLE IF NOT EXISTS monthly_sundry_outstanding (
  month VARCHAR(6) NOT NULL,
  brought_forward INT DEFAULT NULL,
  current_outstanding INT DEFAULT NULL,
  PRIMARY KEY (month)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 7. Table: notifications
CREATE TABLE IF NOT EXISTS notifications (
  notification_id INT NOT NULL AUTO_INCREMENT,
  entry_id VARCHAR(50) NOT NULL,
  status ENUM('approved','rejected') NOT NULL,
  created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (notification_id),
  KEY idx_entry_id (entry_id),
  KEY idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 8. Table: payments
CREATE TABLE IF NOT EXISTS payments (
  id INT NOT NULL AUTO_INCREMENT,
  payment_id VARCHAR(20) NOT NULL,
  account_name VARCHAR(100) NOT NULL,
  amount DECIMAL(10,2) NOT NULL,
  mop VARCHAR(50) NOT NULL,
  narration VARCHAR(255) NOT NULL,
  date DATE NOT NULL,
  remarks VARCHAR(255) DEFAULT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY payment_id (payment_id),
  KEY account_name_idx (account_name),
  CONSTRAINT payments_ibfk_1 FOREIGN KEY (account_name) REFERENCES accounts (account_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 9. Table: pending_transactions
CREATE TABLE IF NOT EXISTS pending_transactions (
  id INT NOT NULL AUTO_INCREMENT,
  transaction_type ENUM('payment','receipt') NOT NULL,
  account_name VARCHAR(100) NOT NULL,
  amount DECIMAL(10,2) NOT NULL,
  mop VARCHAR(50) NOT NULL,
  narration VARCHAR(255) NOT NULL,
  transaction_date DATE NOT NULL,
  remarks VARCHAR(255) DEFAULT NULL,
  author VARCHAR(100) DEFAULT NULL,
  item_name VARCHAR(100) DEFAULT NULL,
  description VARCHAR(100) DEFAULT NULL,
  property_type VARCHAR(50) DEFAULT NULL,
  fd_duration VARCHAR(50) DEFAULT NULL,
  fd_interest VARCHAR(20) DEFAULT NULL,
  created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 10. Table: property_details
CREATE TABLE IF NOT EXISTS property_details (
  id INT NOT NULL AUTO_INCREMENT,
  payment_id VARCHAR(20) DEFAULT NULL,
  item_name VARCHAR(100) NOT NULL,
  description VARCHAR(20) DEFAULT NULL,
  type VARCHAR(50) DEFAULT NULL,
  purchase_date DATE NOT NULL,
  value DECIMAL(10, 2) NOT NULL,
  depreciation_rate DECIMAL(5, 2) DEFAULT 0.00,
  new_rate DECIMAL(10, 2) DEFAULT 0.00, -- Shows the depreciated value
  PRIMARY KEY (id),
  CONSTRAINT property_details_ibfk_1 FOREIGN KEY (payment_id) REFERENCES payments (payment_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 11. Table: receipts
CREATE TABLE IF NOT EXISTS receipts (
  id INT NOT NULL AUTO_INCREMENT,
  receipt_id VARCHAR(20) NOT NULL,
  account_name VARCHAR(100) NOT NULL,
  amount DECIMAL(10,2) NOT NULL,
  mop VARCHAR(50) NOT NULL,
  narration VARCHAR(255) NOT NULL,
  date DATE NOT NULL,
  remarks VARCHAR(255) DEFAULT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY receipt_id (receipt_id),
  KEY account_name_idx (account_name),
  CONSTRAINT receipts_ibfk_1 FOREIGN KEY (account_name) REFERENCES accounts (account_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 12. Table: sundry_credits
CREATE TABLE IF NOT EXISTS sundry_credits (
  entry_id INT NOT NULL AUTO_INCREMENT,
  account_name VARCHAR(255) DEFAULT NULL,
  amount DECIMAL(12,2) DEFAULT NULL,
  entry_date DATE DEFAULT NULL,
  narration VARCHAR(255) DEFAULT NULL,
  PRIMARY KEY (entry_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 13. Table: users
CREATE TABLE IF NOT EXISTS users (
  user_id INT NOT NULL AUTO_INCREMENT,
  username VARCHAR(50) NOT NULL UNIQUE,
  password VARCHAR(255) NOT NULL,
  role VARCHAR(20) NOT NULL,
  PRIMARY KEY (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO users (username, password, role) VALUES
  ('admin', 'admin123', 'admin'),
  ('accountant', 'account123', 'accountant'),
  ('viewer', 'viewer123', 'viewer')
ON DUPLICATE KEY UPDATE username=username;

-- 14. Triggers
DELIMITER $$
CREATE TRIGGER before_payment_insert
BEFORE INSERT ON payments
FOR EACH ROW
BEGIN
  IF NEW.payment_id IS NULL OR NEW.payment_id = '' THEN
    SET NEW.payment_id = (
      SELECT CONCAT('PY', LPAD(
        IFNULL(
          MAX(CAST(SUBSTRING(payment_id, 3) AS UNSIGNED)), 0
        ) + 1, 5, '0'))
      FROM payments
    );
  END IF;
END$$

CREATE TRIGGER before_receipt_insert
BEFORE INSERT ON receipts
FOR EACH ROW
BEGIN
  IF NEW.receipt_id IS NULL OR NEW.receipt_id = '' THEN
    SET NEW.receipt_id = (
      SELECT CONCAT('RV', LPAD(
        IFNULL(
          MAX(CAST(SUBSTRING(receipt_id, 3) AS UNSIGNED)), 0
        ) + 1, 5, '0'))
      FROM receipts
    );
  END IF;
END$$
DELIMITER ;

-- End of setup script
