import asyncio
import aiohttp
import feedparser
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime
from typing import List, Dict, Optional
import hashlib
import re
from urllib.parse import urlparse
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NewsIngestion:
    def __init__(self):
        self.articles = []
        self.rss_feeds = [
            'https://feeds.bbci.co.uk/news/rss.xml',
            'https://rss.cnn.com/rss/edition.rss',
            'https://feeds.reuters.com/reuters/topNews',
            'https://feeds.npr.org/1001/rss.xml',
            'https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml'
        ]
        
    def generate_id(self, url: str) -> str:
        """Generate unique ID for article based on URL"""
        return hashlib.md5(url.encode()).hexdigest()
    
    def extract_source(self, url: str) -> str:
        """Extract source domain from URL"""
        try:
            domain = urlparse(url).netloc
            return domain.replace('www.', '')
        except:
            return 'unknown'
    
    async def fetch_rss_feed(self, session: aiohttp.ClientSession, url: str) -> List[Dict]:
        """Fetch and parse RSS feed"""
        try:
            logger.info(f"Fetching RSS feed: {url}")
            async with session.get(url, timeout=30) as response:
                if response.status == 200:
                    content = await response.text()
                    feed = feedparser.parse(content)
                    return feed.entries[:10]  # Limit to 10 articles per feed
                else:
                    logger.warning(f"Failed to fetch {url}: Status {response.status}")
                    return []
        except Exception as e:
            logger.error(f"Error fetching RSS feed {url}: {str(e)}")
            return []
    
    async def scrape_article_content(self, session: aiohttp.ClientSession, url: str) -> str:
        """Scrape article content from URL"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            async with session.get(url, headers=headers, timeout=30) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Remove unwanted elements
                    for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'advertisement']):
                        element.decompose()
                    
                    # Try different selectors for article content
                    content_selectors = [
                        'article',
                        '.article-content',
                        '.story-body',
                        '.entry-content',
                        'main .content',
                        '.post-content',
                        '.article-body',
                        '[role="main"]'
                    ]
                    
                    content = ""
                    for selector in content_selectors:
                        element = soup.select_one(selector)
                        if element:
                            content = element.get_text(strip=True)
                            if len(content) > 200:
                                break
                    
                    # Fallback to all paragraph text
                    if len(content) < 200:
                        paragraphs = soup.find_all('p')
                        content = ' '.join([p.get_text(strip=True) for p in paragraphs])
                    
                    # Clean up content
                    content = re.sub(r'\s+', ' ', content)  # Replace multiple whitespace with single space
                    content = content.strip()
                    
                    return content[:3000]  # Limit content length
                else:
                    logger.warning(f"Failed to scrape {url}: Status {response.status}")
                    return ""
        except Exception as e:
            logger.error(f"Error scraping article {url}: {str(e)}")
            return ""
    
    async def process_article(self, session: aiohttp.ClientSession, article: Dict) -> Optional[Dict]:
        """Process individual article"""
        try:
            url = article.get('link', '')
            if not url:
                return None
            
            # Scrape content
            content = await self.scrape_article_content(session, url)
            
            if len(content) < 100:
                logger.info(f"Skipping article with insufficient content: {article.get('title', 'Untitled')}")
                return None
            
            # Extract publication date
            pub_date = None
            if hasattr(article, 'published_parsed') and article.published_parsed:
                pub_date = datetime(*article.published_parsed[:6])
            elif hasattr(article, 'updated_parsed') and article.updated_parsed:
                pub_date = datetime(*article.updated_parsed[:6])
            else:
                pub_date = datetime.now()
            
            processed_article = {
                'id': self.generate_id(url),
                'title': article.get('title', 'Untitled'),
                'content': content,
                'url': url,
                'published_date': pub_date.isoformat(),
                'source': self.extract_source(url),
                'summary': article.get('summary', '')[:500],  # Limit summary length
                'word_count': len(content.split()),
                'ingestion_date': datetime.now().isoformat()
            }
            
            logger.info(f"Processed: {processed_article['title']}")
            return processed_article
            
        except Exception as e:
            logger.error(f"Error processing article: {str(e)}")
            return None
    
    async def ingest_all_feeds(self) -> List[Dict]:
        """Ingest all RSS feeds"""
        logger.info("Starting news ingestion...")
        
        async with aiohttp.ClientSession() as session:
            tasks = []
            
            # Fetch all RSS feeds
            for feed_url in self.rss_feeds:
                task = self.fetch_rss_feed(session, feed_url)
                tasks.append(task)
            
            # Wait for all feeds to be fetched
            feed_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process articles from all feeds
            article_tasks = []
            for feed_articles in feed_results:
                if isinstance(feed_articles, list):
                    for article in feed_articles:
                        task = self.process_article(session, article)
                        article_tasks.append(task)
            
            # Process articles with rate limiting
            processed_articles = []
            for i, task in enumerate(article_tasks):
                try:
                    article = await task
                    if article:
                        processed_articles.append(article)
                    
                    # Rate limiting: wait 1 second every 5 articles
                    if (i + 1) % 5 == 0:
                        await asyncio.sleep(1)
                        
                except Exception as e:
                    logger.error(f"Error processing article task: {str(e)}")
                    continue
            
            self.articles = processed_articles
            logger.info(f"Ingestion complete! Processed {len(self.articles)} articles.")
            return self.articles
    
    def save_articles(self, output_path: str = "data/articles.json"):
        """Save articles to JSON file"""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.articles, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Articles saved to: {output_path}")
    
    def print_summary(self):
        """Print ingestion summary"""
        if not self.articles:
            logger.warning("No articles to summarize")
            return
        
        total_articles = len(self.articles)
        avg_word_count = sum(article['word_count'] for article in self.articles) / total_articles
        sources = list(set(article['source'] for article in self.articles))
        
        print("\n=== INGESTION SUMMARY ===")
        print(f"Total articles: {total_articles}")
        print(f"Average word count: {avg_word_count:.0f}")
        print(f"Sources: {', '.join(sources)}")
        print(f"Date range: {min(article['published_date'] for article in self.articles)} to {max(article['published_date'] for article in self.articles)}")
    
    async def run(self, output_path: str = "data/articles.json"):
        """Run the complete ingestion process"""
        try:
            await self.ingest_all_feeds()
            self.save_articles(output_path)
            self.print_summary()
        except Exception as e:
            logger.error(f"Ingestion failed: {str(e)}")
            raise

async def main():
    """Main function for running ingestion"""
    ingester = NewsIngestion()
    await ingester.run()

if __name__ == "__main__":
    asyncio.run(main())

