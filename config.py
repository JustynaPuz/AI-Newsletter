import os

class Config:
    NEWS_API_KEY = os.environ.get('NEWS_API_KEY') or '8a0eeddd46c043318061874a2da988ce'
