import asyncio
from rag_pipeline_simple import RAGPipeline
from config import Config

async def test_queries():
    config = Config()
    rag = RAGPipeline()
    
    # Test queries that should match the articles
    test_queries = [
        "What's happening in UK politics?",
        "Tell me about the Madeleine McCann case",
        "What's the latest on UK healthcare?",
        "Tell me about food prices in the UK",
        "What are the latest developments in artificial intelligence?",  # This should fail
        "latest news today"  # This should work
    ]
    
    for query in test_queries:
        print(f"\n{'='*50}")
        print(f"Query: {query}")
        print('='*50)
        
        result = await rag.query(query)
        print(f"Answer: {result['answer'][:200]}...")
        print(f"Sources: {len(result['sources'])}")
        print(f"Confidence: {result['confidence']:.3f}")

if __name__ == "__main__":
    asyncio.run(test_queries())
