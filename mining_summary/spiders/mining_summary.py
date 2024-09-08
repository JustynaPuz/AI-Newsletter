# from enum import Enum, auto
#
# import scrapy
# from scrapy.crawler import CrawlerProcess
# import os
# import html
# import re
# import nltk
# from model import client  # Import klienta Azure OpenAI z model.py
# from model import generate_openai_completion
# import mysql.connector
# from mysql.connector import Error
#
# nltk.download('punkt')
#
# host_name = 'localhost'
# user_name = 'newsletter'
# user_password = 'newsletter'
# db_name = 'newsletter'
#
#
# class WhatToSave(Enum):
#     LINK = auto()
#     ARTICLE = auto()
#     SUMMARY = auto()
#     SCRAPY = auto()
#
#
# class Database:
#
#     def connect_to_db(self, host_name, user_name, user_password, db_name):
#         connection = None
#         try:
#             connection = mysql.connector.connect(
#                 host=host_name,
#                 user=user_name,
#                 passwd=user_password,
#                 database=db_name
#             )
#             print("Połączenie z bazą danych MySQL udane")
#         except Error as e:
#             print(f"Błąd '{e}' podczas połączenia z bazą danych")
#
#         return connection
#         # Połączenie z bazą danych
#
#     def insert_article(self, connection, id, link, scrapy_text):
#         cursor = connection.cursor()
#         query = "INSERT INTO article (id, link, scrapy_text) VALUES (%s, %s, %s)"
#         args = (id, link, scrapy_text)
#
#         try:
#             cursor.execute(query, args)
#             connection.commit()
#             print("Pomyślnie dodano artykuł do bazy danych")
#             return cursor.lastrowid
#         except Error as e:
#             print(f"Błąd '{e}' podczas dodawania artykułu")
#             return None
#         finally:
#             cursor.close()
#
#     def insert_link(self, connection, link):
#         cursor = connection.cursor()
#         query = "INSERT INTO article (link) VALUES (%s)"
#         args = (link,)
#
#         try:
#             cursor.execute(query, args)
#             connection.commit()
#             print("Pomyślnie dodano artykuł do bazy danych")
#             return cursor.lastrowid
#         except Error as e:
#             print(f"Błąd '{e}' podczas dodawania artykułu")
#             return None
#         finally:
#             cursor.close()
#
#     def insert_scrapy_text(self, connection, link, scrapy_text):
#         cursor = connection.cursor()
#         query = "UPDATE article SET scrapy_text = %s WHERE link = %s"
#         args = (scrapy_text, link)
#
#         try:
#             cursor.execute(query, args)
#             connection.commit()
#             print("Pomyślnie dodano artykuł do bazy danych")
#             return cursor.lastrowid
#         except Error as e:
#             print(f"Błąd '{e}' podczas dodawania artykułu")
#             return None
#         finally:
#             cursor.close()
#
#     def insert_summary(self, connection, id, category, summary):
#         cursor = connection.cursor()
#         query = "INSERT INTO article_details (article_id, category, summary) VALUES (%s, %s, %s)"
#         args = (id, category, summary)
#
#         try:
#             cursor.execute(query, args)
#             connection.commit()
#             print("Pomyślnie dodano artykuł do bazy danych")
#             return cursor.lastrowid
#         except Error as e:
#             print(f"Błąd '{e}' podczas dodawania artykułu")
#             return None
#         finally:
#             cursor.close()
#
#     def get_article_id_by_link(self, connection, link):
#         cursor = connection.cursor()
#         query = "SELECT id FROM article WHERE link = %s"
#
#         try:
#             cursor.execute(query, (link,))
#             record = cursor.fetchone()
#             print(f"ID artykułu dla linku {link} to: {record[0]}")
#             return record[0]
#         except Error as e:
#             print(f"Błąd '{e}' podczas dodawania artykułu")
#             return None
#         finally:
#             cursor.close()
#
#     def save_to_db(self, connection, parameter: WhatToSave, id, link, scrapy_text=None, summary=None, category=None):
#         if connection is not None:
#             if parameter == WhatToSave.LINK:
#                 article_id = self.insert_link(connection, link)
#             elif parameter == WhatToSave.ARTICLE:
#                 article_id = self.insert_article(connection, id, link, summary)
#             elif parameter == WhatToSave.SCRAPY:
#                 article_id = self.insert_scrapy_text(connection, link, scrapy_text)
#             elif parameter == WhatToSave.SUMMARY:
#                 article_id = self.insert_summary(connection, id, category, summary)
#
#             if article_id is not None:
#                 print(f"Dodano artykuł z ID: {article_id}")
#             else:
#                 print("Nie udało się dodać artykułu")
#         else:
#             print("Nie udało się połączyć z bazą danych")
#
#     # # Dane, które chcesz zapisać
#     # id =2
#     # link = "http://example.com/article"
#     # scrapy_text = "Tutaj wpisz pobrany tekst"
#
#     # Pamiętaj, aby zamknąć połączenie z bazą danych po zakończeniu
#
#
# class MiningSpider(scrapy.Spider):
#     name = "mining_summary"
#
#     host_name = 'localhost'
#     user_name = 'newsletter'
#     user_password = 'newsletter'
#     db_name = 'newsletter'
#     db = Database()
#     connection = None
#     summary_instructions = ""
#
#     def __init__(self, *args, **kwargs):
#         super(MiningSpider, self).__init__(*args, **kwargs)
#         self.load_summary_instructions()
#
#     def load_summary_instructions(self):
#         # Load summary instructions from 'typeofreaders.txt' using UTF-8 encoding
#         with open('typeofreaders.txt', 'r', encoding='utf-8') as file:
#             lines = file.readlines()
#             # Assuming the specific summary instruction starts after a certain keyword in the file
#             start = False
#             for line in lines:
#                 if "Typical summary of this article:" in line:
#                     start = True
#                 if start:
#                     self.summary_instructions += line
#
#     def start_requests(self):
#         self.connection = self.db.connect_to_db(host_name, user_name, user_password, db_name)
#         with open('links.txt', 'r') as file:
#             start_urls = [url.strip() for url in file.readlines() if url.strip()]
#             print(f"URLs loaded: {start_urls}")
#
#         for url in start_urls:
#             self.db.save_to_db(self.connection, WhatToSave.LINK, 1, url)
#
#         for url in start_urls:
#             yield scrapy.Request(url, self.parse)
#
#     def parse(self, response):
#         self.logger.info(f"Processing: {response.url}")
#         if "koreabizwire.com" in response.url:
#             page_content = response.xpath('//div[@class="entry-content"]//p//text()').getall()
#         else:
#             page_content = response.xpath('//p//text()').getall()
#
#         if not page_content:
#             self.logger.error(f"No content extracted from: {response.url}")
#             return
#
#         self.logger.info(f"Extracted content: {page_content[:100]}")
#         content = ' '.join(page_content)
#         cleaned_content = self.clean_text(content)
#
#         # Generate summary from the cleaned content
#         summary = self.generate_summary(cleaned_content)
#
#         # Save summary to a file
#         summary_filename = f"{response.url.split('/')[-2]}_summary.txt"
#         with open(summary_filename, 'w', encoding='utf-8') as f:
#             f.write(summary)
#
#     def clean_text(self, text):
#         text = html.unescape(text)
#         text = re.sub(r'\s+', ' ', text)
#         return text.strip()
#
#     def generate_summary(self, text):
#         # Using the custom prompt from the loaded summary instructions
#         prompt = f"{self.summary_instructions}\n\n{text}"
#         return generate_openai_completion(prompt)
#
#     def closed(self):
#         if self.connection and self.connection.is_connected():
#             self.connection.close()
#             print("Database connection closed")
#
# if __name__ == "__main__":
#     process = CrawlerProcess()
#     process.crawl(MiningSpider)
#     process.start()

