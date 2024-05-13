from enum import Enum, auto

import scrapy
from scrapy.crawler import CrawlerProcess
import os
import html
import re
import nltk
from model import client  # Import klienta Azure OpenAI z model.py
from model import generate_openai_completion
import mysql.connector
from mysql.connector import Error

nltk.download('punkt')

host_name = 'localhost'
user_name = 'newsletter'
user_password = 'newsletter'
db_name = 'newsletter'


class WhatToSave(Enum):
    LINK = auto()
    ARTICLE = auto()
    SUMMARY = auto()
    SCRAPY = auto()


class Database:

    def connect_to_db(self, host_name, user_name, user_password, db_name):
        connection = None
        try:
            connection = mysql.connector.connect(
                host=host_name,
                user=user_name,
                passwd=user_password,
                database=db_name
            )
            print("Połączenie z bazą danych MySQL udane")
        except Error as e:
            print(f"Błąd '{e}' podczas połączenia z bazą danych")

        return connection
        # Połączenie z bazą danych

    def insert_article(self, connection, id, link, scrapy_text):
        cursor = connection.cursor()
        query = "INSERT INTO article (id, link, scrapy_text) VALUES (%s, %s, %s)"
        args = (id, link, scrapy_text)

        try:
            cursor.execute(query, args)
            connection.commit()
            print("Pomyślnie dodano artykuł do bazy danych")
            return cursor.lastrowid
        except Error as e:
            print(f"Błąd '{e}' podczas dodawania artykułu")
            return None
        finally:
            cursor.close()

    def insert_link(self, connection, link):
        cursor = connection.cursor()
        query = "INSERT INTO article (link) VALUES (%s)"
        args = (link,)

        try:
            cursor.execute(query, args)
            connection.commit()
            print("Pomyślnie dodano artykuł do bazy danych")
            return cursor.lastrowid
        except Error as e:
            print(f"Błąd '{e}' podczas dodawania artykułu")
            return None
        finally:
            cursor.close()

    def insert_scrapy_text(self, connection, link, scrapy_text):
        cursor = connection.cursor()
        query = "UPDATE article SET scrapy_text = %s WHERE link = %s"
        args = (scrapy_text, link)

        try:
            cursor.execute(query, args)
            connection.commit()
            print("Pomyślnie dodano artykuł do bazy danych")
            return cursor.lastrowid
        except Error as e:
            print(f"Błąd '{e}' podczas dodawania artykułu")
            return None
        finally:
            cursor.close()

    def insert_summary(self, connection, id, category, summary):
        cursor = connection.cursor()
        query = "INSERT INTO article_details (article_id, category, summary) VALUES (%s, %s, %s)"
        args = (id, category, summary)

        try:
            cursor.execute(query, args)
            connection.commit()
            print("Pomyślnie dodano artykuł do bazy danych")
            return cursor.lastrowid
        except Error as e:
            print(f"Błąd '{e}' podczas dodawania artykułu")
            return None
        finally:
            cursor.close()

    def get_article_id_by_link(self, connection, link):
        cursor = connection.cursor()
        query = "SELECT id FROM article WHERE link = %s"

        try:
            cursor.execute(query, (link,))
            record = cursor.fetchone()
            print(f"ID artykułu dla linku {link} to: {record[0]}")
            return record[0]
        except Error as e:
            print(f"Błąd '{e}' podczas dodawania artykułu")
            return None
        finally:
            cursor.close()

    def save_to_db(self, connection, parameter: WhatToSave, id, link, scrapy_text=None, summary=None, category=None):
        if connection is not None:
            if parameter == WhatToSave.LINK:
                article_id = self.insert_link(connection, link)
            elif parameter == WhatToSave.ARTICLE:
                article_id = self.insert_article(connection, id, link, summary)
            elif parameter == WhatToSave.SCRAPY:
                article_id = self.insert_scrapy_text(connection, link, scrapy_text)
            elif parameter == WhatToSave.SUMMARY:
                article_id = self.insert_summary(connection, id, category, summary)

            if article_id is not None:
                print(f"Dodano artykuł z ID: {article_id}")
            else:
                print("Nie udało się dodać artykułu")
        else:
            print("Nie udało się połączyć z bazą danych")

    # # Dane, które chcesz zapisać
    # id =2
    # link = "http://example.com/article"
    # scrapy_text = "Tutaj wpisz pobrany tekst"

    # Pamiętaj, aby zamknąć połączenie z bazą danych po zakończeniu


class MiningSpider(scrapy.Spider):
    name = "mining_summary"

    host_name = 'localhost'
    user_name = 'newsletter'
    user_password = 'newsletter'
    db_name = 'newsletter'
    db = Database()
    connection = None

    def start_requests(self):
        self.connection = self.db.connect_to_db(host_name, user_name, user_password, db_name)
        with open('links.txt', 'r') as file:
            start_urls = [url.strip() for url in file.readlines() if url.strip()]
            print(f"URLs loaded: {start_urls}")

        for url in start_urls:
            self.db.save_to_db(self.connection, WhatToSave.LINK, 1, url)

        for url in start_urls:
            yield scrapy.Request(url, self.parse)

    def parse(self, response):
        self.logger.info(f"Processing: {response.url}")
        if "koreabizwire.com" in response.url:
            page_content = response.xpath('//div[@class="entry-content"]//p//text()').getall()
        else:
            page_content = response.xpath('//p//text()').getall()

        if not page_content:
            self.logger.error(f"No content extracted from: {response.url}")
            return

        self.logger.info(f"Extracted content: {page_content[:100]}")
        content = ' '.join(page_content)
        cleaned_content = self.clean_text(content)

        # Save scrapy text to db
        self.db.save_to_db(self.connection, WhatToSave.SCRAPY, 9, response.url, cleaned_content)

        # Save original content to a file
        raw_filename = f"{response.url.split('/')[-2]}_raw.txt"
        with open(raw_filename, 'w', encoding='utf-8') as f:
            f.write(cleaned_content)

        # Generate summary from the cleaned content
        summary = self.generate_summary(cleaned_content)

        # get article id
        article_id = self.db.get_article_id_by_link(self.connection, response.url)
        category = "None"

        if article_id:
            print(f"Znaleziono ID: {article_id}")

        # Save summary to db
        self.db.save_to_db(self.connection, WhatToSave.SUMMARY, article_id, None, None, summary, category)

        # Save summary to a file
        summary_filename = f"{response.url.split('/')[-2]}_summary.txt"
        with open(summary_filename, 'w', encoding='utf-8') as f:
            f.write(summary)

    def clean_text(self, text):
        text = html.unescape(text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def generate_summary(self, text):
        # Poprawione wywołanie funkcji generate_openai_completion
        prompt = "Summarize this text in max 4 sentences: " + text
        return generate_openai_completion(prompt)

    def closed(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("Połączenie z bazą danych zostało zamknięte")


if __name__ == "__main__":
    process = CrawlerProcess()
    process.crawl(MiningSpider)
    process.start()
