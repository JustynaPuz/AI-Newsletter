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
