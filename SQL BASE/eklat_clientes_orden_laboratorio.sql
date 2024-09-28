-- MySQL dump 10.13  Distrib 8.0.38, for Win64 (x86_64)
--
-- Host: localhost    Database: eklat_clientes
-- ------------------------------------------------------
-- Server version	9.0.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `orden_laboratorio`
--

DROP TABLE IF EXISTS `orden_laboratorio`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `orden_laboratorio` (
  `orden_lab_id` int NOT NULL AUTO_INCREMENT,
  `pedido_id` int DEFAULT NULL,
  `montura` varchar(100) DEFAULT NULL,
  `color` varchar(50) DEFAULT NULL,
  `material_lentes` varchar(50) DEFAULT NULL,
  `ar` varchar(50) DEFAULT NULL,
  `progresivo` varchar(50) DEFAULT NULL,
  `gama_progresivo` varchar(50) DEFAULT NULL,
  `monofocal` varchar(50) DEFAULT NULL,
  `opcion_monofocal` varchar(50) DEFAULT NULL,
  `fotocromatico` varchar(50) DEFAULT NULL,
  `bifocal` varchar(50) DEFAULT NULL,
  `af` varchar(50) DEFAULT NULL,
  `corredor` varchar(50) DEFAULT NULL,
  `adicional` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`orden_lab_id`),
  KEY `pedido_id` (`pedido_id`),
  CONSTRAINT `orden_laboratorio_ibfk_1` FOREIGN KEY (`pedido_id`) REFERENCES `pedidos` (`pedido_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-09-16  1:13:38
