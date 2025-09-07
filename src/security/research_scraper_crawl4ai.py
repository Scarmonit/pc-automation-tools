"""
Research scraper using Crawl4AI for LLM-ready content extraction
Demonstrates high-performance web crawling for research data collection
"""

import asyncio
import json
from datetime import datetime
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
import chromadb
import ollama

def setup_vector_db():
    """Initialize ChromaDB for storing research data"""
    client = chromadb.Client()
    try:
        collection = client.get_collection("crawl4ai_research")
    except:
        collection = client.create_collection("crawl4ai_research")
    return collection

def analyze_with_ollama(content, query, model="llama3.1:8b"):
    """Analyze scraped content using local Ollama model"""
    
    prompt = f"""
    Analyze the following web content and extract information relevant to: {query}
    
    Please provide:
    1. Key findings and insights
    2. Important data points or statistics
    3. Notable quotes or statements
    4. Relevant research topics or trends
    5. Summary of main points
    
    Content to analyze:
    {content[:4000]}...
    
    Provide a structured analysis focusing on research value and relevance.
    """
    
    try:
        response = ollama.generate(model=model, prompt=prompt)
        return response['response']
    except Exception as e:
        print(f"Ollama analysis error: {e}")
        return None

async def crawl_research_site(url, wait_time=2000):
    """
    Crawl a research website using Crawl4AI
    
    Args:
        url: Target website URL
        wait_time: Time to wait for page loading (ms)
    
    Returns:
        Crawled content and metadata
    """
    
    # Browser configuration
    browser_config = BrowserConfig(
        headless=True,
        verbose=False
    )
    
    # Crawler run configuration
    crawl_config = CrawlerRunConfig(
        wait_for=wait_time,
        word_count_threshold=50,  # Minimum word count for content blocks
        css_selector="article, .paper, .abstract, .content, main, .post",  # Research-focused selectors
        screenshot=False,  # Disable screenshots for faster processing
        verbose=False
    )
    
    async with AsyncWebCrawler(config=browser_config) as crawler:
        try:
            print(f"🕷️ Crawling: {url}")
            result = await crawler.arun(url=url, config=crawl_config)
            
            if result.success:
                return {
                    'url': url,
                    'title': result.metadata.get('title', 'No title'),
                    'markdown': result.markdown,
                    'cleaned_html': result.cleaned_html,
                    'metadata': result.metadata,
                    'links': result.links,
                    'media': result.media,
                    'crawled_at': datetime.now().isoformat()
                }
            else:
                print(f"❌ Failed to crawl {url}: {result.error_message}")
                return None
                
        except Exception as e:
            print(f"❌ Crawling error for {url}: {e}")
            return None

async def crawl_multiple_sources(urls, concurrent_limit=3):
    """Crawl multiple research sources concurrently"""
    
    semaphore = asyncio.Semaphore(concurrent_limit)
    
    async def crawl_with_limit(url):
        async with semaphore:
            return await crawl_research_site(url)
    
    tasks = [crawl_with_limit(url) for url in urls]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Filter successful results
    successful_crawls = []
    for result in results:
        if isinstance(result, dict) and result is not None:
            successful_crawls.append(result)
    
    return successful_crawls

async def research_ai_papers():
    """Crawl AI research paper sources"""
    
    research_urls = [
        "https://arxiv.org/list/cs.AI/recent",
        "https://arxiv.org/list/cs.LG/recent",
        "https://arxiv.org/list/cs.CL/recent",
        "https://papers.nips.cc/",
        "https://distill.pub/"
    ]
    
    print("📚 Crawling AI research paper sources...")
    results = await crawl_multiple_sources(research_urls)
    
    for result in results:
        if result:
            print(f"\n📄 Successfully crawled: {result['title']}")
            print(f"URL: {result['url']}")
            print(f"Content length: {len(result['markdown'])} characters")
            
            # Analyze with Ollama
            analysis = analyze_with_ollama(
                result['markdown'], 
                "AI research papers and recent developments"
            )
            
            if analysis:
                result['ollama_analysis'] = analysis
                print(f"🤖 Ollama analysis completed")
    
    return results

