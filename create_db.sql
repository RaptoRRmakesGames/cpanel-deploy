CREATE TABLE IF NOT EXISTS `big_kitchens` (
    `id` INT NOT NULL AUTO_INCREMENT,
    `name` VARCHAR(255) NOT NULL,
    `dep_ids` VARCHAR(500) NOT NULL,
    PRIMARY KEY (`id`)
);


CREATE TABLE IF NOT EXISTS `sub_department` (
    `id` INT NOT NULL AUTO_INCREMENT,
    `name` VARCHAR(255) NOT NULL,
    PRIMARY KEY (`id`)
);


CREATE TABLE IF NOT EXISTS `employees` (
    `id` INT NOT NULL AUTO_INCREMENT,
    `name` VARCHAR(255) NOT NULL,
    `title` VARCHAR(255) NOT NULL,
    `default_dep` VARCHAR(255) NOT NULL,
    PRIMARY KEY (`id`)
);

CREATE TABLE IF NOT EXISTS `schedules` (
    `id` INT NOT NULL AUTO_INCREMENT,
    `week` VARCHAR(255) NOT NULL,
    `schedule_json` LONGTEXT,
    PRIMARY KEY (`id`)
);

CREATE TABLE IF NOT EXISTS `programs` (
    `id` INT NOT NULL AUTO_INCREMENT,
    `name` VARCHAR(255) NOT NULL,
    PRIMARY KEY (`id`)
)