CREATE DATABASE metaports;

USE metaports;

CREATE TABLE background (user_id INT, is_vr INT);
ALTER TABLE `metaports`.`background` CHANGE COLUMN `user_id` `user_id` INT NOT NULL AUTO_INCREMENT, ADD PRIMARY KEY (`user_id`);

CREATE TABLE mt_training_result (play_id INT, capture_time INT, accuracy INT);
ALTER TABLE `metaports`.`mt_training_result` CHANGE COLUMN `play_id` `play_id` INT NOT NULL AUTO_INCREMENT, ADD PRIMARY KEY (`play_id`);

CREATE TABLE player_data (play_id INT, total INT, perfect_frame INT, awesome_frame INT, good_frame INT, ok_frame INT, bad_frame INT);
ALTER TABLE `metaports`.`player_data` CHANGE COLUMN `play_id` `play_id` INT NOT NULL AUTO_INCREMENT, ADD PRIMARY KEY (`play_id`);

CREATE TABLE program_running (program_id INT, is_running INT);
ALTER TABLE `metaports`.`program_running` CHANGE COLUMN `program_id` `program_id` INT NOT NULL AUTO_INCREMENT, ADD PRIMARY KEY (`program_id`);

CREATE TABLE hand (hand_id INT, rx INT, ry INT, lx INT, ly INT);
ALTER TABLE `metaports`.`hand` CHANGE COLUMN `hand_id` `hand_id` INT NOT NULL AUTO_INCREMENT, ADD PRIMARY KEY (`hand_id`);

CREATE TABLE recommend (user_id INT, content_url VARCHAR(255));

CREATE TABLE basic_data (play_id INT, reaction_time FLOAT, on_air FLOAT, squat_jump INT, knee_punch INT, balance_test INT);

-- TRUNCATE TABLE mt_training_result;
-- TRUNCATE TABLE player_data;
-- TRUNCATE TABLE background;
-- TRUNCATE TABLE program_running;
-- TRUNCATE TABLE hand;
-- TRUNCATE TABLE basic_data;

-- INSERT INTO hand (hand_id, rx, ry, lx, ly) VALUES (1, 100, 200, 300, 400);

SELECT * FROM mt_training_result;
SELECT * FROM player_data;
SELECT * FROM background;
SELECT * FROM program_running;
SELECT * FROM hand;
SELECT * FROM basic_data;