async def research_tech_news():
    """Crawl technology and AI news sources"""
    
    news_urls = [
        "https://venturebeat.com/ai/",
        "https://www.technologyreview.com/topic/artificial-intelligence/",
        "https://techcrunch.com/category/artificial-intelligence/",
        "https://www.theverge.com/ai-artificial-intelligence"
    ]
    
    print("📰 Crawling tech news sources...")
    results = await crawl_multiple_sources(news_urls)
    
    for result in results:
        if result:
            print(f"\n🗞️ Successfully crawled: {result['title']}")
            print(f"URL: {result['url']}")
            
            # Analyze with Ollama
            analysis = analyze_with_ollama(
                result['markdown'], 
                "AI industry news and developments"
            )
            
            if analysis:
                result['ollama_analysis'] = analysis
                print(f"🤖 Ollama analysis completed")
    
    return results

def store_crawled_data(collection, crawl_results, category):
    """Store crawled research data in vector database"""
    
    for result in crawl_results:
        if not result:
            continue
            
        try:
            # Create document ID
            doc_id = f"{category}_{result['url'].replace('/', '_').replace(':', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Prepare document content
            content = f"Title: {result['title']}\n\n"
            content += f"URL: {result['url']}\n\n"
            content += f"Content:\n{result['markdown'][:3000]}\n\n"
            
            if 'ollama_analysis' in result:
                content += f"AI Analysis:\n{result['ollama_analysis']}"
            
            # Store in ChromaDB
            collection.add(
                documents=[content],
                metadatas=[{
                    "url": result['url'],
                    "title": result['title'],
                    "category": category,
                    "crawled_at": result['crawled_at'],
                    "method": "crawl4ai",
                    "has_analysis": 'ollama_analysis' in result
                }],
                ids=[doc_id]
            )
            
            print(f"✅ Stored: {result['title'][:50]}...")
            
        except Exception as e:
            print(f"❌ Failed to store {result.get('title', 'Unknown')}: {e}")

def search_research_db(collection, query, n_results=5):
    """Search the research database"""
    
    try:
        results = collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        print(f"\n🔍 Search Results for: '{query}'")
        print("="*80)
        
        for i, (doc, metadata) in enumerate(zip(results['documents'][0], results['metadatas'][0])):
            print(f"\n📑 Result {i+1}: {metadata['title']}")
            print(f"🔗 URL: {metadata['url']}")
            print(f"📂 Category: {metadata['category']}")
            print(f"🕒 Crawled: {metadata['crawled_at']}")
            print(f"🤖 Has AI Analysis: {metadata['has_analysis']}")
            print(f"📝 Content Preview: {doc[:200]}...")
            print("-" * 60)
            
    except Exception as e:
        print(f"❌ Search failed: {e}")

async def main():
    """Main research crawling pipeline"""
    
    print("🚀 Starting Research Crawling Pipeline with Crawl4AI")
    print("="*80)
    
    # Check Ollama availability
    try:
        models = ollama.list()
        available_models = [model['name'] for model in models['models']]
        print(f"✅ Ollama models available: {available_models}")
    except Exception as e:
        print(f"⚠️ Ollama connection issue: {e}")
        print("Make sure Ollama is running: ollama serve")
    
    # Initialize vector database
    print("\n📊 Setting up ChromaDB...")
    collection = setup_vector_db()
    
    # Research data collection
    print("\n🔍 Starting research data collection...")
    
    # Crawl AI research papers
    print("\n📚 Phase 1: AI Research Papers")
    ai_papers = await research_ai_papers()
    if ai_papers:
        store_crawled_data(collection, ai_papers, "research_papers")
    
    # Crawl tech news
    print("\n📰 Phase 2: Technology News")
    tech_news = await research_tech_news()
    if tech_news:
        store_crawled_data(collection, tech_news, "tech_news")
    
    # Demonstrate research queries
    print("\n🔎 Testing research database queries...")
    await asyncio.sleep(1)  # Brief pause
    
    search_research_db(collection, "large language models transformer architecture")
    search_research_db(collection, "AI safety alignment research")
    search_research_db(collection, "machine learning breakthrough")
    
    print("\n✨ Research crawling pipeline completed!")
    print("\nCrawl4AI Features Used:")
    print("- ✅ Asynchronous high-speed crawling")
    print("- ✅ LLM-ready Markdown extraction")
    print("- ✅ Concurrent multi-site processing")
    print("- ✅ Research-focused CSS selectors")
    print("- ✅ Local Ollama integration for analysis")
    print("- ✅ Vector database storage")
    
    print("\nNext Steps:")
    print("- Scale to more research sources")
    print("- Implement content deduplication")
    print("- Add automated summarization")
    print("- Set up scheduled crawling")

if __name__ == "__main__":
    asyncio.run(main())