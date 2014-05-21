SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL,ALLOW_INVALID_DATES';

-- -----------------------------------------------------
-- Schema mydb
-- -----------------------------------------------------
-- -----------------------------------------------------
-- Schema forum_db
-- -----------------------------------------------------
DROP SCHEMA IF EXISTS `forum_db` ;
CREATE SCHEMA IF NOT EXISTS `forum_db` DEFAULT CHARACTER SET utf8 ;
USE `forum_db` ;

-- -----------------------------------------------------
-- Table `forum_db`.`user`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `forum_db`.`user` ;

CREATE TABLE IF NOT EXISTS `forum_db`.`user` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `username` VARCHAR(255) NULL DEFAULT NULL,
  `password` VARCHAR(255) NOT NULL,
  `email` VARCHAR(255) NOT NULL,
  `name` VARCHAR(255) NULL DEFAULT NULL,
  `isAnonymous` TINYINT(3) UNSIGNED NOT NULL DEFAULT '0',
  `about` VARCHAR(255) NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `email_UNIQUE` (`email` ASC),
  UNIQUE INDEX `username_UNIQUE` (`username` ASC))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `forum_db`.`followers`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `forum_db`.`followers` ;

CREATE TABLE IF NOT EXISTS `forum_db`.`followers` (
  `follower` INT UNSIGNED NOT NULL,
  `followee` INT UNSIGNED NOT NULL,
  PRIMARY KEY (`follower`, `followee`),
  INDEX `fk_user_has_user_user1_idx` (`followee` ASC),
  INDEX `fk_user_has_user_user_idx` (`follower` ASC),
  CONSTRAINT `fk_user_has_user_user`
    FOREIGN KEY (`follower`)
    REFERENCES `forum_db`.`user` (`id`)
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_user_has_user_user1`
    FOREIGN KEY (`followee`)
    REFERENCES `forum_db`.`user` (`id`)
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `forum_db`.`forum`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `forum_db`.`forum` ;

CREATE TABLE IF NOT EXISTS `forum_db`.`forum` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(255) NOT NULL,
  `short_name` VARCHAR(255) NOT NULL,
  `user` VARCHAR(255) NOT NULL,
  `user_id` INT UNSIGNED NOT NULL,
  PRIMARY KEY (`id`, `user_id`),
  UNIQUE INDEX `short_name_UNIQUE` (`short_name` ASC),
  INDEX `fk_forum_user1_idx` (`user_id` ASC),
  INDEX `user_INDEX` (`user` ASC),
  CONSTRAINT `fk_forum_user1`
    FOREIGN KEY (`user_id`)
    REFERENCES `forum_db`.`user` (`id`)
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `forum_db`.`thread`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `forum_db`.`thread` ;

CREATE TABLE IF NOT EXISTS `forum_db`.`thread` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `date` DATETIME NOT NULL,
  `isClosed` TINYINT(3) UNSIGNED NOT NULL DEFAULT '0',
  `isDeleted` TINYINT(3) UNSIGNED NOT NULL DEFAULT '0',
  `title` VARCHAR(255) NOT NULL,
  `slug` VARCHAR(255) NOT NULL,
  `posts` INT(10) UNSIGNED NOT NULL DEFAULT '0',
  `message` MEDIUMTEXT NOT NULL,
  `likes` INT(11) NOT NULL DEFAULT '0',
  `dislikes` INT(11) NOT NULL DEFAULT '0',
  `points` INT(11) NOT NULL DEFAULT '0',
  `user` VARCHAR(255) NOT NULL,
  `forum` VARCHAR(255) NOT NULL,
  `forum_id` INT UNSIGNED NOT NULL,
  `user_id` INT UNSIGNED NOT NULL,
  PRIMARY KEY (`id`, `forum_id`, `user_id`),
  INDEX `fk_thread_forum1_idx` (`forum_id` ASC),
  INDEX `fk_thread_user1_idx` (`user_id` ASC),
  INDEX `user_INDEX` (`user` ASC),
  INDEX `forum_INDEX` (`forum` ASC),
  CONSTRAINT `fk_thread_forum1`
    FOREIGN KEY (`forum_id`)
    REFERENCES `forum_db`.`forum` (`id`)
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_thread_user1`
    FOREIGN KEY (`user_id`)
    REFERENCES `forum_db`.`user` (`id`)
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `forum_db`.`post`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `forum_db`.`post` ;

CREATE TABLE IF NOT EXISTS `forum_db`.`post` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `date` DATETIME NOT NULL,
  `dislikes` INT(11) NOT NULL DEFAULT 0,
  `likes` INT(11) NOT NULL DEFAULT '0',
  `isApproved` TINYINT(3) UNSIGNED NOT NULL DEFAULT '0',
  `isDeleted` TINYINT(3) UNSIGNED NOT NULL DEFAULT '0',
  `isEdited` TINYINT(3) UNSIGNED NOT NULL DEFAULT '0',
  `isHighlighted` TINYINT(3) UNSIGNED NOT NULL DEFAULT '0',
  `isSpam` TINYINT(3) UNSIGNED NOT NULL DEFAULT '0',
  `message` MEDIUMTEXT NOT NULL,
  `parent` INT UNSIGNED NULL DEFAULT NULL,
  `points` INT(11) NOT NULL DEFAULT '0',
  `forum` VARCHAR(255) NOT NULL,
  `user` VARCHAR(255) NOT NULL,
  `user_id` INT UNSIGNED NOT NULL,
  `thread_id` INT UNSIGNED NOT NULL,
  PRIMARY KEY (`id`, `user_id`, `thread_id`),
  INDEX `fk_post_user1_idx` (`user_id` ASC),
  INDEX `fk_post_thread1_idx` (`thread_id` ASC),
  INDEX `fk_post_parent_1_idx` (`parent` ASC),
  INDEX `user_INDEX` (`user` ASC),
  INDEX `forum_INDEX` (`forum` ASC),
  CONSTRAINT `fk_post_user1`
    FOREIGN KEY (`user_id`)
    REFERENCES `forum_db`.`user` (`id`)
    ON DELETE RESTRICT
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_post_thread1`
    FOREIGN KEY (`thread_id`)
    REFERENCES `forum_db`.`thread` (`id`)
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_post_parent_1`
    FOREIGN KEY (`parent`)
    REFERENCES `forum_db`.`post` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `forum_db`.`subscriptions`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `forum_db`.`subscriptions` ;

CREATE TABLE IF NOT EXISTS `forum_db`.`subscriptions` (
  `user_id` INT UNSIGNED NOT NULL,
  `thread_id` INT UNSIGNED NOT NULL,
  PRIMARY KEY (`user_id`, `thread_id`),
  INDEX `fk_user_subscribed_thread1_idx` (`thread_id` ASC),
  INDEX `fk_userId_to_user_id_idx` (`user_id` ASC),
  CONSTRAINT `fk_userId_to_user_id`
    FOREIGN KEY (`user_id`)
    REFERENCES `forum_db`.`user` (`id`),
  CONSTRAINT `fk_threadId_to_thread_id`
    FOREIGN KEY (`thread_id`)
    REFERENCES `forum_db`.`thread` (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
