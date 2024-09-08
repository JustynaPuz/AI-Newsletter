import feedparser
import requests
from bs4 import BeautifulSoup
from Newsletter_database.news_api import NewsAPI

class ArticleFinder:
    def __init__(self):
        self.news_api = NewsAPI()
        self.rss_feeds = [
            'http://feeds.bbci.co.uk/news/technology/rss.xml',
            'http://rss.nytimes.com/services/xml/rss/nyt/Technology.xml',
            'https://feeds.feedburner.com/TechCrunch/',
            'https://www.wired.com/feed/rss',
            'https://www.theverge.com/rss/index.xml',
            'https://rss.slashdot.org/Slashdot/slashdotMain',
            'https://www.cnet.com/rss/news/',
            'https://feeds.arstechnica.com/arstechnica/technology-lab',
            'https://www.zdnet.com/news/rss.xml',
            'https://www.computerworld.com/index.rss',
            'https://www.engadget.com/rss.xml',
            'https://www.techmeme.com/feed.xml',
            'https://www.technologyreview.com/topnews.rss',
            'https://www.sciencedaily.com/rss/computers_math.xml',
            'https://www.nature.com/subjects/computer-science.rss'
        ]
        self.websites = [
            'https://techcrunch.com',
            'https://www.theverge.com',
            'https://www.wired.com',
            'https://www.cnet.com',
            'https://arstechnica.com',
            'https://www.zdnet.com',
            'https://www.engadget.com',
            'https://www.techmeme.com',
            'https://www.technologyreview.com',
            'https://www.computerworld.com',
            'https://www.infoworld.com',
            'https://www.venturebeat.com',
            'https://www.gizmodo.com',
            'https://www.digitaltrends.com',
            'https://www.techradar.com'
        ]

    def find_new_articles(self):
        articles = []
        articles.extend(self._parse_rss_feeds())
        articles.extend(self._scrape_websites())
        return self._filter_new_articles(articles)

    def _parse_rss_feeds(self):
        articles = []
        for feed_url in self.rss_feeds:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries:
                articles.append({
                    'title': entry.title,
                    'link': entry.link,
                    'source': feed_url
                })
        return articles

    def _scrape_websites(self):
        articles = []
        for website in self.websites:
            response = requests.get(website)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                for article in soup.find_all('article'):
                    title = article.find('h2')
                    link = article.find('a')
                    if title and link:
                        articles.append({
                            'title': title.text.strip(),
                            'link': link['href'],
                            'source': website
                        })
        return articles

    def _filter_new_articles(self, articles):
        new_articles = []
        for article in articles:
            if not self.news_api.article_exists(article['link']):
                new_articles.append(article)
        return new_articles