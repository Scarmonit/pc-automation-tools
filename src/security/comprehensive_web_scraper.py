#!/usr/bin/env python3
"""
Comprehensive Web Scraper - Ultimate Data Extraction Tool
Implements all 2024 best practices for extracting maximum information from any website
"""

import asyncio
import aiohttp
import requests
import time
import random
import json
import re
from pathlib import Path
from urllib.parse import urljoin, urlparse, parse_qs
from dataclasses import dataclass
from typing import List, Dict, Optional, Set
import hashlib

# Advanced scraping libraries
try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    import undetected_chromedriver as uc
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

try:
    from bs4 import BeautifulSoup
    import lxml
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False

try:
    from fake_useragent import UserAgent
    UA_AVAILABLE = True
except ImportError:
    UA_AVAILABLE = False

# AI-powered extraction
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

@dataclass
class ScrapingConfig:
    """Configuration for web scraping session"""
    target_url: str
    max_depth: int = 3
    concurrent_requests: int = 10
    request_delay: float = 1.0
    use_proxies: bool = False
    rotate_user_agents: bool = True
    extract_images: bool = True
    extract_links: bool = True
    extract_text: bool = True
    extract_metadata: bool = True
    extract_structured_data: bool = True
    save_raw_html: bool = False
    output_format: str = "json"  # json, csv, xml
    output_file: Optional[str] = None

@dataclass
class ExtractedData:
    """Container for extracted website data"""
    url: str
    title: str
    text_content: str
    links: List[str]
    images: List[str]
    metadata: Dict
    structured_data: Dict
    forms: List[Dict]
    scripts: List[str]
    stylesheets: List[str]
    headers: Dict
    cookies: Dict
    response_time: float
    status_code: int
    content_type: str
    page_size: int
    hash: str

class ProxyRotator:
    """Manages proxy rotation for anti-detection"""
    def __init__(self):
        self.proxies = []
        self.current_proxy = 0
        self.load_free_proxies()
    
    def load_free_proxies(self):
        """Load free proxy list"""
        # This would typically load from a proxy service
        self.proxies = [
            # Add your proxy list here
            # Example: {"http": "http://proxy1:port", "https": "https://proxy1:port"}
        ]
    
    def get_proxy(self):
        """Get next proxy in rotation"""
        if not self.proxies:
            return None
        
        proxy = self.proxies[self.current_proxy]
        self.current_proxy = (self.current_proxy + 1) % len(self.proxies)
        return proxy

class UserAgentRotator:
    """Manages user agent rotation"""
    def __init__(self):
        if UA_AVAILABLE:
            self.ua = UserAgent()
        else:
            self.user_agents = [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
            ]
            self.current = 0
    
    def get_user_agent(self):
        """Get random user agent"""
        if UA_AVAILABLE:
            return self.ua.random
        else:
            ua = self.user_agents[self.current]
            self.current = (self.current + 1) % len(self.user_agents)
            return ua

