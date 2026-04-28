CREATE DATABASE IF NOT EXISTS courses
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE courses;

CREATE TABLE users (
  id              BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  email           VARCHAR(255) NOT NULL,
  password_hash   VARCHAR(255) NOT NULL,
  name            VARCHAR(120) NOT NULL,
  created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uq_users_email (email)
)

CREATE TABLE courses (
  id              BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  title           VARCHAR(200) NOT NULL,
  slug            VARCHAR(200) NOT NULL,
  short_desc      VARCHAR(500) NOT NULL,
  long_desc       TEXT,
  price_cents     INT UNSIGNED NOT NULL,          -- store price as integer cents
  is_active       TINYINT(1) NOT NULL DEFAULT 1,
  created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uq_courses_slug (slug),
  KEY idx_courses_active (is_active),
  FULLTEXT KEY ftx_courses_text (title, short_desc, long_desc)  -- for lexical/hybrid search
)

CREATE TABLE discounts (
  id              BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  code            VARCHAR(64) NOT NULL,
  type            ENUM('PERCENT','AMOUNT') NOT NULL,
  value           DECIMAL(7,2) NOT NULL,          -- PERCENT: 0–100, AMOUNT: currency units
  is_active       TINYINT(1) NOT NULL DEFAULT 1,
  created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uq_discounts_code (code)
)

CREATE TABLE payments (
  id              BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  user_id         BIGINT UNSIGNED NOT NULL,
  course_id       BIGINT UNSIGNED NOT NULL,
  discount_id     BIGINT UNSIGNED NULL,
  provider        ENUM('MOCK') NOT NULL DEFAULT 'MOCK',
  provider_ref    VARCHAR(128) NOT NULL,          -- mock receipt/id
  amount_cents    INT UNSIGNED NOT NULL,
  currency        CHAR(3) NOT NULL DEFAULT 'USD',
  status          ENUM('PENDING','PAID','FAILED') NOT NULL DEFAULT 'PENDING',
  created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

  CONSTRAINT fk_payment_user
    FOREIGN KEY (user_id)   REFERENCES users(id)    ON DELETE CASCADE,
  CONSTRAINT fk_payment_course
    FOREIGN KEY (course_id) REFERENCES courses(id)  ON DELETE RESTRICT,
  CONSTRAINT fk_payment_discount
    FOREIGN KEY (discount_id) REFERENCES discounts(id) ON DELETE SET NULL,

  UNIQUE KEY uq_payment_provider_ref (provider_ref),
  KEY idx_payment_status (status),
  KEY idx_payment_user_course (user_id, course_id)
);

CREATE TABLE enrollments (
  id              BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  user_id         BIGINT UNSIGNED NOT NULL,
  course_id       BIGINT UNSIGNED NOT NULL,
  payment_id      BIGINT UNSIGNED NOT NULL,
  status          ENUM('PENDING','PAID','CANCELLED') NOT NULL DEFAULT 'PAID',
  created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

  CONSTRAINT fk_enroll_user
    FOREIGN KEY (user_id)   REFERENCES users(id)    ON DELETE CASCADE,
  CONSTRAINT fk_enroll_course
    FOREIGN KEY (course_id) REFERENCES courses(id)  ON DELETE RESTRICT,
  CONSTRAINT fk_enroll_payment
    FOREIGN KEY (payment_id) REFERENCES payments(id) ON DELETE RESTRICT,

  UNIQUE KEY uq_enroll_user_course (user_id, course_id),
  UNIQUE KEY uq_enroll_payment (payment_id),
  KEY idx_enroll_status (status)
);



-- choose one host: localhost (TCP) or % (any host)
CREATE USER 'prreddy'@'localhost' IDENTIFIED WITH caching_sha2_password BY 'db1234';
GRANT ALL PRIVILEGES ON courses.* TO 'prreddy'@'localhost';
FLUSH PRIVILEGES;

