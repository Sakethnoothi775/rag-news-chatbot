import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import environment config if .env doesn't exist
if not os.path.exists('.env'):
    try:
        from env_config import *
    except ImportError:
        pass

class Config:
    # Server Configuration
    PORT = int(os.getenv('PORT', 8000))
    HOST = os.getenv('HOST', '0.0.0.0')
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    
    # Google Gemini API
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    
    # Jina AI Embeddings
    JINA_API_KEY = os.getenv('JINA_API_KEY')
    
    # Redis Configuration
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')
    REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', '')
    
    # Vector Database
    QDRANT_URL = os.getenv('QDRANT_URL', 'http://localhost:6333')
    QDRANT_API_KEY = os.getenv('QDRANT_API_KEY', '')
    
    # Session Configuration
    SESSION_TTL = int(os.getenv('SESSION_TTL', 3600))
    CACHE_TTL = int(os.getenv('CACHE_TTL', 1800))
    
    # News Sources
    NEWS_RSS_FEEDS = os.getenv('NEWS_RSS_FEEDS', 
        'https://feeds.bbci.co.uk/news/rss.xml,https://rss.cnn.com/rss/edition.rss,https://feeds.reuters.com/reuters/topNews'
    ).split(',')
    
    # RAG Configuration
    TOP_K_RESULTS = 5
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
