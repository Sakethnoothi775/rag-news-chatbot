const Parser = require('rss-parser');
const axios = require('axios');
const cheerio = require('cheerio');
const fs = require('fs');
const path = require('path');

class NewsIngestion {
  constructor() {
    this.parser = new Parser();
    this.articles = [];
    this.rssFeeds = [
      'https://feeds.bbci.co.uk/news/rss.xml',
      'https://rss.cnn.com/rss/edition.rss',
      'https://feeds.reuters.com/reuters/topNews',
      'https://feeds.npr.org/1001/rss.xml',
      'https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml'
    ];
  }

  async fetchRSSFeed(url) {
    try {
      console.log(`Fetching RSS feed: ${url}`);
      const feed = await this.parser.parseURL(url);
      return feed.items.slice(0, 10); // Limit to 10 articles per feed
    } catch (error) {
      console.error(`Error fetching RSS feed ${url}:`, error.message);
      return [];
    }
  }

  async scrapeArticleContent(articleUrl) {
    try {
      const response = await axios.get(articleUrl, {
        headers: {
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        },
        timeout: 10000
      });
      
      const $ = cheerio.load(response.data);
      
      // Remove script and style elements
      $('script, style, nav, header, footer, aside').remove();
      
      // Extract main content
      let content = '';
      
      // Try different selectors for article content
      const contentSelectors = [
        'article',
        '.article-content',
        '.story-body',
        '.entry-content',
        'main',
        '.content',
        'p'
      ];
      
      for (const selector of contentSelectors) {
        const element = $(selector);
        if (element.length > 0) {
          content = element.text().trim();
          if (content.length > 200) break; // Good enough content found
        }
      }
      
      // Fallback to all paragraph text
      if (content.length < 200) {
        content = $('p').text().trim();
      }
      
      return content.substring(0, 2000); // Limit content length
    } catch (error) {
      console.error(`Error scraping article ${articleUrl}:`, error.message);
      return '';
    }
  }

  async processArticle(article) {
    const content = await this.scrapeArticleContent(article.link);
    
    if (content.length < 100) {
      console.log(`Skipping article with insufficient content: ${article.title}`);
      return null;
    }

    return {
      id: this.generateId(),
      title: article.title || 'Untitled',
      content: content,
      url: article.link,
      publishedDate: article.pubDate ? new Date(article.pubDate) : new Date(),
      source: this.extractSource(article.link),
      summary: article.contentSnippet || article.content || '',
      wordCount: content.split(' ').length
    };
  }

  generateId() {
    return 'article_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
  }

  extractSource(url) {
    try {
      const domain = new URL(url).hostname;
      return domain.replace('www.', '');
    } catch {
      return 'unknown';
    }
  }

  async ingestAllFeeds() {
    console.log('Starting news ingestion...');
    
    for (const feedUrl of this.rssFeeds) {
      const articles = await this.fetchRSSFeed(feedUrl);
      
      for (const article of articles) {
        const processedArticle = await this.processArticle(article);
        if (processedArticle) {
          this.articles.push(processedArticle);
          console.log(`Processed: ${processedArticle.title}`);
        }
        
        // Add delay to be respectful to servers
        await new Promise(resolve => setTimeout(resolve, 1000));
      }
    }
    
    console.log(`\nIngestion complete! Processed ${this.articles.length} articles.`);
    return this.articles;
  }

  async saveArticles() {
    const outputPath = path.join(__dirname, '..', 'data', 'articles.json');
    
    // Create data directory if it doesn't exist
    const dataDir = path.dirname(outputPath);
    if (!fs.existsSync(dataDir)) {
      fs.mkdirSync(dataDir, { recursive: true });
    }
    
    fs.writeFileSync(outputPath, JSON.stringify(this.articles, null, 2));
    console.log(`Articles saved to: ${outputPath}`);
  }

  async run() {
    try {
      await this.ingestAllFeeds();
      await this.saveArticles();
      
      // Print summary
      console.log('\n=== INGESTION SUMMARY ===');
      console.log(`Total articles: ${this.articles.length}`);
      console.log(`Average word count: ${Math.round(this.articles.reduce((sum, a) => sum + a.wordCount, 0) / this.articles.length)}`);
      console.log(`Sources: ${[...new Set(this.articles.map(a => a.source))].join(', ')}`);
      
    } catch (error) {
      console.error('Ingestion failed:', error);
      process.exit(1);
    }
  }
}

// Run if called directly
if (require.main === module) {
  const ingester = new NewsIngestion();
  ingester.run();
}

module.exports = NewsIngestion;

