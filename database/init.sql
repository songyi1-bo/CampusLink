-- Safe to execute repeatedly; no DROP statements.
CREATE DATABASE IF NOT EXISTS campuslink
    CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
USE campuslink;

CREATE TABLE IF NOT EXISTS `user` (
    id BIGINT NOT NULL AUTO_INCREMENT,
    username VARCHAR(32) COLLATE utf8mb4_bin NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    nickname VARCHAR(32) NOT NULL,
    avatar VARCHAR(255) NULL,
    created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    updated_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    PRIMARY KEY (id),
    UNIQUE KEY uq_user_username (username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS ride_trip (
	id BIGINT NOT NULL AUTO_INCREMENT,
	owner_id BIGINT NOT NULL,
	origin VARCHAR(80) NOT NULL,
	destination VARCHAR(80) NOT NULL,
	meeting_point VARCHAR(160) NOT NULL,
	origin_location JSON,
	destination_location JSON,
	meeting_location JSON,
	meeting_note VARCHAR(200) NOT NULL,
	departure_at DATETIME(6) NOT NULL,
	recruit_seats SMALLINT NOT NULL,
	estimated_cost NUMERIC(8, 2),
	contact_type VARCHAR(16) NOT NULL,
	contact_value VARCHAR(64) NOT NULL,
	note VARCHAR(500) NOT NULL,
	status VARCHAR(16) NOT NULL,
	created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
	updated_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
	PRIMARY KEY (id),
	CONSTRAINT ck_ride_seats CHECK (recruit_seats BETWEEN 1 AND 6),
	CONSTRAINT ck_ride_status CHECK (status IN ('scheduled','cancelled','completed')),
	CONSTRAINT ck_ride_cost CHECK (estimated_cost IS NULL OR estimated_cost BETWEEN 0 AND 9999.99),
	FOREIGN KEY(owner_id) REFERENCES user (id) ON DELETE RESTRICT,
    INDEX ix_ride_departure (status, departure_at, id),
    INDEX ix_ride_owner (owner_id, created_at, id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS ride_member (
	id BIGINT NOT NULL AUTO_INCREMENT,
	trip_id BIGINT NOT NULL,
	user_id BIGINT NOT NULL,
	status VARCHAR(16) NOT NULL,
	contact_type VARCHAR(16) NOT NULL,
	contact_value VARCHAR(64) NOT NULL,
	created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
	updated_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
	PRIMARY KEY (id),
	CONSTRAINT uq_ride_member UNIQUE (trip_id, user_id),
	CONSTRAINT ck_ride_member_status CHECK (status IN ('joined','withdrawn')),
	FOREIGN KEY(trip_id) REFERENCES ride_trip (id) ON DELETE RESTRICT,
	FOREIGN KEY(user_id) REFERENCES user (id) ON DELETE RESTRICT,
    INDEX ix_ride_members (trip_id, status),
    INDEX ix_ride_member_user (user_id, created_at, id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
-- Quest Module

CREATE TABLE IF NOT EXISTS book_listing (
	id BIGINT NOT NULL AUTO_INCREMENT,
	seller_id BIGINT NOT NULL,
	title VARCHAR(120) NOT NULL,
	author VARCHAR(80) NOT NULL,
	isbn VARCHAR(20),
	category VARCHAR(16) NOT NULL,
	condition_grade VARCHAR(16) NOT NULL,
	description VARCHAR(1000) NOT NULL,
	cover_images JSON NOT NULL,
	original_price NUMERIC(8, 2),
	price NUMERIC(8, 2) NOT NULL,
	is_negotiable TINYINT(1) NOT NULL DEFAULT 0,
	trade_method VARCHAR(16) NOT NULL,
	trade_location VARCHAR(160) NOT NULL,
	contact_type VARCHAR(16) NOT NULL,
	contact_value VARCHAR(64) NOT NULL,
	status VARCHAR(16) NOT NULL DEFAULT 'listed',
	view_count INT NOT NULL DEFAULT 0,
	created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
	updated_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
	PRIMARY KEY (id),
	CONSTRAINT ck_book_isbn CHECK (isbn IS NULL OR isbn REGEXP '^[0-9Xx-]{10,20}$'),
	CONSTRAINT ck_book_category CHECK (category IN ('textbook','reference','exam','literature','other')),
	CONSTRAINT ck_book_condition CHECK (condition_grade IN ('new','like_new','good','worn')),
	CONSTRAINT ck_book_price CHECK (price BETWEEN 0 AND 9999.99),
	CONSTRAINT ck_book_original_price CHECK (original_price IS NULL OR original_price BETWEEN 0 AND 9999.99),
	CONSTRAINT ck_book_discount CHECK (original_price IS NULL OR original_price >= price),
	CONSTRAINT ck_book_trade_method CHECK (trade_method IN ('meetup','delivery','either')),
	CONSTRAINT ck_book_status CHECK (status IN ('listed','reserved','sold','removed')),
	FOREIGN KEY(seller_id) REFERENCES user (id) ON DELETE RESTRICT,
    INDEX ix_book_browse (status, category, created_at, id),
    INDEX ix_book_seller (seller_id, created_at, id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS book_favorite (
	id BIGINT NOT NULL AUTO_INCREMENT,
	listing_id BIGINT NOT NULL,
	user_id BIGINT NOT NULL,
	created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
	PRIMARY KEY (id),
	CONSTRAINT uq_book_favorite UNIQUE (listing_id, user_id),
	FOREIGN KEY(listing_id) REFERENCES book_listing (id) ON DELETE RESTRICT,
	FOREIGN KEY(user_id) REFERENCES user (id) ON DELETE RESTRICT,
    INDEX ix_book_favorite_user (user_id, created_at, id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
CREATE TABLE IF NOT EXISTS quest_task (
    id BIGINT NOT NULL AUTO_INCREMENT,
    owner_id BIGINT NOT NULL,
    assignee_id BIGINT NULL,
    title VARCHAR(80) NOT NULL,
    description VARCHAR(1500) NOT NULL,
    category VARCHAR(16) NOT NULL,
    location VARCHAR(160) NOT NULL,
    reward NUMERIC(8,2) NOT NULL,
    deadline DATETIME(6) NOT NULL,
    contact_type VARCHAR(16) NOT NULL,
    contact_value VARCHAR(64) NOT NULL,
    assignee_contact_type VARCHAR(16) NULL,
    assignee_contact_value VARCHAR(64) NULL,
    completion_note VARCHAR(500) NOT NULL DEFAULT '',
    status VARCHAR(16) NOT NULL DEFAULT 'open',
    created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    updated_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    PRIMARY KEY (id),
    CONSTRAINT ck_quest_category CHECK (category IN ('delivery','study','repair','other')),
    CONSTRAINT ck_quest_status CHECK (status IN ('open','accepted','submitted','completed','cancelled')),
    CONSTRAINT ck_quest_reward CHECK (reward BETWEEN 0 AND 9999.99),
    CONSTRAINT ck_quest_assignee CHECK (assignee_id IS NULL OR assignee_id <> owner_id),
    FOREIGN KEY (owner_id) REFERENCES user(id) ON DELETE RESTRICT,
    FOREIGN KEY (assignee_id) REFERENCES user(id) ON DELETE RESTRICT,
    INDEX ix_quest_browse (status, category, deadline, id),
    INDEX ix_quest_owner (owner_id, created_at, id),
    INDEX ix_quest_assignee (assignee_id, created_at, id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
