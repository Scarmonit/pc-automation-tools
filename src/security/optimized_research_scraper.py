"""
Performance-Optimized Research Scraper
Uses system optimization configs for maximum throughput
"""

import asyncio
import json
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import aiohttp
import aiofiles
from datetime import datetime

# Import our optimized configurations
import sys
sys.path.append('.')
from system_config import SystemOptimizer, set_environment_optimizations

# Import scraping libraries with optimizations
from scrapegraphai.graphs import SmartScraperGraph
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
import chromadb
import ollama

class OptimizedResearchScraper:
    """High-performance research scraper with system optimizations"""
    
    def __init__(self, config_dir="configs"):
        self.config_dir = Path(config_dir)
        
        # Set system optimizations
        set_environment_optimizations()
        
        # Load configurations
        self.load_configs()
        
        # Initialize system optimizer
        self.optimizer = SystemOptimizer()
        self.worker_counts = self.optimizer.get_optimal_worker_counts()
        
        # Performance tracking
        self.start_time = time.time()
        self.metrics = {
            "urls_processed": 0,
            "successful_scrapes": 0,
            "failed_scrapes": 0,
            "total_content_size": 0,
            "processing_times": []
        }
        
    def load_configs(self):
        """Load optimized configuration files"""
        try:
            with open(self.config_dir / "scrapegraph_config.json") as f:
                self.scrapegraph_config = json.load(f)
                
            with open(self.config_dir / "crawl4ai_config.json") as f:
                self.crawl4ai_config = json.load(f)
                
            with open(self.config_dir / "chromadb_config.json") as f:
                self.chromadb_config = json.load(f)
                
            print("Loaded optimized configurations successfully")
        except Exception as e:
            print(f"Warning: Could not load config files: {e}")
            print("Using default configurations")
            self._set_default_configs()
    
    def _set_default_configs(self):
        """Set default configurations if files not found"""
        self.scrapegraph_config = {
            "llm": {"model": "ollama/gemma2:27b", "base_url": "http://localhost:11434"},
            "performance": {"concurrent_requests": 16, "request_delay": 1.0}
        }
        self.crawl4ai_config = {
            "browser_config": {"headless": True},
            "performance": {"semaphore_limit": 12, "concurrent_crawls": 8}
        }
        self.chromadb_config = {
            "performance": {"batch_size": 500, "max_connections": 20}
        }
    
    def setup_chromadb(self):
        """Initialize ChromaDB with optimizations"""
        client = chromadb.Client()
        try:
            collection = client.get_collection("optimized_research")
        except:
            collection = client.create_collection("optimized_research")
        return collection
    
    async def optimized_crawl4ai_scraping(self, urls, semaphore_limit=None):
        """High-performance Crawl4AI scraping with concurrency control"""
        
        if semaphore_limit is None:
            semaphore_limit = self.crawl4ai_config["performance"]["semaphore_limit"]
            
        semaphore = asyncio.Semaphore(semaphore_limit)
        results = []
        
        browser_config = BrowserConfig(
            headless=self.crawl4ai_config["browser_config"]["headless"],
            verbose=False
        )
        
        crawler_config = CrawlerRunConfig(
            wait_for=2000,
            word_count_threshold=50,
            screenshot=False,
            verbose=False
        )
        
        async def crawl_single_url(url):
            async with semaphore:
                start_time = time.time()
                try:
                    async with AsyncWebCrawler(config=browser_config) as crawler:
                        result = await crawler.arun(url=url, config=crawler_config)
                        
                        if result.success:
                            processing_time = time.time() - start_time
                            self.metrics["processing_times"].append(processing_time)
                            self.metrics["successful_scrapes"] += 1
                            self.metrics["total_content_size"] += len(result.markdown)
                            
                            return {
                                'url': url,
                                'title': result.metadata.get('title', 'No title'),
                                'content': result.markdown[:5000],  # Limit content size
                                'processing_time': processing_time,
                                'method': 'crawl4ai_optimized'
                            }
                        else:
                            self.metrics["failed_scrapes"] += 1
                            return None
                except Exception as e:
                    self.metrics["failed_scrapes"] += 1
                    print(f"Error crawling {url}: {e}")
                    return None
                finally:
                    self.metrics["urls_processed"] += 1
        
        # Process URLs concurrently
        tasks = [crawl_single_url(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter successful results
        successful_results = [r for r in results if r and not isinstance(r, Exception)]
        return successful_results
    
    def optimized_scrapegraph_scraping(self, urls, prompt, max_workers=None):
        """High-performance ScrapeGraphAI scraping with thread pool"""
        
        if max_workers is None:
            max_workers = min(self.worker_counts["ai_processing_workers"], len(urls))
        
        def scrape_single_url(url):
            start_time = time.time()
            try:
                smart_scraper = SmartScraperGraph(
                    prompt=prompt,
                    source=url,
                    config=self.scrapegraph_config["llm"]
                )
                
                result = smart_scraper.run()
                
                if result:
                    processing_time = time.time() - start_time
                    self.metrics["processing_times"].append(processing_time)
                    self.metrics["successful_scrapes"] += 1
                    
                    content_str = str(result)
                    self.metrics["total_content_size"] += len(content_str)
                    
                    return {
                        'url': url,
                        'content': content_str[:5000],  # Limit content size
                        'processing_time': processing_time,
                        'method': 'scrapegraph_optimized'
                    }
                else:
                    self.metrics["failed_scrapes"] += 1
                    return None
                    
            except Exception as e:
                self.metrics["failed_scrapes"] += 1
                print(f"Error scraping {url} with ScrapeGraphAI: {e}")
                return None
            finally:
                self.metrics["urls_processed"] += 1
        
        # Process URLs with thread pool for CPU-bound AI processing
        results = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {executor.submit(scrape_single_url, url): url for url in urls}
            
            for future in as_completed(future_to_url):
                result = future.result()
                if result:
                    results.append(result)
        
        return results
    
    def batch_store_to_chromadb(self, collection, data_batch):
        """Optimized batch storage to ChromaDB"""
        
        if not data_batch:
            return 0
            
        batch_size = self.chromadb_config["performance"]["batch_size"]
        stored_count = 0
        
        # Process in batches
        for i in range(0, len(data_batch), batch_size):
            batch = data_batch[i:i + batch_size]
            
            try:
                documents = []
                metadatas = []
                ids = []
                
                for j, item in enumerate(batch):
                    doc_id = f"opt_{int(time.time())}_{i+j}"
                    
                    content = f"URL: {item.get('url', '')}\n"
                    content += f"Content: {item.get('content', '')}"
                    
                    documents.append(content)
                    metadatas.append({
                        'url': item.get('url', ''),
                        'method': item.get('method', 'unknown'),
                        'processing_time': item.get('processing_time', 0),
                        'scraped_at': datetime.now().isoformat()
                    })
                    ids.append(doc_id)
                
                # Batch insert
                collection.add(
                    documents=documents,
                    metadatas=metadatas,
                    ids=ids
                )
                
                stored_count += len(batch)
                
            except Exception as e:
                print(f"Error storing batch: {e}")
        
        return stored_count
    
    def get_performance_report(self):
        """Generate detailed performance report"""
        
        elapsed_time = time.time() - self.start_time
        
        report = {
            "execution_time_seconds": round(elapsed_time, 2),
            "urls_processed": self.metrics["urls_processed"],
            "successful_scrapes": self.metrics["successful_scrapes"],
            "failed_scrapes": self.metrics["failed_scrapes"],
            "success_rate_percent": round((self.metrics["successful_scrapes"] / max(1, self.metrics["urls_processed"])) * 100, 2),
            "total_content_size_mb": round(self.metrics["total_content_size"] / (1024*1024), 2),
            "urls_per_second": round(self.metrics["urls_processed"] / elapsed_time, 2),
            "successful_urls_per_second": round(self.metrics["successful_scrapes"] / elapsed_time, 2),
            "average_processing_time": round(sum(self.metrics["processing_times"]) / max(1, len(self.metrics["processing_times"])), 2) if self.metrics["processing_times"] else 0,
            "system_utilization": {
                "cpu_cores_used": self.worker_counts["ai_processing_workers"],
                "web_scraping_workers": self.worker_counts["web_scraping_workers"],
                "memory_concurrent": self.worker_counts["memory_intensive_concurrent"]
            }
        }
        
        return report
    
    async def run_performance_benchmark(self):
        """Run comprehensive performance benchmark"""
        
        print("=== Optimized Research Scraper Performance Benchmark ===")
        print()
        
        # Test URLs for benchmarking
        test_urls = [
            "https://example.com",
            "https://httpbin.org/html",
            "https://httpbin.org/json",
            "https://httpbin.org/xml",
            "https://www.wikipedia.org/",
        ]
        
        print(f"Testing with {len(test_urls)} URLs")
        print(f"System: {self.optimizer.logical_cpu_count} cores, {self.optimizer.memory_gb:.1f}GB RAM")
        print()
        
        # Initialize ChromaDB
        collection = self.setup_chromadb()
        
        # Test 1: Crawl4AI Performance
        print("1. Testing Crawl4AI Performance...")
        crawl4ai_start = time.time()
        crawl4ai_results = await self.optimized_crawl4ai_scraping(test_urls)
        crawl4ai_time = time.time() - crawl4ai_start
        
        print(f"   Crawl4AI: {len(crawl4ai_results)} successful in {crawl4ai_time:.2f}s")
        print(f"   Rate: {len(crawl4ai_results)/crawl4ai_time:.2f} URLs/sec")
        
        # Store Crawl4AI results
        if crawl4ai_results:
            stored = self.batch_store_to_chromadb(collection, crawl4ai_results)
            print(f"   Stored: {stored} documents")
        
        # Test 2: ScrapeGraphAI Performance (if models available)
        try:
            models = ollama.list()
            if models.get('models'):
                print("\n2. Testing ScrapeGraphAI Performance...")
                scrapegraph_start = time.time()
                
                scrapegraph_results = self.optimized_scrapegraph_scraping(
                    test_urls[:3],  # Limit to 3 URLs for AI processing
                    "Extract the main content and key information from this webpage"
                )
                
                scrapegraph_time = time.time() - scrapegraph_start
                
                print(f"   ScrapeGraphAI: {len(scrapegraph_results)} successful in {scrapegraph_time:.2f}s")
                print(f"   Rate: {len(scrapegraph_results)/scrapegraph_time:.2f} URLs/sec")
                
                # Store ScrapeGraphAI results
                if scrapegraph_results:
                    stored = self.batch_store_to_chromadb(collection, scrapegraph_results)
                    print(f"   Stored: {stored} documents")
            else:
                print("\n2. ScrapeGraphAI: No models available")
                
        except Exception as e:
            print(f"\n2. ScrapeGraphAI: Error - {e}")
        
        # Generate performance report
        print("\n=== Performance Report ===")
        report = self.get_performance_report()
        
        for key, value in report.items():
            if isinstance(value, dict):
                print(f"{key.replace('_', ' ').title()}:")
                for subkey, subvalue in value.items():
                    print(f"  {subkey.replace('_', ' ').title()}: {subvalue}")
            else:
                print(f"{key.replace('_', ' ').title()}: {value}")
        
        # Test database query performance
        print("\n=== Database Query Performance ===")
        query_start = time.time()
        
        try:
            results = collection.query(
                query_texts=["web content information"],
                n_results=10
            )
            query_time = time.time() - query_start
            
            print(f"Query Time: {query_time:.3f}s")
            print(f"Results Found: {len(results['documents'][0])}")
            
        except Exception as e:
            print(f"Query Error: {e}")
        
        print("\n=== Optimization Complete ===")
        print("Your system is now configured for maximum performance!")
        
        return report

async def main():
    """Run the optimized performance benchmark"""
    
    scraper = OptimizedResearchScraper()
    report = await scraper.run_performance_benchmark()
    
    # Save performance report
    report_file = f"performance_report_{int(time.time())}.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\nPerformance report saved to: {report_file}")

if __name__ == "__main__":
    asyncio.run(main())