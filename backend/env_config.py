import os

# Environment configuration for development
os.environ['PORT'] = '8000'
os.environ['HOST'] = '0.0.0.0'
os.environ['DEBUG'] = 'True'
os.environ['GEMINI_API_KEY'] = 'AIzaSyBUwwMOSa75EtVHdBr2kOuzdRLLH45p0A4'
os.environ['JINA_API_KEY'] = 'jina_b322a5add1274233ab7d3c5da3e45ea1AiNQ0Rd-snLJUe7sER_CQfBkOc07'
os.environ['REDIS_URL'] = 'redis://localhost:6379'
os.environ['REDIS_PASSWORD'] = ''
os.environ['QDRANT_URL'] = 'http://localhost:6333'
os.environ['QDRANT_API_KEY'] = ''
os.environ['SESSION_TTL'] = '3600'
os.environ['CACHE_TTL'] = '1800'
os.environ['NEWS_RSS_FEEDS'] = 'https://feeds.bbci.co.uk/news/rss.xml,https://rss.cnn.com/rss/edition.rss,https://feeds.reuters.com/reuters/topNews'

