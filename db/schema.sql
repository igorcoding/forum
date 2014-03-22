SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL,ALLOW_INVALID_DATES';

DROP SCHEMA IF EXISTS `forum_db` ;
CREATE SCHEMA IF NOT EXISTS `forum_db` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci ;
USE `forum_db` ;

-- -----------------------------------------------------
-- Table `forum_db`.`user`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `forum_db`.`user` ;

CREATE TABLE IF NOT EXISTS `forum_db`.`user` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `username` VARCHAR(255) NOT NULL,
  `password` VARCHAR(255) NOT NULL,
  `email` VARCHAR(255) NOT NULL,
  `name` VARCHAR(255) NULL,
  `isAnonymous` TINYINT UNSIGNED NOT NULL,
  `about` VARCHAR(255) NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `email_UNIQUE` (`email` ASC),
  UNIQUE INDEX `username_UNIQUE` (`username` ASC))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `forum_db`.`forum`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `forum_db`.`forum` ;

CREATE TABLE IF NOT EXISTS `forum_db`.`forum` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(255) NOT NULL,
  `short_name` VARCHAR(255) NOT NULL,
  `user` VARCHAR(255) NOT NULL,
  `user_id` BIGINT UNSIGNED NOT NULL,
  PRIMARY KEY (`id`, `user_id`),
  UNIQUE INDEX `short_name_UNIQUE` (`short_name` ASC),
  INDEX `fk_forum_user1_idx` (`user_id` ASC),
  CONSTRAINT `fk_forum_user1`
    FOREIGN KEY (`user_id`)
    REFERENCES `forum_db`.`user` (`id`)
    ON DELETE RESTRICT
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `forum_db`.`thread`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `forum_db`.`thread` ;

CREATE TABLE IF NOT EXISTS `forum_db`.`thread` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `date` DATETIME NOT NULL,
  `dislikes` INT UNSIGNED NOT NULL,
  `likes` INT UNSIGNED NOT NULL,
  `isClosed` TINYINT UNSIGNED NOT NULL,
  `isDeleted` TINYINT UNSIGNED NOT NULL,
  `title` VARCHAR(255) NOT NULL,
  `slug` VARCHAR(255) NOT NULL,
  `message` MEDIUMTEXT NOT NULL,
  `user` VARCHAR(255) NOT NULL,
  `forum` VARCHAR(255) NOT NULL,
  `forum_id` BIGINT UNSIGNED NOT NULL,
  `user_id` BIGINT UNSIGNED NOT NULL,
  PRIMARY KEY (`id`, `forum_id`, `user_id`),
  UNIQUE INDEX `slug_UNIQUE` (`slug` ASC),
  INDEX `fk_thread_forum1_idx` (`forum_id` ASC),
  INDEX `fk_thread_user1_idx` (`user_id` ASC),
  CONSTRAINT `fk_thread_forum1`
    FOREIGN KEY (`forum_id`)
    REFERENCES `forum_db`.`forum` (`id`)
    ON DELETE RESTRICT
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_thread_user1`
    FOREIGN KEY (`user_id`)
    REFERENCES `forum_db`.`user` (`id`)
    ON DELETE RESTRICT
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `forum_db`.`post`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `forum_db`.`post` ;

CREATE TABLE IF NOT EXISTS `forum_db`.`post` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `date` DATETIME NOT NULL,
  `dislikes` INT UNSIGNED NOT NULL,
  `likes` INT UNSIGNED NOT NULL,
  `isApproved` TINYINT UNSIGNED NOT NULL,
  `isDeleted` TINYINT UNSIGNED NOT NULL,
  `isEdited` TINYINT UNSIGNED NOT NULL,
  `isHighlighted` TINYINT UNSIGNED NOT NULL,
  `isSpam` TINYINT UNSIGNED NOT NULL,
  `message` MEDIUMTEXT NOT NULL,
  `parent` BIGINT UNSIGNED NOT NULL,
  `points` INT UNSIGNED NOT NULL,
  `forum` VARCHAR(255) NOT NULL,
  `user` VARCHAR(45) NOT NULL,
  `user_id` BIGINT UNSIGNED NOT NULL,
  `thread_id` BIGINT UNSIGNED NOT NULL,
  PRIMARY KEY (`id`, `user_id`, `thread_id`),
  INDEX `fk_post_user1_idx` (`user_id` ASC),
  INDEX `fk_post_thread1_idx` (`thread_id` ASC),
  CONSTRAINT `fk_post_user1`
    FOREIGN KEY (`user_id`)
    REFERENCES `forum_db`.`user` (`id`)
    ON DELETE RESTRICT
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_post_thread1`
    FOREIGN KEY (`thread_id`)
    REFERENCES `forum_db`.`thread` (`id`)
    ON DELETE RESTRICT
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `forum_db`.`followers`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `forum_db`.`followers` ;

CREATE TABLE IF NOT EXISTS `forum_db`.`followers` (
  `follower` BIGINT UNSIGNED NOT NULL,
  `followee` BIGINT UNSIGNED NOT NULL,
  `unfollowed` TINYINT NOT NULL DEFAULT 0,
  PRIMARY KEY (`follower`, `followee`),
  INDEX `fk_user_has_user_user1_idx` (`followee` ASC),
  INDEX `fk_user_has_user_user_idx` (`follower` ASC),
  CONSTRAINT `fk_user_has_user_user`
    FOREIGN KEY (`follower`)
    REFERENCES `forum_db`.`user` (`id`)
    ON DELETE RESTRICT
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_user_has_user_user1`
    FOREIGN KEY (`followee`)
    REFERENCES `forum_db`.`user` (`id`)
    ON DELETE RESTRICT
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `forum_db`.`subscriptions`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `forum_db`.`subscriptions` ;

CREATE TABLE IF NOT EXISTS `forum_db`.`subscriptions` (
  `user_id` BIGINT UNSIGNED NOT NULL,
  `thread_id` BIGINT UNSIGNED NOT NULL,
  `unsubscribed` TINYINT NOT NULL,
  PRIMARY KEY (`user_id`, `thread_id`),
  INDEX `fk_user_subscribed_thread1_idx` (`thread_id` ASC),
  INDEX `fk_userId_to_user_id_idx` (`user_id` ASC),
  CONSTRAINT `fk_userId_to_user_id`
    FOREIGN KEY (`user_id`)
    REFERENCES `forum_db`.`user` (`id`)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT,
  CONSTRAINT `fk_threadId_to_thread_id`
    FOREIGN KEY (`thread_id`)
    REFERENCES `forum_db`.`thread` (`id`)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT)
ENGINE = InnoDB;

SET SQL_MODE = '';
GRANT USAGE ON *.* TO forum_db_user@localhost;
 DROP USER forum_db_user@localhost;
SET SQL_MODE='TRADITIONAL,ALLOW_INVALID_DATES';
CREATE USER 'forum_db_user'@'localhost' IDENTIFIED BY 'forum_db_user';

GRANT ALL ON `forum_db`.* TO 'forum_db_user'@'localhost';

SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
