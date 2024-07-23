CREATE TABLE IF NOT EXISTS `large_department` (
    `id` INT NOT NULL AUTO_INCREMENT,
    `name` VARCHAR(255) NOT NULL,
    `kitchen_ids` VARCHAR(500) NOT NULL,
    `user_id` INT NOT NULL,
    PRIMARY KEY (`id`)
);
CREATE TABLE IF NOT EXISTS `big_kitchens` (
    `id` INT NOT NULL AUTO_INCREMENT,
    `name` VARCHAR(255) NOT NULL,
    `dep_ids` VARCHAR(500) NOT NULL,
    `user_id` INT NOT NULL,
    PRIMARY KEY (`id`)
);
CREATE TABLE IF NOT EXISTS `sub_department` (
    `id` INT NOT NULL AUTO_INCREMENT,
    `name` VARCHAR(255) NOT NULL,
    `user_id` INT NOT NULL,
    PRIMARY KEY (`id`)
);
CREATE TABLE IF NOT EXISTS `employees` (
    `id` INT NOT NULL AUTO_INCREMENT,
    `name` VARCHAR(255) NOT NULL,
    `title` VARCHAR(255) NOT NULL,
    `default_dep` VARCHAR(255) NOT NULL,
    `user_id` INT NOT NULL,
    PRIMARY KEY (`id`)
);

CREATE TABLE IF NOT EXISTS `schedules` (
    `id` INT NOT NULL AUTO_INCREMENT,
    `week` VARCHAR(255) NOT NULL,
    `schedule_json` LONGTEXT,
    `user_id` INT NOT NULL,
    PRIMARY KEY (`id`)
);

CREATE TABLE IF NOT EXISTS `programs` (
    `id` INT NOT NULL AUTO_INCREMENT,
    `name` VARCHAR(255) NOT NULL,
    `user_id` INT NOT NULL,
    PRIMARY KEY (`id`)
)

CREATE TABLE IF NOT EXISTS `titles` (
    `id` INT NOT NULL AUTO_INCREMENT,
    `name` VARCHAR(255) NOT NULL,
    `user_id` INT NOT NULL,
    PRIMARY KEY (`id`)
)


CREATE TABLE IF NOT EXISTS `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `role` varchar(255) NOT NULL,
  `admin` int(11) NOT NULL,
  `owner` int(11) NOT NULL DEFAULT 0,
  `parent_id` int(11) NOT NULL DEFAULT 1,
  `password` varchar(500) NOT NULL,
  `email` varchar(255) NOT NULL
);