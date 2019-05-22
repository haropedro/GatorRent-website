-- Initialize the database.

CREATE database gatorrent_db;

USE gatorrent_db;

CREATE TABLE `user_table` (
  `user_id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `user_name` VARCHAR(30) NOT NULL,
  `password` VARCHAR(63) NOT NULL,
  `email` VARCHAR(40) NOT NULL,
  `user_type` TINYINT(1) NOT NULL,
  `timestamp` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE INDEX `user_name_UNIQUE` (`user_name` ASC));

 CREATE TABLE `image_table` (
 `image_id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
 `image_path` VARCHAR(200) NOT NULL);

 CREATE TABLE `rent_type_table` (
  `rent_type_id` INT(12) NOT NULL,
  `type` VARCHAR(40) NOT NULL,
  PRIMARY KEY (`rent_type_id`),
  UNIQUE INDEX `username_UNIQUE` (`type` ASC));

CREATE TABLE `listing_table` (
  `listing_id` INT NOT NULL AUTO_INCREMENT,
  `user_id` INT NOT NULL,
  `rent_type_id` INT(12) NOT NULL,
  `price` DECIMAL(12) NOT NULL,
  `dist_from_campus` DECIMAL(12),
  `is_pet` TINYINT(1) NOT NULL,
  `is_shared` TINYINT(1) NOT NULL,
  `status` VARCHAR(100),
  `street` VARCHAR(100) NOT NULL,
  `city` VARCHAR(100) NOT NULL,
  `state` VARCHAR(100) NOT NULL,
  `country` VARCHAR(100) DEFAULT 'United States',
  `postcode` INT(5) NOT NULL,
  `lat` FLOAT(10.6),
  `long` FLOAT(10.6),
  `isApproved` TINYINT(1) DEFAULT 0,
  `image_id` INT,
  `thumbnail_path` VARCHAR(200),
  `description` TEXT,
  `title` TINYTEXT,
  `timestamp` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`listing_id`, `rent_type_id`, `user_id`),
  CONSTRAINT `user_id`
	FOREIGN KEY (`user_id`)
	REFERENCES `gatorrent_db`.`user_table` (`user_id`)
	ON DELETE NO ACTION
	ON UPDATE NO ACTION,
  CONSTRAINT `rent_type_id`
	FOREIGN KEY (`rent_type_id`)
	REFERENCES `gatorrent_db`.`rent_type_table` (`rent_type_id`)
	ON DELETE NO ACTION
	ON UPDATE NO ACTION);

CREATE TABLE `message_table` (
  `message_id` INT NOT NULL AUTO_INCREMENT,
  `body` VARCHAR(100) NOT NULL,
  `sender_user_id` INT(12) NOT NULL,
  `reciever_user_id` INT(12) NOT NULL,
  `listing_id` INT(12) NOT NULL,
  `timestamp` TIMESTAMP(6) NOT NULL,
  PRIMARY KEY (`message_id`),
  INDEX `sender_user_id_idx` (`sender_user_id` ASC),
  INDEX `reciever_user_id_idx` (`reciever_user_id` ASC),
  INDEX `listing_id_idx` (`listing_id` ASC),
  CONSTRAINT `sender_user_id`
	FOREIGN KEY (`sender_user_id`)
	REFERENCES `gatorrent_db`.`user_table` (`user_id`)
	ON DELETE NO ACTION
	ON UPDATE NO ACTION,
  CONSTRAINT `reciever_user_id`
	FOREIGN KEY (`reciever_user_id`)
	REFERENCES `gatorrent_db`.`user_table` (`user_id`)
	ON DELETE NO ACTION
	ON UPDATE NO ACTION,
  CONSTRAINT `listing_id`
	FOREIGN KEY (`listing_id`)
	REFERENCES `gatorrent_db`.`listing_table` (`listing_id`)
	ON DELETE NO ACTION
	ON UPDATE NO ACTION);

ALTER TABLE message_table AUTO_INCREMENT=10010;


CREATE TABLE `message_admin_table` (
  `message_id_admin` INT NOT NULL AUTO_INCREMENT,
  `body_admin` VARCHAR(100) NOT NULL,
  `user_id` INT(12) NOT NULL,
  `timestamp` TIMESTAMP(6) NOT NULL,
  PRIMARY KEY (`message_id_admin`),
  INDEX `admin_user_id_idx` (`message_id_admin` ASC),
  CONSTRAINT `message_id_admin`
	FOREIGN KEY (`user_id`)
	REFERENCES `gatorrent_db`.`user_table` (`user_id`)
	ON DELETE NO ACTION
	ON UPDATE NO ACTION);

