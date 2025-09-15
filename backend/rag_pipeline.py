import os
import json
import numpy as np
from typing import List, Dict, Optional, Tuple
import logging
from datetime import datetime
import asyncio
import aiohttp

from jina import Client
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from qdrant_client.http import models
import google.generativeai as genai

from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAGPipeline:
    def __init__(self):
        self.config = Config()
        self.jina_client = None
        self.qdrant_client = None
        self.gemini_model = None
        self.collection_name = "news_articles"
        self.embedding_dim = 768  # Jina embedding dimension
        
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize all required clients"""
        try:
            # Initialize Jina client
            if self.config.JINA_API_KEY:
                self.jina_client = Client(api_key=self.config.JINA_API_KEY)
                logger.info("Jina client initialized")
            else:
                logger.warning("Jina API key not found, using mock embeddings")
            
            # Initialize Qdrant client
            self.qdrant_client = QdrantClient(
                url=self.config.QDRANT_URL,
                api_key=self.config.QDRANT_API_KEY if self.config.QDRANT_API_KEY else None
            )
            logger.info("Qdrant client initialized")
            
            # Initialize Gemini
            if self.config.GEMINI_API_KEY:
                genai.configure(api_key=self.config.GEMINI_API_KEY)
                self.gemini_model = genai.GenerativeModel('gemini-pro')
                logger.info("Gemini model initialized")
            else:
                logger.warning("Gemini API key not found")
                
        except Exception as e:
            logger.error(f"Error initializing clients: {str(e)}")
            raise
    
    async def create_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Create embeddings using Jina AI"""
        if not self.jina_client:
            # Return mock embeddings for testing
            return [np.random.rand(self.embedding_dim).tolist() for _ in texts]
        
        try:
            # Use Jina's embedding API
            embeddings = []
            for text in texts:
                response = await self.jina_client.post(
                    '/embeddings',
                    inputs=[text],
                    parameters={'model': 'jina-embeddings-v2-base-en'}
                )
                if response.outputs:
                    embeddings.append(response.outputs[0].embedding)
                else:
                    # Fallback to mock embedding
                    embeddings.append(np.random.rand(self.embedding_dim).tolist())
            
            return embeddings
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
                    embeddings = await self.create_embeddings([chunk])
                    embedding = embeddings[0]
                    
                    # Create point for Qdrant
                    point_id = f"{article['id']}_{j}"
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
            query_embeddings = await self.create_embeddings([query])
            query_embedding = query_embeddings[0]
            
            # Search in Qdrant
            search_results = self.qdrant_client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=top_k,
                with_payload=True
            )
            
            # Format results
            results = []
            for result in search_results:
                results.append({
                    'score': result.score,
                    'content': result.payload['content'],
                    'title': result.payload['title'],
                    'url': result.payload['url'],
                    'source': result.payload['source'],
                    'published_date': result.payload['published_date'],
                    'chunk_index': result.payload['chunk_index']
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching similar chunks: {str(e)}")
            return []
    
    async def generate_response(self, query: str, context_chunks: List[Dict]) -> str:
        """Generate response using Gemini with retrieved context"""
        if not self.gemini_model:
            return "I'm sorry, but the AI model is not available. Please check the configuration."
        
        try:
            # Prepare context
            context_text = "\n\n".join([
                f"Source: {chunk['source']}\nTitle: {chunk['title']}\nContent: {chunk['content']}"
                for chunk in context_chunks
            ])
            
            # Create prompt
            prompt = f"""You are a helpful news assistant. Based on the following news articles, please answer the user's question. If the information is not available in the provided context, please say so.

Context from news articles:
{context_text}

User Question: {query}

Please provide a comprehensive and accurate answer based on the news articles provided. Include relevant details and cite the sources when possible."""

            # Generate response
            response = self.gemini_model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return f"I apologize, but I encountered an error while generating a response: {str(e)}"
    
    async def query(self, question: str) -> Dict:
        """Main query method that combines retrieval and generation"""
        try:
            # Search for relevant chunks
            similar_chunks = await self.search_similar_chunks(question)
            
            if not similar_chunks:
                return {
                    'answer': "I couldn't find any relevant information in the news articles to answer your question.",
                    'sources': [],
                    'confidence': 0.0
                }
            
            # Generate response
            answer = await self.generate_response(question, similar_chunks)
            
            # Extract unique sources
            sources = list(set([
                {
                    'title': chunk['title'],
                    'url': chunk['url'],
                    'source': chunk['source'],
                    'published_date': chunk['published_date']
                }
                for chunk in similar_chunks
            ]))
            
            # Calculate confidence based on similarity scores
            confidence = sum(chunk['score'] for chunk in similar_chunks) / len(similar_chunks)
            
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

