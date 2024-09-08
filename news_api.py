import requests

def fetch_tech_articles(api_key, query='technology', from_date='2024-07-15', sort_by='popularity'):
    url = (f'https://newsapi.org/v2/everything?'
           f'q={query}&'
           f'from={from_date}&'
           f'sortBy={sort_by}&'
           f'apiKey={api_key}')
    response = requests.get(url)
    return response.json().get('articles', [])

if __name__ == "__main__":
    api_key = '8a0eeddd46c043318061874a2da988ce'
    articles = fetch_tech_articles(api_key)

    for article in articles:
        print(f"Title: {article['title']}")
        print(f"Description: {article['description']}")
        print(f"URL: {article['url']}")
        print('-' * 80)