ALTER TABLE message_admin_table AUTO_INCREMENT=10010;

--
-- INSERT DUMMY DATA
--

-- USER_TABLE:
-- 0 for admin
-- 1 for normal users
INSERT INTO `user_table` (`user_name`, `password`, `email`, `user_type`) VALUES
('chirag', 'chirag', 'cagarwal@mail.sfsu.edu', 1),
('cheryl', 'cheryl', 'cheryl@mail.com', 1),
('johanna', 'johanna', 'jhadgu@mail.sfsu.edu', 1),
('ermias', 'ermias', 'ehaile@mail.sfsu.edu', 1),
('jerry', 'jerry', 'jwong@mail.sfsu.edu', 1),
('landlord', 'landlord','landlord@mail.com', 1),
('admin', '$2b$12$dfBFrCJVOm0s8YqaLgJbau0SMoyMEg5/oQbAyINDN1gwmc1Dvc83i', 'admin@mail.com', 0);
-- admin password: admin

-- RENT_TYPE_TABLE:
insert into rent_type_table values (1,"Apartment");
insert into rent_type_table values (2,"House");
insert into rent_type_table values (3,"Room");

-- IMAGE_TABLE:
insert into image_table values (1, "50_Chumasero.jpg");
insert into image_table values (2, "100_Font.jpg");
insert into image_table values (3, "150_Searano.jpg");

-- LISTING_TABLE:
INSERT INTO `listing_table` (`listing_id`, `user_id`, `title`, `description`, `rent_type_id`, `price`, `dist_from_campus`, `is_pet`, `is_shared`, `status`, `street`, `city`, `state`, `country`, `postcode`, `lat`, `long`, `isApproved`, `image_id`, `thumbnail_path`, `timestamp`) VALUES
(10, 1, 'Luxury apartment',  'apartment', 1, '850', '5', 1, 1, 'available', '50 Chumasero', 'San Francisco', 'CA', 'US',  92132, 37.7148, -122.474, 1, 1, 'https://marketplace.canva.com/MADGyVipG3g/4/screen/canva-round-brown-wooden-stool-near-brown-sofa-MADGyVipG3g.jpg', '2019-04-04 01:11:41.822361'),
(11, 1, 'Ocean view room', 'room', 3, '950', '1', 0, 0, 'available', '50 Font', 'San Francisco', 'CA', 'US',  95132, 37.7148, -122.474, 1, 1, 'https://marketplace.canva.com/MADGybsz64k/4/thumbnail_large/canva-gray-throw-pillow-on-white-padded-armchair-MADGybsz64k.jpg', '2019-04-04 01:11:30.560611'),
(12, 2, 'Affordable apartment', 'apartment', 1, '1550', '15', 1, 1, 'available', '150 Searano', 'San Francisco', 'CA', 'US', 94132, 37.7148, -122.474, 1, 3, 'https://marketplace.canva.com/MADGvrjQHI8/7/screen/canva-white-dining-table-near-bar-table-MADGvrjQHI8.jpg', '2019-04-04 01:11:06.793463'),
(13, 3, 'Cozy home', 'house', 2, '2850', '5', 1, 0, 'available', '50 Chumasero', 'San Francisco', 'CA', 'US', 94113, 37.7148, -122.474, 1, 1, 'https://marketplace.canva.com/MAAgcMpQ-oY/1/screen/canva-relaxing-by-the-pool-MAAgcMpQ-oY.jpg', '2019-04-04 01:10:45.909387'),
(14, 4, 'Spacious apartment', 'apartment', 1, '650', '8', 1, 1, 'available', '150 Font', 'San Francisco', 'CA', 'US', 94132, 37.7148, -122.474, 1, 2, 'https://marketplace.canva.com/MADGvkJj6KQ/7/screen/canva-living-room-with-couches-and-coffee-table-MADGvkJj6KQ.jpg', '2019-04-04 01:10:16.734927');

-- MESSAGE_TABLE:
insert into message_table values (10000,"message_1",1,1,10,"2019-02-02 22:11:03");
insert into message_table values (10001,"message_2",2,2,11,"2019-02-02 22:11:03");
insert into message_table values (10002,"message_3",3,3,12,"2019-02-02 22:11:03");
insert into message_table values (10003,"message_4",4,4,13,"2019-02-02 22:11:03");
insert into message_table values (10004,"message_5",5,5,14,"2019-02-02 22:11:03");
