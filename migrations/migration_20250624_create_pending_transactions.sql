CREATE TABLE `pending_transactions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `transaction_type` enum('payment','receipt') NOT NULL,
  `account_name` varchar(100) NOT NULL,
  `amount` decimal(10,2) NOT NULL,
  `mop` varchar(50) NOT NULL,
  `narration` varchar(255) NOT NULL,
  `transaction_date` date NOT NULL,
  `remarks` varchar(255) DEFAULT NULL,
  `author` varchar(100) DEFAULT NULL,
  `item_name` varchar(100) DEFAULT NULL,
  `description` varchar(100) DEFAULT NULL,
  `property_type` varchar(50) DEFAULT NULL,
  `fd_duration` varchar(50) DEFAULT NULL,
  `fd_interest` varchar(20) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