import scrapy
from scrapy.crawler import CrawlerProcess
from mining_summary.spiders.article_finder import ArticleFinder
from Newsletter_database.news_api import NewsAPI
from utils.text_processing import clean_text
from mining_summary.spiders.model import generate_summary
import logging
import os

class MiningSpider(scrapy.Spider):
    name = "mining_summary"

    def __init__(self, *args, **kwargs):
        super(MiningSpider, self).__init__(*args, **kwargs)
        # Inicjalizacja komponentów
        self.article_finder = ArticleFinder()
        self.news_api = NewsAPI()
        self.summary_instructions = self.load_summary_instructions()
        self.logger = logging.getLogger(self.name)

    def load_summary_instructions(self):
        try:
            with open('config/typeofreaders.txt', 'r', encoding='utf-8') as file:
                return file.read()
        except FileNotFoundError:
            self.logger.error("Plik 'typeofreaders.txt' nie znaleziony.")
            return ""
        except Exception as e:
            self.logger.error(f"Błąd podczas wczytywania instrukcji: {str(e)}")
            return ""

    def start_requests(self):
        # Rozpoczęcie procesu scrapowania dla nowych artykułów
        new_articles = self.article_finder.find_new_articles()
        for article in new_articles:
            yield scrapy.Request(article['link'], self.parse, meta={'source': article['source']})

    def parse(self, response):
        # Parsowanie odpowiedzi i przetwarzanie artykułu
        content = self.extract_content(response)
        if not content:
            self.logger.error(f"Nie udało się wyekstrahować treści z: {response.url}")
            return

        # Czyszczenie i przetwarzanie treści
        cleaned_content = clean_text(content)
        summary = generate_summary(self.summary_instructions + "\n\n" + cleaned_content)
        category = self.categorize_tech_article(cleaned_content)

        try:
            if not self.news_api.article_exists(response.url):
                article_id = self.news_api.save_article(
                    link=response.url,
                    title=response.css('title::text').get(),
                    scrapy_text=cleaned_content,
                    source=response.meta['source']
                )

                if article_id:
                    self.news_api.save_summary(
                        article_id=article_id,
                        summary=summary,
                        category=category
                    )
                    self.logger.info(f"Artykuł i streszczenie zapisane: {response.url}")
                else:
                    self.logger.error(f"Nie udało się zapisać artykułu: {response.url}")
            else:
                self.logger.info(f"Artykuł już istnieje: {response.url}")
        except Exception as e:
            self.logger.error(f"Błąd podczas przetwarzania artykułu {response.url}: {str(e)}")

        self.save_summary_to_file(response.url, summary)

    def categorize_tech_article(self, content):
        categories = {
            'AI': ['sztuczna inteligencja', 'uczenie maszynowe', 'deep learning', 'AI', 'machine learning'],
            'IoT': ['internet rzeczy', 'IoT', 'połączone urządzenia', 'smart home', 'inteligentne miasta'],
            'CS': ['cyberbezpieczeństwo', 'bezpieczeństwo cyfrowe', 'hacking', 'ochrona danych', 'kryptografia'],
            'RA': ['robotyka', 'automatyzacja', 'robot', 'coboty', 'RPA'],
            'TC': ['chmura', 'cloud computing', 'edge computing', 'fog computing', 'centrum danych'],
            'TM': ['5G', '6G', 'smartfon', 'aplikacje mobilne', 'technologie mobilne'],
            'BT': ['biotechnologia', 'inżynieria genetyczna', 'CRISPR', 'terapia genowa', 'bioczujniki'],
            'NT': ['nanotechnologia', 'nanomateriały', 'nanoroboty', 'nanostruktury'],
            'EO': ['energia odnawialna', 'fotowoltaika', 'energia wiatrowa', 'magazynowanie energii'],
            'TK': ['komputer kwantowy', 'kryptografia kwantowa', 'czujniki kwantowe', 'internet kwantowy']
        }

        content_lower = content.lower()
        for category, keywords in categories.items():
            if any(keyword in content_lower for keyword in keywords):
                return category

        return 'OT'  # Other Technology, jeśli nie pasuje do żadnej konkretnej kategorii

    def save_summary_to_file(self, url, summary):
        directory = "summaries"
        if not os.path.exists(directory):
            os.makedirs(directory)

        filename = f"{directory}/{url.split('/')[-1]}_summary.txt"
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(summary)
            self.logger.info(f"Streszczenie zapisane do pliku: {filename}")
        except Exception as e:
            self.logger.error(f"Błąd podczas zapisywania streszczenia do pliku {filename}: {str(e)}")

    def extract_content(self, response):
        # Ekstrakcja treści z różnych źródeł
        url = response.url.lower()

        if "bbc.co.uk" in url:
            return ' '.join(response.css('.article__body-content p::text').getall())
        elif "nytimes.com" in url:
            return ' '.join(response.css('.StoryBodyCompanionColumn p::text').getall())
        elif "techcrunch.com" in url:
            return ' '.join(response.css('.article-content p::text').getall())
        elif "theverge.com" in url:
            return ' '.join(response.css('.c-entry-content p::text').getall())
        elif "wired.com" in url:
            return ' '.join(response.css('.body__inner-container p::text').getall())
        elif "cnet.com" in url:
            return ' '.join(response.css('.article-main-body p::text').getall())
        elif "arstechnica.com" in url:
            return ' '.join(response.css('.article-content p::text').getall())
        elif "zdnet.com" in url:
            return ' '.join(response.css('.article-body p::text').getall())
        elif "engadget.com" in url:
            return ' '.join(response.css('.article-text p::text').getall())
        elif "technologyreview.com" in url:
            return ' '.join(response.css('.article-body__content p::text').getall())
        elif "computerworld.com" in url:
            return ' '.join(response.css('.article-body p::text').getall())
        elif "venturebeat.com" in url:
            return ' '.join(response.css('.article-content p::text').getall())
        elif "gizmodo.com" in url:
            return ' '.join(response.css('.js_post-content p::text').getall())
        elif "digitaltrends.com" in url:
            return ' '.join(response.css('.article-content p::text').getall())
        elif "techradar.com" in url:
            return ' '.join(response.css('.article-body p::text').getall())
        # Dla źródeł RSS, które mogą przekierowywać do różnych domen
        elif "rss.slashdot.org" in url or "feeds.feedburner.com" in url:
            return ' '.join(response.xpath('//p[not(@class)]//text()').getall())
        # Ogólna metoda dla stron, które nie mają specyficznego selektora
        else:
            content = ' '.join(response.xpath('//article//p[not(@class) or @class=""]//text()').getall())
            if not content:
                content = ' '.join(response.xpath('//div[@class="content"]//p//text()').getall())
            if not content:
                content = ' '.join(response.xpath('//p//text()').getall())
            return content.strip()

def run_spider():
    # Uruchomienie spider'a
    process = CrawlerProcess(settings={
        'LOG_LEVEL': 'INFO',
        'LOG_FILE': 'spider.log'
    })
    process.crawl(MiningSpider)
    process.start()

if __name__ == "__main__":
    run_spider()