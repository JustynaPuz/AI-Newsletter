import html
import re
from enum import Enum, auto

import mysql.connector
import nltk
import scrapy
from mysql.connector import Error
from scrapy.crawler import CrawlerProcess

from model import generate_openai_completion

nltk.download('punkt')

# Database connection credentials
host_name = 'localhost'
user_name = 'newsletter'
user_password = 'newsletter'
db_name = 'newsletter'

# Enumeration for different data storage actions
class WhatToSave(Enum):
    LINK = auto()
    ARTICLE = auto()
    SUMMARY = auto()
    SCRAPY = auto()

# Database class for handling database operations
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

    # Insert an article into the database if it does not already exist
    def insert_article(self, connection, id, link, scrapy_text):
        cursor = connection.cursor()
        # Najpierw sprawdzamy, czy link już istnieje
        query = "SELECT id FROM article WHERE link = %s"
        cursor.execute(query, (link,))
        if cursor.fetchone():
            print("Artykuł o danym linku już istnieje w bazie danych.")
            return None
        else:
            # Dodajemy artykuł, ponieważ nie istnieje
            insert_query = "INSERT INTO article (id, link, scrapy_text) VALUES (%s, %s, %s)"
            args = (id, link, scrapy_text)
            try:
                cursor.execute(insert_query, args)
                connection.commit()
                print("Pomyślnie dodano artykuł do bazy danych")
                return cursor.lastrowid
            except Error as e:
                print(f"Błąd '{e}' podczas dodawania artykułu")
                return None
            finally:
                cursor.close()

    # Insert link into the database
    def insert_link(self, connection, link):
        cursor = connection.cursor()
        query = "SELECT id FROM article WHERE link = %s"
        cursor.execute(query, (link,))
        if cursor.fetchone():
            print("Link już istnieje w bazie danych.")
            return None
        else:
            insert_query = "INSERT INTO article (link) VALUES (%s)"
            args = (link,)
            try:
                cursor.execute(insert_query, args)
                connection.commit()
                print("Pomyślnie dodano link do bazy danych")
                return cursor.lastrowid
            except Error as e:
                print(f"Błąd '{e}' podczas dodawania linku")
                return None
            finally:
                cursor.close()

    # Save acrapy text to the database
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

    # Save summary to the database
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

    # Save different types of data to the database
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

    def fetch_summaries_by_category(self, connection, category):
        cursor = connection.cursor()
        query = "SELECT a.link, a.id, ad.category, ad.summary FROM article a JOIN article_details ad ON a.id = ad.article_id WHERE ad.category = %s "
        try:
            cursor.execute(query, (category,))
            records = cursor.fetchall()
            return records
        except Error as e:
            print(f"Błąd '{e}' podczas pobierania streszczeń")
            return []
        finally:
            cursor.close()

# Define a Scrapy Spider for crawling websites and extracting content
class MiningSpider(scrapy.Spider):
    name = "mining_summary"

    # Database connection settings
    host_name = 'localhost'
    user_name = 'newsletter'
    user_password = 'newsletter'
    db_name = 'newsletter'
    db = Database()
    connection = None
    summary_instructions = ""


    def __init__(self, *args, **kwargs):
        super(MiningSpider, self).__init__(*args, **kwargs)
        self.load_summary_instructions() # Load summary instructions upon initialization


    def load_summary_instructions(self):
        # Load summary instructions from 'typeofreaders.txt' using UTF-8 encoding
        with open('typeofreaders.txt', 'r', encoding='utf-8') as file:
            self.summary_instructions = file.read()

    def start_requests(self):
        # Establish database connection
        self.connection = self.db.connect_to_db(self.host_name, self.user_name, self.user_password, self.db_name)
        with open('links.txt', 'r') as file:
            start_urls = [url.strip() for url in file.readlines() if url.strip()]
            print(f"URLs loaded: {start_urls}")

        # Save each URL to the database and initiate a request
        for url in start_urls:
            self.db.save_to_db(self.connection, WhatToSave.LINK, 1, url)

        for url in start_urls:
            yield scrapy.Request(url, self.parse)


    def parse(self, response):
        """ Parse the content of a web page, extract and process text data. """
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
        # Save extracted text to database
        self.db.save_to_db(self.connection, WhatToSave.SCRAPY, None, response.url, cleaned_content)
        summaries = self.generate_summaries_for_all_types(cleaned_content)

        # Compile and log summary results
        summary_results = ""
        for reader_type, summary in summaries.items():
            if not summary:
                summary = "Not enough information."
            summary_results += f"{reader_type}: {summary}\n"
        # Save summaries to database
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
        """ Extract textual content from specific parts of a webpage based on its structure. """
        if "koreabizwire.com" in url:
            return response.xpath('//div[@class="entry-content"]//p//text()').getall()
        else:
            return response.xpath('//p//text()').getall()

    def clean_text(self, text):
        """ Clean extracted text by removing HTML entities and extra spaces. """
        text = html.unescape(text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def generate_summaries_for_all_types(self, text):
        """ Generate summaries for various reader types using a pre-defined OpenAI model. """
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
        """ Log summary information for debugging and tracking. """
        print(f"URL: {url}, Summary: {summary}")

    def closed(self, reason):
        """ Log summary information for debugging and tracking. """
        if self.connection and self.connection.is_connected():
            self.connection.close()

            print("Database connection closed")

if __name__ == "__main__":
    process = CrawlerProcess()
    process.crawl(MiningSpider)
    process.start()




