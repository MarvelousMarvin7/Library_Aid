-- Sets up mysql server for Library Aid database

CREATE DATABASE IF NOT EXISTS liaid_dev_db;
CREATE USER IF NOT EXISTS 'liaid_dev'@'localhost' IDENTIFIED BY 'liaid_dev_pwd';
GRANT ALL PRIVILEGES ON `liaid_dev_db`.* TO 'liaid_dev'@'localhost';
GRANT SELECT ON `performance_schema`.* TO 'liaid_dev'@'localhost';

FLUSH PRIVILEGES;
