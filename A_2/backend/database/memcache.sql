-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL,ALLOW_INVALID_DATES';

-- -----------------------------------------------------
-- Schema estore
-- -----------------------------------------------------
DROP SCHEMA IF EXISTS `memcache` ;
CREATE SCHEMA IF NOT EXISTS `memcache` DEFAULT CHARACTER SET utf8 ;
USE `memcache` ;

DROP TABLE IF EXISTS `memcache`.`images` ;

CREATE TABLE IF NOT EXISTS `memcache`.`images` (
  `key` VARCHAR(255) NOT NULL,
  `location` VARCHAR(255) NOT NULL,
  PRIMARY KEY (`key`))
ENGINE = InnoDB;

DROP TABLE IF EXISTS `memcache`.`cache_properties` ;

CREATE TABLE IF NOT EXISTS `memcache`.`cache_properties` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `max_capacity` INT NOT NULL,
  `replacement_policy` VARCHAR(255) NOT NULL,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;

DROP TABLE IF EXISTS `memcache`.`cache_policies` ;

CREATE TABLE IF NOT EXISTS `memcache`.`cache_policies` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `max_miss_rate` FLOAT NOT NULL,
  `min_miss_rate` FLOAT NOT NULL,
  `expansion_ratio` FLOAT NOT NULL,
  `shrink_ratio` FLOAT NOT NULL,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`))
  
ENGINE = InnoDB;

SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;

START TRANSACTION;
USE `memcache`;
INSERT INTO `memcache`.`images` (`key`, `location`) VALUES ('hot', 'hot.jpeg');
INSERT INTO `memcache`.`images` (`key`, `location`) VALUES ('cold', 'cold.jpeg');
INSERT INTO `memcache`.`images` (`key`, `location`) VALUES ('flower', 'flower.jpeg');
INSERT INTO `memcache`.`images` (`key`, `location`) VALUES ('kings', 'kings.png');
INSERT INTO `memcache`.`images` (`key`, `location`) VALUES ('lakers', 'lakers.png');
INSERT INTO `memcache`.`images` (`key`, `location`) VALUES ('heat', 'heat.png');
INSERT INTO `memcache`.`images` (`key`, `location`) VALUES ('spurs', 'spurs.png');
INSERT INTO `memcache`.`images` (`key`, `location`) VALUES ('suns', 'suns.png');

COMMIT;

-- DROP USER IF EXISTS 'admin'@'localhost';
-- CREATE USER 'admin'@'localhost' IDENTIFIED BY 'ece1779';
-- GRANT ALL PRIVILEGES ON *.* TO 'admin'@'localhost';
