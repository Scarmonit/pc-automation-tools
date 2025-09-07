"""
Research scraper using ScrapeGraphAI with local Ollama LLM
Demonstrates AI-powered web scraping for research tasks
"""

import os
from scrapegraphai.graphs import SmartScraperGraph
import chromadb
from datetime import datetime

def setup_vector_db():
    """Initialize ChromaDB for storing research data"""
    client = chromadb.Client()
    try:
        collection = client.get_collection("research_papers")
    except:
        collection = client.create_collection("research_papers")
    return collection

def scrape_research_site(url, prompt, model="llama3.1:8b"):
    """
    Scrape research content using ScrapeGraphAI with local Ollama model
    
    Args:
        url: Target website URL
        prompt: Research-focused prompt for extraction
        model: Ollama model to use (default: llama3.1:8b)
    
    Returns:
        Extracted research data
    """
    
    # Configuration for local Ollama model
    graph_config = {
        "llm": {
            "model": f"ollama/{model}",
            "temperature": 0.1,  # Lower temperature for more focused research
            "base_url": "http://localhost:11434",
        },
        "verbose": True,
        "headless": True,  # Run browser in headless mode
    }
    
    # Create scraper instance
    smart_scraper = SmartScraperGraph(
        prompt=prompt,
        source=url,
        config=graph_config
    )
    
    try:
        result = smart_scraper.run()
        return result
    except Exception as e:
        print(f"Scraping error: {e}")
        return None

def scrape_arxiv_papers():
    """Example: Scrape ArXiv for AI research papers"""
    
    url = "https://arxiv.org/list/cs.AI/recent"
    prompt = """
    Extract information about recent AI research papers including:
    - Paper titles
    - Authors
    - Abstract summaries (first 2 sentences)
    - Paper IDs/links
    - Publication dates
    
    Focus on papers related to large language models, machine learning, and AI research.
    Format the output as structured data with clear separation between papers.
    """
    
    print("Scraping ArXiv for recent AI papers...")
    result = scrape_research_site(url, prompt)
    
    if result:
        print("\nResearch Papers Found:")
        print("="*50)
        print(result)
        return result
    else:
        print("Failed to scrape ArXiv")
        return None

def scrape_research_news():
    """Example: Scrape AI/ML news and developments"""
    
    url = "https://venturebeat.com/ai/"
    prompt = """
    Extract recent AI and machine learning news articles including:
    - Article headlines
    - Brief summaries (1-2 sentences each)
    - Publication dates
    - Key companies or researchers mentioned
    - Main topics (LLMs, computer vision, robotics, etc.)
    
    Focus on breakthrough research, new model releases, and industry developments.
    Organize by relevance to research and development.
    """
    
    print("Scraping AI news from VentureBeat...")
    result = scrape_research_site(url, prompt)
    
    if result:
        print("\nAI News Headlines:")
        print("="*50)
        print(result)
        return result
    else:
        print("Failed to scrape AI news")
        return None

def store_research_data(collection, data, source_url, topic):
    """Store scraped research data in vector database"""
    
    if not data:
        return
    
    # Create document entry
    doc_id = f"{topic}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    try:
        collection.add(
            documents=[str(data)],
            metadatas=[{
                "source": source_url,
                "topic": topic,
                "scraped_at": datetime.now().isoformat(),
                "method": "scrapegraphai"
            }],
            ids=[doc_id]
        )
        print(f"Stored research data with ID: {doc_id}")
    except Exception as e:
        print(f"Failed to store data: {e}")

def query_research_db(collection, query, n_results=3):
    """Query the research database for relevant information"""
    
    try:
        results = collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        print(f"\nSearch Results for: '{query}'")
        print("="*60)
        
        for i, (doc, metadata) in enumerate(zip(results['documents'][0], results['metadatas'][0])):
            print(f"\nResult {i+1}:")
            print(f"Source: {metadata['source']}")
            print(f"Topic: {metadata['topic']}")
            print(f"Date: {metadata['scraped_at']}")
            print(f"Content: {doc[:300]}...")
            print("-" * 40)
            
    except Exception as e:
        print(f"Query failed: {e}")

def main():
    """Main research scraping pipeline"""
    
    print("Starting Research Scraping Pipeline with ScrapeGraphAI")
    print("="*60)
    
    # Check if Ollama is running
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json()
            available_models = [model['name'] for model in models.get('models', [])]
            print(f"Ollama is running. Available models: {available_models}")
            
            # Use the first available model or default
            if available_models:
                model_to_use = "llama3.1:8b" if "llama3.1:8b" in available_models else available_models[0]
            else:
                model_to_use = "llama3.1:8b"
            print(f"Using model: {model_to_use}")
        else:
            print("Ollama server not responding properly")
            model_to_use = "llama3.1:8b"  # Fallback
    except Exception as e:
        print(f"Could not connect to Ollama: {e}")
        print("Make sure Ollama is running: ollama serve")
        model_to_use = "llama3.1:8b"  # Fallback
    
    # Initialize vector database
    print("\nSetting up ChromaDB...")
    collection = setup_vector_db()
    
    # Scrape research content
    print("\nStarting research data collection...")
    
    # Example 1: ArXiv papers (using available model)
    if available_models:
        arxiv_data = scrape_research_site(
            "https://arxiv.org/list/cs.AI/recent",
            "Extract recent AI research papers with titles, authors, and abstracts",
            model_to_use
        )
        if arxiv_data:
            store_research_data(collection, arxiv_data, "https://arxiv.org/list/cs.AI/recent", "arxiv_ai_papers")
        
        # Example 2: Simple test scraping
        print("Testing basic scraping functionality...")
        test_data = scrape_research_site(
            "https://example.com",
            "Extract the main content and structure of this webpage",
            model_to_use
        )
        if test_data:
            print("Test scraping successful!")
            store_research_data(collection, test_data, "https://example.com", "test_scraping")
    else:
        print("No models available for scraping")
    
    # Example queries
    print("\nTesting research database queries...")
    query_research_db(collection, "large language models")
    query_research_db(collection, "machine learning research")
    
    print("\nResearch scraping pipeline completed!")
    print("\nNext steps:")
    print("- Review extracted research data")
    print("- Expand to additional research sources")
    print("- Implement automated scheduling")
    print("- Add data analysis and summarization")

if __name__ == "__main__":
    main()