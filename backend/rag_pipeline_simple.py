import os
import json
import numpy as np
from typing import List, Dict, Optional, Tuple
import logging
from datetime import datetime
import asyncio
import aiohttp

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import google.generativeai as genai
from sentence_transformers import SentenceTransformer

from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAGPipeline:
    def __init__(self):
        self.config = Config()
        self.qdrant_client = None
        self.gemini_model = None
        self.embedding_model = None
        self.collection_name = "news_articles"
        self.embedding_dim = 384  # sentence-transformers dimension
        
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize all required clients"""
        try:
            # Initialize sentence transformer for embeddings
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("Sentence transformer model loaded")
            
            # Initialize Qdrant client
            self.qdrant_client = QdrantClient(
                url=self.config.QDRANT_URL,
                api_key=self.config.QDRANT_API_KEY if self.config.QDRANT_API_KEY else None
            )
            logger.info("Qdrant client initialized")
            
            # Initialize Gemini
            if self.config.GEMINI_API_KEY:
                genai.configure(api_key=self.config.GEMINI_API_KEY)
                self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
                logger.info("Gemini model initialized")
            else:
                logger.warning("Gemini API key not found")
                
        except Exception as e:
            logger.error(f"Error initializing clients: {str(e)}")
            raise
    
    def create_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Create embeddings using sentence transformers"""
        try:
            embeddings = self.embedding_model.encode(texts)
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Error creating embeddings: {str(e)}")
            # Return mock embeddings as fallback
            return [np.random.rand(self.embedding_dim).tolist() for _ in texts]
    
    def chunk_text(self, text: str, chunk_size: int = None, overlap: int = None) -> List[str]:
        """Split text into overlapping chunks"""
        if chunk_size is None:
            chunk_size = self.config.CHUNK_SIZE
        if overlap is None:
            overlap = self.config.CHUNK_OVERLAP
        
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk = ' '.join(words[i:i + chunk_size])
            if len(chunk.strip()) > 50:  # Only include substantial chunks
                chunks.append(chunk.strip())
        
        return chunks
    
    async def setup_vector_store(self):
        """Setup Qdrant collection for vector storage"""
        try:
            # Check if collection exists
            collections = self.qdrant_client.get_collections()
            collection_names = [col.name for col in collections.collections]
            
            if self.collection_name not in collection_names:
                # Create collection
                self.qdrant_client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.embedding_dim,
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"Created collection: {self.collection_name}")
            else:
                logger.info(f"Collection {self.collection_name} already exists")
                
        except Exception as e:
            logger.error(f"Error setting up vector store: {str(e)}")
            raise
    
    async def index_articles(self, articles: List[Dict]):
        """Index articles in the vector store"""
        try:
            await self.setup_vector_store()
            
            points = []
            for i, article in enumerate(articles):
                # Create chunks from article content
                chunks = self.chunk_text(article['content'])
                
                for j, chunk in enumerate(chunks):
                    # Create embedding for chunk
                    embeddings = self.create_embeddings([chunk])
                    embedding = embeddings[0]
                    
                    # Create point for Qdrant (use integer ID)
                    point_id = hash(f"{article['id']}_{j}") % (2**63 - 1)  # Convert to positive integer
                    point = PointStruct(
                        id=point_id,
                        vector=embedding,
                        payload={
                            'article_id': article['id'],
                            'title': article['title'],
                            'content': chunk,
                            'url': article['url'],
                            'source': article['source'],
                            'published_date': article['published_date'],
                            'chunk_index': j,
                            'total_chunks': len(chunks)
                        }
                    )
                    points.append(point)
            
            # Batch insert points
            batch_size = 100
            for i in range(0, len(points), batch_size):
                batch = points[i:i + batch_size]
                self.qdrant_client.upsert(
                    collection_name=self.collection_name,
                    points=batch
                )
                logger.info(f"Indexed batch {i//batch_size + 1}/{(len(points)-1)//batch_size + 1}")
            
            logger.info(f"Successfully indexed {len(points)} chunks from {len(articles)} articles")
            
        except Exception as e:
            logger.error(f"Error indexing articles: {str(e)}")
            raise
    
    async def search_similar_chunks(self, query: str, top_k: int = None) -> List[Dict]:
        """Search for similar chunks using vector similarity"""
        if top_k is None:
            top_k = self.config.TOP_K_RESULTS
        
        try:
            # Create embedding for query
            query_embeddings = self.create_embeddings([query])
            query_embedding = query_embeddings[0]
            
            # Search in Qdrant
            search_results = self.qdrant_client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=top_k,
                with_payload=True
            )
            
            # Format results and filter by minimum similarity threshold
            results = []
            min_similarity = 0.2  # Minimum similarity threshold (reduced for better retrieval)
            
            for result in search_results:
                if result.score >= min_similarity:
                    results.append({
                        'score': result.score,
                        'content': result.payload['content'],
                        'title': result.payload['title'],
                        'url': result.payload['url'],
                        'source': result.payload['source'],
                        'published_date': result.payload['published_date'],
                        'chunk_index': result.payload.get('chunk_index', 0)
                    })
            
            logger.info(f"Found {len(results)} chunks above similarity threshold {min_similarity}")
            return results
            
        except Exception as e:
            logger.error(f"Error searching similar chunks: {str(e)}")
            return []
    
    async def generate_response(self, query: str, context_chunks: List[Dict]) -> str:
        """Generate response using Gemini with retrieved context"""
        if not self.gemini_model:
            return "I'm sorry, but the AI model is not available. Please check the configuration."
        
        try:
            # Prepare context with better formatting and relevance scores
            context_sections = []
            for i, chunk in enumerate(context_chunks, 1):
                context_sections.append(f"""
Article {i}:
Title: {chunk['title']}
Source: {chunk['source']}
Published: {chunk['published_date']}
Relevance Score: {chunk['score']:.3f}
Content: {chunk['content']}
---""")
            
            context_text = "\n".join(context_sections)
            
            # Create comprehensive prompt for better orchestration
            prompt = f"""You are a news analysis assistant. Based on the following retrieved news articles, provide a comprehensive and well-structured answer to the user's question.

USER QUESTION: {query}

RETRIEVED NEWS ARTICLES:
{context_text}

INSTRUCTIONS:
1. Analyze the retrieved articles to find information relevant to the user's question
2. Synthesize information from multiple sources when available
3. Provide specific details, facts, and context from the articles
4. Structure your response clearly with key points
5. If information is limited, explain what is available and what is missing
6. Be factual and objective, citing information from the articles
7. If the articles don't contain relevant information, clearly state this

RESPONSE:"""

            # Generate response
            response = self.gemini_model.generate_content(prompt)
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return f"I apologize, but I encountered an error while generating a response: {str(e)}"
    
    async def query(self, question: str) -> Dict:
        """Main query method that combines retrieval and generation"""
        try:
            logger.info(f"Processing query: '{question}'")
            
            # Check if question is too short or not news-related
            if len(question.strip()) < 3 or question.lower().strip() in ['hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening']:
                return {
                    'answer': "Hello! I'm a news chatbot. Please ask me about current events, news topics, or anything you'd like to know about recent news articles. For example, you could ask about politics, technology, world events, or any specific news story.",
                    'sources': [],
                    'confidence': 1.0
                }
            
            # Step 1: Retrieve top-k relevant chunks
            logger.info("Step 1: Retrieving relevant chunks...")
            similar_chunks = await self.search_similar_chunks(question)
            logger.info(f"Retrieved {len(similar_chunks)} chunks")
            
            if not similar_chunks:
                logger.info("No relevant chunks found")
                return {
                    'answer': "I couldn't find any relevant information in the news articles to answer your question. Please try asking about current events, politics, world news, or other topics that might be covered in recent news articles.",
                    'sources': [],
                    'confidence': 0.0
                }
            
            # Log retrieved chunks for debugging
            for i, chunk in enumerate(similar_chunks):
                logger.info(f"Chunk {i+1}: {chunk['title']} (score: {chunk['score']:.3f})")
            
            # Step 2: Generate response using Gemini with retrieved context
            logger.info("Step 2: Generating response with Gemini...")
            answer = await self.generate_response(question, similar_chunks)
            logger.info("Response generated successfully")
            
            # Step 3: Extract unique sources
            sources = []
            seen_sources = set()
            for chunk in similar_chunks:
                source_key = (chunk['title'], chunk['url'])
                if source_key not in seen_sources:
                    sources.append({
                        'title': chunk['title'],
                        'url': chunk['url'],
                        'source': chunk['source'],
                        'published_date': chunk['published_date']
                    })
                    seen_sources.add(source_key)
            
            # Calculate confidence based on similarity scores
            confidence = sum(chunk['score'] for chunk in similar_chunks) / len(similar_chunks)
            logger.info(f"Final confidence: {confidence:.3f}")
            
            return {
                'answer': answer,
                'sources': sources,
                'confidence': confidence,
                'retrieved_chunks': len(similar_chunks)
            }
            
        except Exception as e:
            logger.error(f"Error in query processing: {str(e)}")
            return {
                'answer': f"I encountered an error while processing your question: {str(e)}",
                'sources': [],
                'confidence': 0.0
            }
    
    async def load_and_index_articles(self, articles_file: str = "data/articles.json"):
        """Load articles from file and index them"""
        try:
            if not os.path.exists(articles_file):
                logger.error(f"Articles file not found: {articles_file}")
                return False
            
            with open(articles_file, 'r', encoding='utf-8') as f:
                articles = json.load(f)
            
            logger.info(f"Loaded {len(articles)} articles from {articles_file}")
            await self.index_articles(articles)
            return True
            
        except Exception as e:
            logger.error(f"Error loading and indexing articles: {str(e)}")
            return False

# Example usage
async def main():
    """Example usage of the RAG pipeline"""
    rag = RAGPipeline()
    
    # Load and index articles
    success = await rag.load_and_index_articles()
    if not success:
        logger.error("Failed to load and index articles")
        return
    
    # Test query
    query = "What are the latest developments in artificial intelligence?"
    result = await rag.query(query)
    
    print(f"Query: {query}")
    print(f"Answer: {result['answer']}")
    print(f"Sources: {len(result['sources'])}")
    print(f"Confidence: {result['confidence']:.2f}")

if __name__ == "__main__":
    asyncio.run(main())

