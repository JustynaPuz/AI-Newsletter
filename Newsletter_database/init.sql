CREATE DATABASE IF NOT EXISTS newsletter;
USE newsletter;
CREATE TABLE IF NOT EXISTS article(
    id INT AUTO_INCREMENT PRIMARY KEY,
    link VARCHAR(2083),
    scrapy_text MEDIUMTEXT
);

CREATE TABLE IF NOT EXISTS summaries (
    id INT AUTO_INCREMENT PRIMARY KEY,
    article_id INT,
    summary TEXT,
    category VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE,
    INDEX (category)
);

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(100) UNIQUE,
    password VARCHAR(255),
    preferences JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) UNIQUE,
    description TEXT
);

CREATE TABLE IF NOT EXISTS subscriptions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    category_id INT,
    frequency ENUM('daily', 'weekly', 'monthly') DEFAULT 'weekly',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE,
    UNIQUE KEY (user_id, category_id)
);

-- Dodanie indeksów dla poprawy wydajności
CREATE INDEX idx_article_link ON articles(link);
CREATE INDEX idx_summary_article_id ON summaries(article_id);
CREATE INDEX idx_user_email ON users(email);