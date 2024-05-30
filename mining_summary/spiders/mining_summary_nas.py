from enum import Enum, auto

import scrapy
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
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
        print(
            f"Attempting to insert: ID={id}, Category={category}, Summary={summary[:30]}...")  # Print a snippet of summary

        try:
            cursor.execute(query, args)
            connection.commit()
            print("Successfully added summary to the database.")
            return cursor.lastrowid
        except Error as e:
            print(f"Error while inserting summary: {e}")
            return None
        finally:
            cursor.close()

    def get_article_id_by_link(self, connection, link):
        cursor = connection.cursor()
        query = "SELECT id FROM article WHERE link = %s"

        try:
            cursor.execute(query, (link,))
            record = cursor.fetchone()
            if record:
                print(f"ID artykułu dla linku {link} to: {record[0]}")
                return record[0]
            else:
                print(f"No article found for link: {link}")
                return None
        except Error as e:
            print(f"Błąd '{e}' podczas dodawania artykułu")
            return None
        finally:
            cursor.close()

    def save_to_db(self, connection, parameter: WhatToSave, id, link, scrapy_text=None, summary=None, category=None):
        if connection is not None:
            cursor = connection.cursor()
            try:
                if parameter == WhatToSave.LINK:
                    query = "INSERT INTO article (link) VALUES (%s)"
                    args = (link,)
                elif parameter == WhatToSave.ARTICLE:
                    query = "INSERT INTO article (id, link, scrapy_text) VALUES (%s, %s, %s)"
                    args = (id, link, scrapy_text)
                elif parameter == WhatToSave.SCRAPY:
                    query = "UPDATE article SET scrapy_text = %s WHERE link = %s"
                    args = (scrapy_text, link)
                elif parameter == WhatToSave.SUMMARY:
                    query = "INSERT INTO article_details (article_id, category, summary) VALUES (%s, %s, %s)"
                    args = (id, category, summary)
                print(f"Executing query: {query} with args {args}")  # Debug print

                cursor.execute(query, args)
                connection.commit()
                print(f"Data saved for {parameter}. ID: {id}, Category: {category}")
            except Error as e:
                print(f"Error while saving data for {parameter}: {e}")
            finally:
                cursor.close()
        else:
            print("No database connection available.")

    # # Dane, które chcesz zapisać
    # id =2
    # link = "http://example.com/article"
    # scrapy_text = "Tutaj wpisz pobrany tekst"

    # Pamiętaj, aby zamknąć połączenie z bazą danych po zakończeniu

    def fetch_summaries_by_category(self, connection, category):
        cursor = connection.cursor()
        query = "SELECT a.link, a.id, ad.category, ad.summary FROM article a JOIN article_details ad ON a.id = ad.article_id "
        try:
            cursor.execute(query, (category,))
            records = cursor.fetchall()
            return records
        except Error as e:
            print(f"Błąd '{e}' podczas pobierania streszczeń")
            return []
        finally:
            cursor.close()

    def generate_pdf_by_category(self, connection, category):
            records = self.fetch_summaries_by_category(connection, category)
            if not records:
                print(f"No summaries found for category {category}")
                return

            pdf_filename = f"{category}_newsletter.pdf"
            c = canvas.Canvas(pdf_filename, pagesize=letter)
            width, height = letter

            y = height - 40
            for link, summary in records:
                text = f"{summary}\n{link}\n\n"
                for line in text.split('\n'):
                    c.drawString(40, y, line)
                    y -= 14
                    if y < 40:
                        c.showPage()
                        y = height - 40

            c.save()
            print(f"PDF generated: {pdf_filename}")

        # Pamiętaj, aby zamknąć połączenie z bazą danych po zakończeniu


class MiningSpider(scrapy.Spider):
    name = "mining_summary"

    host_name = 'localhost'
    user_name = 'newsletter'
    user_password = 'newsletter'
    db_name = 'newsletter'
    db = Database()
    connection = None
    summary_instructions = ""

    def __init__(self, *args, **kwargs):
        super(MiningSpider, self).__init__(*args, **kwargs)
        self.load_summary_instructions()

    def load_summary_instructions(self):
        # Load summary instructions from 'typeofreaders.txt' using UTF-8 encoding
        with open('typeofreaders.txt', 'r', encoding='utf-8') as file:
            self.summary_instructions = file.read()

    def start_requests(self):
        self.connection = self.db.connect_to_db(self.host_name, self.user_name, self.user_password, self.db_name)
        with open('links.txt', 'r') as file:
            start_urls = [url.strip() for url in file.readlines() if url.strip()]
            print(f"URLs loaded: {start_urls}")

        for url in start_urls:
            self.db.save_to_db(self.connection, WhatToSave.LINK, 1, url)

        for url in start_urls:
            yield scrapy.Request(url, self.parse)

    def parse(self, response):
        self.logger.info(f"Status: {response.status}, URL: {response.url}")
        if response.status != 200:
            self.logger.error(f"Failed to fetch {response.url}")
            self.save_summary(response.url, "Not enough information.")
            return

        page_content = self.extract_content(response, response.url)
        if not page_content:
            self.logger.error(f"No content extracted from: {response.url}")
            self.save_summary(response.url, "Not enough information.")
            return

        cleaned_content = self.clean_text(' '.join(page_content))
        summaries = self.generate_summaries_for_all_types(cleaned_content)

        summary_results = ""
        for reader_type, summary in summaries.items():
            if not summary:
                summary = "Not enough information."
            summary_results += f"{reader_type}: {summary}\n"

        self.save_summary(response.url, summary_results.strip())
        self.logger.info(f"Extracted content: {cleaned_content[:100]}")

        summary_filename = f"{response.url.split('/')[-2]}_summary.txt"
        with open(summary_filename, 'w', encoding='utf-8') as f:
            f.write(summary_results.strip())

        article_id = self.db.get_article_id_by_link(self.connection, response.url)
        if article_id:
            for reader_type, summary in summaries.items():
                if not summary:
                    summary = "Not enough information."
                self.db.save_to_db(self.connection, WhatToSave.SUMMARY, article_id, response.url, summary=summary,
                                   category=reader_type)

    def extract_content(self, response, url):
        if "koreabizwire.com" in url:
            return response.xpath('//div[@class="entry-content"]//p//text()').getall()
        else:
            return response.xpath('//p//text()').getall()

    def clean_text(self, text):
        text = html.unescape(text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def generate_summaries_for_all_types(self, text):
        summaries = {}
        for reader_type in ["TO", "PO", "R", "SO", "FOCM", "AO"]:
            prompt = f"{self.summary_instructions}\n\nType: {reader_type}\n\n{text}"
            summary = generate_openai_completion(prompt)
            if len(summary.split()) < 10:  # assuming summary should be at least 10 words
                summaries[reader_type] = "Not enough information."
            else:
                summaries[reader_type] = summary
        return summaries

    def save_summary(self, url, summary):
        print(f"URL: {url}, Summary: {summary}")

    def closed(self, reason):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("Database connection closed")

if __name__ == "__main__":
    process = CrawlerProcess()
    process.crawl(MiningSpider)
    process.start()
