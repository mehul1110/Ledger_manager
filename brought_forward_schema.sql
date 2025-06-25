CREATE TABLE IF NOT EXISTS `brought_forward_balances` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `account_name` varchar(255) NOT NULL,
  `balance` decimal(15,2) NOT NULL,
  `month` int(11) NOT NULL,
  `year` int(11) NOT NULL,
  `carry_forward_date` date NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `account_month_year` (`account_name`,`month`,`year`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
