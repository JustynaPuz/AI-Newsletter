# from flask import Blueprint, render_template, request, redirect, url_for
# from app.forms import ScrapeForm
# from mining_summary.spiders import
# from mining_summary.model_connection import summarize_article
#
# bp = Blueprint('routes', __name__)
#
# @bp.route('/', methods=['GET', 'POST'])
# def index():
#     form = ScrapeForm()
#     if form.validate_on_submit():
#         urls = form.urls.data.split(',')
#         summaries = []
#         for url in urls:
#             article_text = scrape_articles(url)
#             summary = summarize_article(article_text)
#             summaries.append(summary)
#         return render_template('index.html', form=form, summaries=summaries)
#     return render_template('index.html', form=form)


from flask import render_template
from app import app
from news_api import fetch_tech_articles

@app.route('/')
@app.route('/index')
def index():
    api_key = app.config['NEWS_API_KEY']
    articles = fetch_tech_articles(api_key)
    return render_template('index.html', articles=articles)