class ComprehensiveWebScraper:
    """Advanced web scraper with all 2024 best practices"""
    
    def __init__(self, config: ScrapingConfig):
        self.config = config
        self.proxy_rotator = ProxyRotator()
        self.ua_rotator = UserAgentRotator()
        self.session = None
        self.scraped_urls = set()
        self.results = []
        
        # Request session setup
        self.setup_session()
    
    def setup_session(self):
        """Setup requests session with optimal configuration"""
        self.session = requests.Session()
        
        # Headers for stealth
        self.session.headers.update({
            'User-Agent': self.ua_rotator.get_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
    
    def extract_with_requests(self, url: str) -> Optional[ExtractedData]:
        """Extract data using requests + BeautifulSoup"""
        try:
            start_time = time.time()
            
            # Rotate user agent
            if self.config.rotate_user_agents:
                self.session.headers['User-Agent'] = self.ua_rotator.get_user_agent()
            
            # Get proxy if enabled
            proxy = self.proxy_rotator.get_proxy() if self.config.use_proxies else None
            
            # Make request
            response = self.session.get(
                url, 
                proxies=proxy,
                timeout=30,
                allow_redirects=True
            )
            
            response_time = time.time() - start_time
            
            if not BS4_AVAILABLE:
                print("⚠️  BeautifulSoup not available, install with: pip install beautifulsoup4 lxml")
                return None
            
            soup = BeautifulSoup(response.content, 'lxml')
            
            # Extract comprehensive data
            data = ExtractedData(
                url=url,
                title=self.extract_title(soup),
                text_content=self.extract_text(soup),
                links=self.extract_links(soup, url),
                images=self.extract_images(soup, url),
                metadata=self.extract_metadata(soup),
                structured_data=self.extract_structured_data(soup),
                forms=self.extract_forms(soup),
                scripts=self.extract_scripts(soup),
                stylesheets=self.extract_stylesheets(soup, url),
                headers=dict(response.headers),
                cookies=dict(response.cookies),
                response_time=response_time,
                status_code=response.status_code,
                content_type=response.headers.get('content-type', ''),
                page_size=len(response.content),
                hash=hashlib.md5(response.content).hexdigest()
            )
            
            return data
            
        except Exception as e:
            print(f"❌ Error scraping {url}: {e}")
            return None
    
    async def extract_with_playwright(self, url: str) -> Optional[ExtractedData]:
        """Extract data using Playwright for dynamic content"""
        if not PLAYWRIGHT_AVAILABLE:
            print("⚠️  Playwright not available, install with: pip install playwright")
            return None
        
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    user_agent=self.ua_rotator.get_user_agent()
                )
                
                page = await context.new_page()
                
                start_time = time.time()
                response = await page.goto(url, wait_until='networkidle')
                
                # Wait for dynamic content
                await page.wait_for_timeout(3000)
                
                response_time = time.time() - start_time
                
                # Extract data
                content = await page.content()
                soup = BeautifulSoup(content, 'lxml')
                
                data = ExtractedData(
                    url=url,
                    title=await page.title(),
                    text_content=self.extract_text(soup),
                    links=self.extract_links(soup, url),
                    images=self.extract_images(soup, url),
                    metadata=self.extract_metadata(soup),
                    structured_data=self.extract_structured_data(soup),
                    forms=self.extract_forms(soup),
                    scripts=self.extract_scripts(soup),
                    stylesheets=self.extract_stylesheets(soup, url),
                    headers={} if not response else dict(response.headers),
                    cookies=await context.cookies(),
                    response_time=response_time,
                    status_code=response.status if response else 0,
                    content_type='text/html',
                    page_size=len(content),
                    hash=hashlib.md5(content.encode()).hexdigest()
                )
                
                await browser.close()
                return data
                
        except Exception as e:
            print(f"❌ Error with Playwright scraping {url}: {e}")
            return None
    
    def extract_with_selenium(self, url: str) -> Optional[ExtractedData]:
        """Extract data using Selenium for maximum compatibility"""
        if not SELENIUM_AVAILABLE:
            print("⚠️  Selenium not available, install with: pip install selenium undetected-chromedriver")
            return None
        
        try:
            options = uc.ChromeOptions()
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument(f"--user-agent={self.ua_rotator.get_user_agent()}")
            
            driver = uc.Chrome(options=options)
            
            start_time = time.time()
            driver.get(url)
            
            # Wait for page load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            response_time = time.time() - start_time
            
            # Extract data
            content = driver.page_source
            soup = BeautifulSoup(content, 'lxml')
            
            data = ExtractedData(
                url=url,
                title=driver.title,
                text_content=self.extract_text(soup),
                links=self.extract_links(soup, url),
                images=self.extract_images(soup, url),
                metadata=self.extract_metadata(soup),
                structured_data=self.extract_structured_data(soup),
                forms=self.extract_forms(soup),
                scripts=self.extract_scripts(soup),
                stylesheets=self.extract_stylesheets(soup, url),
                headers={},
                cookies={cookie['name']: cookie['value'] for cookie in driver.get_cookies()},
                response_time=response_time,
                status_code=200,  # Selenium doesn't provide status codes easily
                content_type='text/html',
                page_size=len(content),
                hash=hashlib.md5(content.encode()).hexdigest()
            )
            
            driver.quit()
            return data
            
        except Exception as e:
            print(f"❌ Error with Selenium scraping {url}: {e}")
            return None
    
    def extract_title(self, soup) -> str:
        """Extract page title"""
        title_tag = soup.find('title')
        if title_tag:
            return title_tag.get_text().strip()
        
        # Try h1 as fallback
        h1_tag = soup.find('h1')
        if h1_tag:
            return h1_tag.get_text().strip()
        
        return ""
    
    def extract_text(self, soup) -> str:
        """Extract all readable text content"""
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text
        text = soup.get_text()
        
        # Clean up text
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text
    
    def extract_links(self, soup, base_url: str) -> List[str]:
        """Extract all links from the page"""
        links = []
        
        for link in soup.find_all('a', href=True):
            url = urljoin(base_url, link['href'])
            if url not in links:
                links.append(url)
        
        return links
    
    def extract_images(self, soup, base_url: str) -> List[str]:
        """Extract all image URLs"""
        images = []
        
        for img in soup.find_all('img', src=True):
            url = urljoin(base_url, img['src'])
            if url not in images:
                images.append(url)
        
        return images
    
    def extract_metadata(self, soup) -> Dict:
        """Extract metadata from head section"""
        metadata = {}
        
        # Meta tags
        for meta in soup.find_all('meta'):
            if meta.get('name'):
                metadata[meta.get('name')] = meta.get('content', '')
            elif meta.get('property'):
                metadata[meta.get('property')] = meta.get('content', '')
        
        # Title
        title = soup.find('title')
        if title:
            metadata['title'] = title.get_text().strip()
        
        return metadata
    
    def extract_structured_data(self, soup) -> Dict:
        """Extract structured data (JSON-LD, microdata, etc.)"""
        structured = {}
        
        # JSON-LD
        json_scripts = soup.find_all('script', type='application/ld+json')
        json_data = []
        for script in json_scripts:
            try:
                data = json.loads(script.string)
                json_data.append(data)
            except:
                pass
        
        if json_data:
            structured['json-ld'] = json_data
        
        # Microdata
        microdata = []
        for item in soup.find_all(attrs={"itemscope": True}):
            item_data = {}
            if item.get('itemtype'):
                item_data['type'] = item.get('itemtype')
            
            properties = {}
            for prop in item.find_all(attrs={"itemprop": True}):
                prop_name = prop.get('itemprop')
                prop_value = prop.get('content') or prop.get_text().strip()
                properties[prop_name] = prop_value
            
            if properties:
                item_data['properties'] = properties
                microdata.append(item_data)
        
        if microdata:
            structured['microdata'] = microdata
        
        return structured
    
    def extract_forms(self, soup) -> List[Dict]:
        """Extract all forms and their fields"""
        forms = []
        
        for form in soup.find_all('form'):
            form_data = {
                'action': form.get('action', ''),
                'method': form.get('method', 'GET').upper(),
                'fields': []
            }
            
            for field in form.find_all(['input', 'select', 'textarea']):
                field_data = {
                    'name': field.get('name', ''),
                    'type': field.get('type', ''),
                    'required': field.has_attr('required')
                }
                form_data['fields'].append(field_data)
            
            forms.append(form_data)
        
        return forms
    
    def extract_scripts(self, soup) -> List[str]:
        """Extract all script URLs"""
        scripts = []
        
        for script in soup.find_all('script', src=True):
            scripts.append(script['src'])
        
        return scripts
    
    def extract_stylesheets(self, soup, base_url: str) -> List[str]:
        """Extract all stylesheet URLs"""
        stylesheets = []
        
        for link in soup.find_all('link', rel='stylesheet', href=True):
            url = urljoin(base_url, link['href'])
            stylesheets.append(url)
        
        return stylesheets
    
    async def scrape_comprehensive(self, url: str) -> Optional[ExtractedData]:
        """Comprehensive scraping using best available method"""
        print(f"🔍 Scraping: {url}")
        
        # Try methods in order of effectiveness
        methods = [
            ("Playwright", self.extract_with_playwright),
            ("Selenium", self.extract_with_selenium),
            ("Requests", self.extract_with_requests)
        ]
        
        for method_name, method in methods:
            try:
                print(f"   Using {method_name}...")
                
                if asyncio.iscoroutinefunction(method):
                    data = await method(url)
                else:
                    data = method(url)
                
                if data:
                    print(f"✅ Success with {method_name}")
                    return data
                else:
                    print(f"❌ Failed with {method_name}")
                    
            except Exception as e:
                print(f"❌ Error with {method_name}: {e}")
                continue
        
        return None
    
    def save_results(self):
        """Save extracted data to file"""
        if not self.results:
            print("⚠️  No results to save")
            return
        
        output_file = self.config.output_file or f"scraped_data_{int(time.time())}.json"
        
        # Convert results to serializable format
        serializable_results = []
        for result in self.results:
            data_dict = {
                'url': result.url,
                'title': result.title,
                'text_content': result.text_content[:1000] + "..." if len(result.text_content) > 1000 else result.text_content,
                'links_count': len(result.links),
                'images_count': len(result.images),
                'metadata': result.metadata,
                'structured_data': result.structured_data,
                'forms_count': len(result.forms),
                'response_time': result.response_time,
                'status_code': result.status_code,
                'page_size': result.page_size,
                'hash': result.hash
            }
            serializable_results.append(data_dict)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(serializable_results, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Results saved to: {output_file}")
    
    async def run_comprehensive_extraction(self):
        """Run comprehensive data extraction"""
        print("🚀 STARTING COMPREHENSIVE WEB SCRAPING")
        print("=" * 60)
        print(f"Target URL: {self.config.target_url}")
        print(f"Max Depth: {self.config.max_depth}")
        print(f"Concurrent Requests: {self.config.concurrent_requests}")
        print("=" * 60)
        
        # Start with target URL
        urls_to_scrape = [self.config.target_url]
        current_depth = 0
        
        while urls_to_scrape and current_depth < self.config.max_depth:
            print(f"\n📊 Processing depth {current_depth + 1}/{self.config.max_depth}")
            print(f"URLs to process: {len(urls_to_scrape)}")
            
            # Process URLs in batches
            batch_size = self.config.concurrent_requests
            next_level_urls = set()
            
            for i in range(0, len(urls_to_scrape), batch_size):
                batch = urls_to_scrape[i:i + batch_size]
                
                # Process batch
                tasks = []
                for url in batch:
                    if url not in self.scraped_urls:
                        tasks.append(self.scrape_comprehensive(url))
                        self.scraped_urls.add(url)
                
                # Execute batch
                if tasks:
                    batch_results = await asyncio.gather(*tasks, return_exceptions=True)
                    
                    for result in batch_results:
                        if isinstance(result, ExtractedData):
                            self.results.append(result)
                            
                            # Collect links for next depth level
                            if current_depth < self.config.max_depth - 1:
                                for link in result.links:
                                    if self.is_same_domain(link, self.config.target_url):
                                        next_level_urls.add(link)
                
                # Respect rate limiting
                if i + batch_size < len(urls_to_scrape):
                    await asyncio.sleep(self.config.request_delay)
            
            # Move to next depth level
            urls_to_scrape = list(next_level_urls)
            current_depth += 1
        
        print(f"\n🎉 SCRAPING COMPLETE!")
        print(f"Total pages scraped: {len(self.results)}")
        print(f"Total unique URLs found: {len(self.scraped_urls)}")
        
        # Save results
        self.save_results()
        
        # Print summary
        self.print_summary()
    
    def is_same_domain(self, url: str, base_url: str) -> bool:
        """Check if URL is from the same domain"""
        try:
            return urlparse(url).netloc == urlparse(base_url).netloc
        except:
            return False
    
    def print_summary(self):
        """Print extraction summary"""
        if not self.results:
            return
        
        total_text = sum(len(r.text_content) for r in self.results)
        total_links = sum(len(r.links) for r in self.results)
        total_images = sum(len(r.images) for r in self.results)
        avg_response_time = sum(r.response_time for r in self.results) / len(self.results)
        
        print("\n📊 EXTRACTION SUMMARY")
        print("=" * 40)
        print(f"Pages scraped: {len(self.results)}")
        print(f"Total text extracted: {total_text:,} characters")
        print(f"Total links found: {total_links:,}")
        print(f"Total images found: {total_images:,}")
        print(f"Average response time: {avg_response_time:.2f}s")
        
        # Show top pages by content
        print(f"\n📄 TOP PAGES BY CONTENT:")
        sorted_results = sorted(self.results, key=lambda x: len(x.text_content), reverse=True)
        for i, result in enumerate(sorted_results[:5]):
            print(f"   {i+1}. {result.url} ({len(result.text_content):,} chars)")

def main():
    """Main function to run comprehensive web scraping"""
    print("🕷️  COMPREHENSIVE WEB SCRAPER - 2024 Edition")
    print("=" * 60)
    
    # Get target URL
    target_url = input("Enter target URL to scrape: ").strip()
    if not target_url:
        print("❌ No URL provided")
        return
    
    # Configure scraping
    config = ScrapingConfig(
        target_url=target_url,
        max_depth=int(input("Max depth (default 2): ") or "2"),
        concurrent_requests=int(input("Concurrent requests (default 5): ") or "5"),
        request_delay=float(input("Request delay in seconds (default 1.0): ") or "1.0"),
        use_proxies=input("Use proxies? (y/N): ").lower().startswith('y'),
        extract_images=input("Extract images? (Y/n): ").lower() != 'n',
        extract_links=input("Extract links? (Y/n): ").lower() != 'n'
    )
    
    # Create and run scraper
    scraper = ComprehensiveWebScraper(config)
    
    try:
        asyncio.run(scraper.run_comprehensive_extraction())
    except KeyboardInterrupt:
        print("\n⏹️  Scraping interrupted by user")
    except Exception as e:
        print(f"❌ Error during scraping: {e}")

if __name__ == "__main__":
    main()