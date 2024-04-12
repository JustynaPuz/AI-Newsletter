import scrapy
from scrapy.crawler import CrawlerProcess
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
import nltk
nltk.download('punkt')

from scrapy.utils.project import get_project_settings  # Import do użycia ustawień projektu

class MiningSpider(scrapy.Spider):
    name = "mining_summary"
    start_urls = [
        'https://im-mining.com/2024/02/08/cat-dss-evolving-and-growing-rapidly/',
        'https://im-mining.com/2024/02/08/caterpillar-and-thoroughtec-simulation-extend-cooperation-agreement/'
    ]

    def parse(self, response):
        page_content = response.xpath('//p//text()').getall()  # Pobranie tekstu z akapitów
        content = ' '.join(page_content)
        summary = self.generate_summary(content)
        filename = f"{response.url.split('/')[-2]}.txt"
        with open(filename, 'w') as f:
            f.write(summary)

    def generate_summary(self, text, sentences_count=3):
        parser = PlaintextParser.from_string(text, Tokenizer("english"))
        summarizer = LsaSummarizer()
        summary = summarizer(parser.document, sentences_count)
        return ' '.join([str(sentence) for sentence in summary])

# Uruchomienie pająka (dla celów przykładowych, zazwyczaj używa się 'scrapy crawl' z terminala)
if __name__ == "__main__":
    process = CrawlerProcess()
    process.crawl(MiningSpider)
    process.start()
