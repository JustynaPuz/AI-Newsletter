CREATE DATABASE IF NOT EXISTS newsletter;
USE newsletter;
CREATE TABLE IF NOT EXISTS article(
    id INT AUTO_INCREMENT PRIMARY KEY,
    link VARCHAR(2083),
    scrapy_text MEDIUMTEXT,
    abstrait_text TEXT
);

CREATE TABLE IF NOT EXISTS article_categories(
    article_id INT,
    category VARCHAR(255),
    PRIMARY KEY (article_id, category)
);