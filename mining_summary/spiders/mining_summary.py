import scrapy
from scrapy.crawler import CrawlerProcess
import os
import html
import re
import nltk
from model import client  # Import klienta Azure OpenAI z model.py
from model import generate_openai_completion

nltk.download('punkt')

class MiningSpider(scrapy.Spider):
    name = "mining_summary"

    def start_requests(self):
        with open('links.txt', 'r') as file:
            start_urls = [url.strip() for url in file.readlines() if url.strip()]

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

        # Save original content to a file
        raw_filename = f"{response.url.split('/')[-2]}_raw.txt"
        with open(raw_filename, 'w', encoding='utf-8') as f:
            f.write(cleaned_content)

        # Generate summary from the cleaned content
        summary = self.generate_summary(cleaned_content)

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

if __name__ == "__main__":
    process = CrawlerProcess()
    process.crawl(MiningSpider)
    process.start()
# 
# import scrapy
# from scrapy.crawler import CrawlerProcess
# from sumy.parsers.plaintext import PlaintextParser
# from sumy.nlp.tokenizers import Tokenizer
# from sumy.summarizers.lsa import LsaSummarizer
# import nltk
# import html
# import re
# 
# nltk.download('punkt')
# 
# from scrapy.utils.project import get_project_settings  # Import do użycia ustawień projektu
# class MiningSpider(scrapy.Spider):
#     name = "mining_summary"
# 
#     def start_requests(self):
#         # Otwórz plik 'links.txt' i wczytaj URL-e
#         with open('links.txt', 'r') as file:
#             links = [url.strip() for url in file.readlines()]
#             for url in links:
#                 yield scrapy.Request(url=url, callback=self.parse)
# 
#                 
#     def parse(self, response):
#             self.logger.info(f"Przetwarzanie: {response.url}")
#             if "koreabizwire.com" in response.url:
#                 page_content = response.xpath('//div[@class="entry-content"]//p//text()').getall()
#             else:
#                 page_content = response.xpath('//p//text()').getall()
#             if not page_content:
#                 self.logger.error(f"Nie wyekstrahowano treści z: {response.url}")
#             else:
#                 self.logger.info(f"Ekstrahowana treść: {page_content[:100]}")
#             content = ' '.join(page_content)
#             cleaned_content = self.clean_text(content)
#             summary = self.generate_summary(cleaned_content)
#             filename = f"{response.url.split('/')[-2]}.txt"
#             with open(filename, 'w', encoding='utf-8') as f:
#                 f.write(summary)
# 
#     def clean_text(self, text):
#             text = html.unescape(text)  # Dekoduje encje HTML
#             text = re.sub(r'\s+', ' ', text)  # Usuwa nadmiarowe białe znaki
#             return text.strip()
# 
#     def generate_summary(self, text, sentences_count=3):
#             parser = PlaintextParser.from_string(text, Tokenizer("english"))
#             summarizer = LsaSummarizer()
#             summary = summarizer(parser.document, sentences_count)
#             return ' '.join([str(sentence) for sentence in summary])
# 
#     # Uruchomienie pająka (dla celów przykładowych, zazwyczaj używa się 'scrapy crawl' z terminala)
# if __name__ == "__main__":
#     process = CrawlerProcess()
#     process.crawl(MiningSpider)
#     process.start()