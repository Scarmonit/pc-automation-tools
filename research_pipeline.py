"""
Comprehensive Research Pipeline
Combines multiple scraping approaches for robust research data collection
"""

import asyncio
import json
from datetime import datetime, timedelta
import ollama
import chromadb
from pathlib import Path

# Import our custom scrapers
from research_scraper_scrapegraph import scrape_research_site, setup_vector_db as setup_scrapegraph_db
from research_scraper_crawl4ai import crawl_research_site, setup_vector_db as setup_crawl4ai_db

class ResearchPipeline:
    """Unified research data collection and analysis pipeline"""
    
    def __init__(self, data_dir="research_data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # Initialize databases
        self.scrapegraph_db = setup_scrapegraph_db()
        self.crawl4ai_db = setup_crawl4ai_db()
        
        # Research targets
        self.research_sources = {
            "ai_papers": [
                "https://arxiv.org/list/cs.AI/recent",
                "https://arxiv.org/list/cs.LG/recent", 
                "https://arxiv.org/list/cs.CL/recent"
            ],
            "tech_news": [
                "https://venturebeat.com/ai/",
                "https://www.technologyreview.com/topic/artificial-intelligence/",
                "https://techcrunch.com/category/artificial-intelligence/"
            ],
            "research_blogs": [
                "https://distill.pub/",
                "https://openai.com/research/",
                "https://research.google/research-areas/machine-intelligence/"
            ]
        }
        
    def check_ollama_status(self):
        """Check if Ollama is running and get available models"""
        try:
            models = ollama.list()
            available = [m['name'] for m in models['models']]
            print(f"✅ Ollama running. Models: {available}")
            return available
        except Exception as e:
            print(f"⚠️ Ollama not available: {e}")
            return []
    
    async def collect_with_crawl4ai(self, urls, category):
        """Collect data using Crawl4AI"""
        print(f"\n🕷️ Crawl4AI Collection: {category}")
        results = []
        
        for url in urls:
            try:
                data = await crawl_research_site(url)
                if data:
                    results.append(data)
                    print(f"✅ Crawled: {data['title'][:50]}...")
                await asyncio.sleep(2)  # Rate limiting
            except Exception as e:
                print(f"❌ Crawl4AI error for {url}: {e}")
                
        return results
    
    def collect_with_scrapegraph(self, urls, category):
        """Collect data using ScrapeGraphAI"""
        print(f"\n🤖 ScrapeGraphAI Collection: {category}")
        results = []
        
        research_prompts = {
            "ai_papers": """Extract research paper information:
                - Paper titles and authors
                - Abstract summaries (2-3 sentences)
                - Key research topics and methodologies
                - Publication dates and venues
                Focus on machine learning, AI, and NLP papers.""",
                
            "tech_news": """Extract technology news information:
                - Article headlines and summaries
                - Key companies and products mentioned
                - Industry trends and developments
                - Publication dates and sources
                Focus on AI, ML, and emerging tech.""",
                
            "research_blogs": """Extract research blog content:
                - Post titles and main topics
                - Key insights and findings
                - Technical concepts explained
                - Author information and publication dates
                Focus on research insights and technical depth."""
        }
        
        prompt = research_prompts.get(category, "Extract relevant research information from this page.")
        
        for url in urls:
            try:
                data = scrape_research_site(url, prompt)
                if data:
                    results.append({
                        'url': url,
                        'content': data,
                        'scraped_at': datetime.now().isoformat(),
                        'method': 'scrapegraphai'
                    })
                    print(f"✅ Scraped: {url}")
            except Exception as e:
                print(f"❌ ScrapeGraphAI error for {url}: {e}")
                
        return results
    
    def analyze_content(self, content, research_focus, model="llama3.1:8b"):
        """Analyze content using local Ollama model"""
        
        analysis_prompt = f"""
        As a research analyst, analyze this content focusing on: {research_focus}
        
        Provide:
        1. Key Research Insights (3-5 points)
        2. Important Findings or Breakthroughs
        3. Relevant Technologies or Methods
        4. Industry Impact Assessment
        5. Future Research Directions
        
        Content to analyze:
        {str(content)[:4000]}
        
        Be concise but comprehensive in your analysis.
        """
        
        try:
            response = ollama.generate(model=model, prompt=analysis_prompt)
            return response['response']
        except Exception as e:
            print(f"❌ Analysis error: {e}")
            return None
    
    def store_research_data(self, data, category, method):
        """Store research data in appropriate database"""
        
        if method == "crawl4ai":
            collection = self.crawl4ai_db
        else:
            collection = self.scrapegraph_db
        
        stored_count = 0
        for item in data:
            try:
                doc_id = f"{category}_{method}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{stored_count}"
                
                # Prepare content
                if method == "crawl4ai":
                    content = f"Title: {item.get('title', 'No title')}\n"
                    content += f"URL: {item.get('url', '')}\n"
                    content += f"Content: {item.get('markdown', '')[:3000]}"
                else:
                    content = f"URL: {item.get('url', '')}\n"
                    content += f"Content: {str(item.get('content', ''))[:3000]}"
                
                # Add AI analysis if available
                if 'analysis' in item:
                    content += f"\n\nAI Analysis:\n{item['analysis']}"
                
                collection.add(
                    documents=[content],
                    metadatas=[{
                        "category": category,
                        "method": method,
                        "url": item.get('url', ''),
                        "collected_at": datetime.now().isoformat(),
                        "has_analysis": 'analysis' in item
                    }],
                    ids=[doc_id]
                )
                stored_count += 1
                
            except Exception as e:
                print(f"❌ Storage error: {e}")
        
        print(f"📦 Stored {stored_count} items in {method} database")
        return stored_count
    
    def search_research(self, query, max_results=5):
        """Search across all research databases"""
        
        print(f"\n🔍 Searching for: '{query}'")
        print("="*60)
        
        # Search both databases
        databases = [
            ("Crawl4AI", self.crawl4ai_db),
            ("ScrapeGraphAI", self.scrapegraph_db)
        ]
        
        all_results = []
        
        for db_name, collection in databases:
            try:
                results = collection.query(
                    query_texts=[query],
                    n_results=max_results//2 + 1
                )
                
                print(f"\n📊 {db_name} Results:")
                print("-" * 30)
                
                for i, (doc, metadata) in enumerate(zip(results['documents'][0], results['metadatas'][0])):
                    print(f"{i+1}. [{metadata['category']}] {metadata.get('url', 'No URL')}")
                    print(f"   Method: {metadata['method']} | Date: {metadata['collected_at']}")
                    print(f"   Preview: {doc[:150]}...")
                    print()
                    
                    all_results.append({
                        'database': db_name,
                        'content': doc,
                        'metadata': metadata
                    })
                    
            except Exception as e:
                print(f"❌ Search error in {db_name}: {e}")
        
        return all_results
    
    def generate_research_summary(self, query, search_results):
        """Generate comprehensive research summary using Ollama"""
        
        # Combine top results
        combined_content = ""
        for result in search_results[:5]:  # Top 5 results
            combined_content += f"\n\nSource: {result['metadata'].get('url', 'Unknown')}\n"
            combined_content += f"Content: {result['content'][:1000]}\n"
            combined_content += "-" * 50
        
        summary_prompt = f"""
        Based on the research data collected, provide a comprehensive summary about: {query}
        
        Please organize your response with:
        
        1. EXECUTIVE SUMMARY (2-3 sentences)
        2. KEY FINDINGS (bullet points)
        3. CURRENT STATE OF RESEARCH
        4. EMERGING TRENDS
        5. FUTURE OUTLOOK
        6. RECOMMENDED FURTHER READING
        
        Research data:
        {combined_content[:5000]}
        
        Focus on providing actionable insights and highlighting the most significant developments.
        """
        
        try:
            response = ollama.generate(model="llama3.1:8b", prompt=summary_prompt)
            return response['response']
        except Exception as e:
            print(f"❌ Summary generation error: {e}")
            return None
    
    def save_report(self, query, summary, results):
        """Save research report to file"""
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = self.data_dir / f"research_report_{query.replace(' ', '_')}_{timestamp}.md"
        
        report = f"""# Research Report: {query}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary
{summary}

## Data Sources
Total sources analyzed: {len(results)}

"""
        
        for i, result in enumerate(results[:10]):  # Top 10
            report += f"### Source {i+1}: {result['metadata'].get('category', 'Unknown')}\n"
            report += f"**URL**: {result['metadata'].get('url', 'No URL')}\n"
            report += f"**Method**: {result['metadata']['method']}\n"
            report += f"**Content Preview**: {result['content'][:300]}...\n\n"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"📄 Report saved: {filename}")
        return filename
    
    async def run_full_pipeline(self, research_query="artificial intelligence research"):
        """Execute the complete research pipeline"""
        
        print("🚀 Starting Comprehensive Research Pipeline")
        print("="*80)
        
        # Check system status
        available_models = self.check_ollama_status()
        if not available_models:
            print("❌ Ollama not available. Some features will be limited.")
            return
        
        total_collected = 0
        
        # Data collection phase
        for category, urls in self.research_sources.items():
            print(f"\n📊 Processing category: {category}")
            print(f"🎯 URLs to process: {len(urls)}")
            
            # Collect with both methods
            crawl4ai_data = await self.collect_with_crawl4ai(urls[:2], category)  # Limit for demo
            scrapegraph_data = self.collect_with_scrapegraph(urls[:2], category)
            
            # Add AI analysis
            for item in crawl4ai_data:
                analysis = self.analyze_content(item.get('markdown', ''), research_query)
                if analysis:
                    item['analysis'] = analysis
            
            for item in scrapegraph_data:
                analysis = self.analyze_content(item.get('content', ''), research_query)
                if analysis:
                    item['analysis'] = analysis
            
            # Store data
            if crawl4ai_data:
                total_collected += self.store_research_data(crawl4ai_data, category, "crawl4ai")
            if scrapegraph_data:
                total_collected += self.store_research_data(scrapegraph_data, category, "scrapegraphai")
        
        print(f"\n📈 Data Collection Complete: {total_collected} items stored")
        
        # Research and analysis phase
        print(f"\n🔍 Analyzing research query: '{research_query}'")
        search_results = self.search_research(research_query)
        
        if search_results:
            print(f"\n🤖 Generating comprehensive summary...")
            summary = self.generate_research_summary(research_query, search_results)
            
            if summary:
                print(f"\n📋 Research Summary:")
                print("="*60)
                print(summary)
                
                # Save report
                report_file = self.save_report(research_query, summary, search_results)
                
                print(f"\n✅ Pipeline completed successfully!")
                print(f"📄 Report available: {report_file}")
            else:
                print("❌ Failed to generate summary")
        else:
            print("❌ No search results found")
        
        return search_results, summary if 'summary' in locals() else None

async def main():
    """Run the research pipeline"""
    
    pipeline = ResearchPipeline()
    
    # Example research queries
    research_topics = [
        "large language models transformer architecture",
        "AI safety and alignment research", 
        "machine learning breakthrough 2024"
    ]
    
    # Run pipeline for first topic
    topic = research_topics[0]
    print(f"🎯 Research Focus: {topic}")
    
    results, summary = await pipeline.run_full_pipeline(topic)
    
    print("\n🎉 Research Pipeline Demo Complete!")
    print("\nFeatures Demonstrated:")
    print("✅ Multi-source data collection")
    print("✅ Dual scraping methods (Crawl4AI + ScrapeGraphAI)")
    print("✅ Local Ollama LLM analysis")
    print("✅ Vector database storage and search")
    print("✅ Automated report generation")
    print("✅ Comprehensive research insights")

if __name__ == "__main__":
    asyncio.run(main())