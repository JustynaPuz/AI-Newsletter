CREATE DATABASE IF NOT EXISTS newsletter;
USE newsletter;
CREATE TABLE IF NOT EXISTS article(
    id INT AUTO_INCREMENT PRIMARY KEY,
    link VARCHAR(2083),
    scrapy_text MEDIUMTEXT
);

CREATE TABLE IF NOT EXISTS article_details(
    article_id INT,
    category VARCHAR(255),
    summary MEDIUMTEXT,
    PRIMARY KEY (article_id, category)
);