-- MySQL dump 10.13  Distrib 8.2.0, for macos13.5 (arm64)
--
-- Host: 10.16.40.111    Database: database_discovery
-- ------------------------------------------------------
-- Server version	8.0.18-google

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
SET @MYSQLDUMP_TEMP_LOG_BIN = @@SESSION.SQL_LOG_BIN;
SET @@SESSION.SQL_LOG_BIN= 0;

--
-- GTID state at the beginning of the backup 
--

SET @@GLOBAL.GTID_PURGED=/*!80000 '+'*/ '9440a4dd-5c10-11ed-a9fc-42010a10286e:1-13649009';

--
-- Table structure for table `tminstance_type`
--

DROP TABLE IF EXISTS `tminstance_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tminstance_type` (
  `seq_id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'primary key',
  `instance_type` varchar(25) NOT NULL COMMENT 'cloudsql|gce',
  `database_type` varchar(25) NOT NULL COMMENT 'mysql|oracle|postgresql|sqlserver',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `created_by` varchar(25) DEFAULT NULL,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_by` varchar(25) DEFAULT NULL,
  PRIMARY KEY (`seq_id`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tminstance_type`
--

LOCK TABLES `tminstance_type` WRITE;
/*!40000 ALTER TABLE `tminstance_type` DISABLE KEYS */;
INSERT INTO `tminstance_type` VALUES (1,'cloudsql','mysql','2024-01-10 14:40:50','interface','2024-01-10 14:40:50','interface'),(2,'cloudsql','sqlserver','2024-01-10 14:40:50','interface','2024-01-10 14:40:50','interface'),(3,'cloudsql','postgresql','2024-01-10 14:41:16','interface','2024-01-10 14:41:16','interface'),(4,'cloudsql','oracle','2024-01-10 14:41:16','interface','2024-01-10 14:41:16','interface'),(5,'gce','mysql','2024-01-10 14:42:21','interface','2024-01-10 14:42:21','interface'),(6,'gce','sqlserver','2024-01-10 14:42:21','interface','2024-01-10 14:42:21','interface'),(7,'gce','postgresql','2024-01-10 14:42:21','interface','2024-01-10 14:42:21','interface'),(8,'gce','oracle','2024-01-10 14:42:21','interface','2024-01-10 14:42:21','interface'),(12,'onpremis','mysql','2024-01-10 14:43:10','interface','2024-01-10 14:43:10','interface'),(13,'onpremis','sqlserver','2024-01-10 14:43:10','interface','2024-01-10 14:43:10','interface'),(14,'onpremis','postgresql','2024-01-10 14:43:10','interface','2024-01-10 14:43:10','interface'),(15,'onpremis','oracle','2024-01-10 14:43:10','interface','2024-01-10 14:43:10','interface');
/*!40000 ALTER TABLE `tminstance_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tmproject`
--

DROP TABLE IF EXISTS `tmproject`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tmproject` (
  `seq_id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'primary key',
  `project_number` int(11) NOT NULL COMMENT 'project number on gcp',
  `project_id` varchar(25) NOT NULL COMMENT 'project id on gcp',
  `project_name` varchar(250) NOT NULL COMMENT 'project name on gcp',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `created_by` varchar(25) DEFAULT NULL,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_by` varchar(25) DEFAULT NULL,
  PRIMARY KEY (`seq_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tmproject`
--

LOCK TABLES `tmproject` WRITE;
/*!40000 ALTER TABLE `tmproject` DISABLE KEYS */;
/*!40000 ALTER TABLE `tmproject` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ttddatabase`
--

DROP TABLE IF EXISTS `ttddatabase`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ttddatabase` (
  `seq_id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'primary key',
  `h_database_id` int(11) NOT NULL COMMENT 'FK from tthdatabase | seq_id',
  `database_size_gb` float NOT NULL COMMENT 'database size',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `created_by` varchar(25) DEFAULT NULL,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_by` varchar(25) DEFAULT NULL,
  PRIMARY KEY (`seq_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ttddatabase`
--

LOCK TABLES `ttddatabase` WRITE;
/*!40000 ALTER TABLE `ttddatabase` DISABLE KEYS */;
/*!40000 ALTER TABLE `ttddatabase` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ttdindex_discovery`
--

DROP TABLE IF EXISTS `ttdindex_discovery`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ttdindex_discovery` (
  `seq_id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'primary key',
  `h_table_id` int(11) NOT NULL COMMENT 'FK from tthtable_discovery|seq_id',
  `index_name` varchar(100) NOT NULL COMMENT 'table name',
  `index_size_mb` float NOT NULL COMMENT 'index size in megabyte on specific table',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `created_by` varchar(25) DEFAULT NULL,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_by` varchar(25) DEFAULT NULL,
  PRIMARY KEY (`seq_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ttdindex_discovery`
--

LOCK TABLES `ttdindex_discovery` WRITE;
/*!40000 ALTER TABLE `ttdindex_discovery` DISABLE KEYS */;
/*!40000 ALTER TABLE `ttdindex_discovery` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ttdinstance`
--

DROP TABLE IF EXISTS `ttdinstance`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ttdinstance` (
  `seq_id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'primary key',
  `h_instance_id` int(11) NOT NULL COMMENT 'FK from tthinstance | seq_id',
  `cpu_core` int(11) NOT NULL COMMENT 'cpu core instance',
  `memory_gb` float NOT NULL COMMENT 'memory in gigabyte on instance',
  `free_disk_gb` float DEFAULT NULL COMMENT 'free disk capacity in gigabyte on instance',
  `total_disk_gb` float DEFAULT NULL COMMENT 'total disk capacity in gigabyte on instance',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `created_by` varchar(25) DEFAULT NULL,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_by` varchar(25) DEFAULT NULL,
  PRIMARY KEY (`seq_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ttdinstance`
--

LOCK TABLES `ttdinstance` WRITE;
/*!40000 ALTER TABLE `ttdinstance` DISABLE KEYS */;
/*!40000 ALTER TABLE `ttdinstance` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ttdtable_discovery`
--

DROP TABLE IF EXISTS `ttdtable_discovery`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ttdtable_discovery` (
  `seq_id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'primary key',
  `h_table_id` int(11) NOT NULL COMMENT 'FK from tthtable_discovery|seq_id',
  `total_row` int(11) NOT NULL COMMENT 'total row on table',
  `table_size_mb` float NOT NULL COMMENT 'table size in megabyte on database',
  `last_updated` datetime DEFAULT CURRENT_TIMESTAMP COMMENT 'last date data scrap',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `created_by` varchar(25) DEFAULT NULL,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_by` varchar(25) DEFAULT NULL,
  PRIMARY KEY (`seq_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ttdtable_discovery`
--

LOCK TABLES `ttdtable_discovery` WRITE;
/*!40000 ALTER TABLE `ttdtable_discovery` DISABLE KEYS */;
/*!40000 ALTER TABLE `ttdtable_discovery` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tthdatabase`
--

DROP TABLE IF EXISTS `tthdatabase`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tthdatabase` (
  `seq_id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'primary key',
  `h_instance_id` int(11) NOT NULL COMMENT 'FK from tthinstance | seq_id',
  `database_name` varchar(25) NOT NULL COMMENT 'database name on instance',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `created_by` varchar(25) DEFAULT NULL,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_by` varchar(25) DEFAULT NULL,
  PRIMARY KEY (`seq_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tthdatabase`
--

LOCK TABLES `tthdatabase` WRITE;
/*!40000 ALTER TABLE `tthdatabase` DISABLE KEYS */;
/*!40000 ALTER TABLE `tthdatabase` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tthinstance`
--

DROP TABLE IF EXISTS `tthinstance`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tthinstance` (
  `seq_id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'primary key',
  `project_id` int(11) NOT NULL COMMENT 'FK from tmproject|seq_id',
  `instance_type` int(11) NOT NULL COMMENT 'FK from tminstance_type|seq_id',
  `ip_address` varchar(25) NOT NULL COMMENT 'ip address instance',
  `connection_name` varchar(50) NOT NULL COMMENT 'connection name on instance detail',
  `is_replica` tinyint(4) DEFAULT '0' COMMENT '0 master | 1 is replica',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `created_by` varchar(25) DEFAULT NULL,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_by` varchar(25) DEFAULT NULL,
  PRIMARY KEY (`seq_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tthinstance`
--

LOCK TABLES `tthinstance` WRITE;
/*!40000 ALTER TABLE `tthinstance` DISABLE KEYS */;
/*!40000 ALTER TABLE `tthinstance` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tthtable_discovery`
--

DROP TABLE IF EXISTS `tthtable_discovery`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tthtable_discovery` (
  `seq_id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'primary key',
  `h_database_id` int(11) NOT NULL COMMENT 'FK from tthdatabase | seq_id',
  `table_name` varchar(50) NOT NULL COMMENT 'table_name on database',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `created_by` varchar(25) DEFAULT NULL,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_by` varchar(25) DEFAULT NULL,
  PRIMARY KEY (`seq_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tthtable_discovery`
--

LOCK TABLES `tthtable_discovery` WRITE;
/*!40000 ALTER TABLE `tthtable_discovery` DISABLE KEYS */;
/*!40000 ALTER TABLE `tthtable_discovery` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ttuser_instance`
--

DROP TABLE IF EXISTS `ttuser_instance`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ttuser_instance` (
  `seq_id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'primary key',
  `m_instance_id` int(11) NOT NULL COMMENT 'FK from tthinstance | seq_id',
  `username` varchar(25) NOT NULL COMMENT 'username from instance',
  `privileges` text NOT NULL COMMENT 'current privileges on instance',
  `expired_date` datetime NOT NULL COMMENT 'user will be expired at datetime',
  `expired_stats` varchar(2) NOT NULL COMMENT 'N is Not Expired | Y is Expired',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `created_by` varchar(25) DEFAULT NULL,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_by` varchar(25) DEFAULT NULL,
  PRIMARY KEY (`seq_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ttuser_instance`
--

LOCK TABLES `ttuser_instance` WRITE;
/*!40000 ALTER TABLE `ttuser_instance` DISABLE KEYS */;
/*!40000 ALTER TABLE `ttuser_instance` ENABLE KEYS */;
UNLOCK TABLES;
SET @@SESSION.SQL_LOG_BIN = @MYSQLDUMP_TEMP_LOG_BIN;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-01-12 15:07:19
