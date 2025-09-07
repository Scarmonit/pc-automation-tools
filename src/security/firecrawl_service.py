#!/usr/bin/env python3
"""
Firecrawl Service for Swarm Intelligence
Provides web crawling, scraping, and research capabilities
"""

import os
import json
import asyncio
import logging
from typing import Dict, List, Any, Optional, Union
from firecrawl import FirecrawlApp
from pathlib import Path

class FirecrawlService:
    """Service for integrating Firecrawl web scraping capabilities with Swarm Intelligence"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Firecrawl service"""
        self.api_key = api_key or os.getenv('FIRECRAWL_API_KEY')
        if not self.api_key:
            raise ValueError("Firecrawl API key not found. Set FIRECRAWL_API_KEY environment variable.")
        
        self.firecrawl = FirecrawlApp(api_key=self.api_key)
        self.logger = logging.getLogger(__name__)
        
    async def crawl_website(self, 
                          url: str, 
                          max_pages: int = 5,
                          include_paths: Optional[List[str]] = None,
                          exclude_paths: Optional[List[str]] = None,
                          wait_for_selector: Optional[str] = None,
                          extract_schema: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Crawl an entire website or specific paths
        
        Args:
            url: Base URL to crawl
            max_pages: Maximum number of pages to crawl
            include_paths: Specific paths to include
            exclude_paths: Paths to exclude
            wait_for_selector: CSS selector to wait for before scraping
            extract_schema: Schema for structured data extraction
            
        Returns:
            Dict containing crawl results with metadata
        """
        try:
            crawl_params = {
                'url': url,
                'limit': max_pages,
                'scrapeOptions': {
                    'formats': ['markdown', 'html'],
                    'includeTags': ['title', 'meta', 'h1', 'h2', 'h3', 'p', 'a', 'img'],
                }
            }
            
            if include_paths:
                crawl_params['includePaths'] = include_paths
            if exclude_paths:
                crawl_params['excludePaths'] = exclude_paths
            if wait_for_selector:
                crawl_params['scrapeOptions']['waitFor'] = wait_for_selector
            if extract_schema:
                crawl_params['scrapeOptions']['extractorOptions'] = {
                    'extractionSchema': extract_schema
                }
            
            self.logger.info(f"Starting crawl of {url} with max {max_pages} pages")
            
            # Use asyncio to run the synchronous firecrawl method
            result = await asyncio.get_event_loop().run_in_executor(
                None, 
                lambda: self.firecrawl.crawl(**crawl_params)
            )
            
            # Firecrawl v2 returns a CrawlResult object with data attribute
            if hasattr(result, 'data') and result.data:
                crawled_data = result.data
                self.logger.info(f"Successfully crawled {len(crawled_data)} pages from {url}")
                
                # Convert Document objects to dicts
                data_list = []
                for doc in crawled_data:
                    data_list.append({
                        'markdown': doc.markdown if hasattr(doc, 'markdown') else '',
                        'html': doc.html if hasattr(doc, 'html') else '',
                        'metadata': doc.metadata.__dict__ if hasattr(doc, 'metadata') else {},
                        'links': doc.links if hasattr(doc, 'links') else [],
                        'images': doc.images if hasattr(doc, 'images') else []
                    })
                
                return {
                    'success': True,
                    'url': url,
                    'pages_crawled': len(crawled_data),
                    'data': data_list,
                    'metadata': {
                        'crawl_params': crawl_params,
                        'timestamp': asyncio.get_event_loop().time()
                    }
                }
            else:
                error_msg = result.error if hasattr(result, 'error') else 'Unknown crawl error'
                self.logger.error(f"Crawl failed for {url}: {error_msg}")
                return {
                    'success': False,
                    'url': url,
                    'error': error_msg
                }
                
        except Exception as e:
            self.logger.error(f"Exception during crawl of {url}: {str(e)}")
            return {
                'success': False,
                'url': url,
                'error': str(e)
            }
    
    async def scrape_page(self, 
                         url: str, 
                         format: str = 'markdown',
                         wait_for_selector: Optional[str] = None,
                         extract_schema: Optional[Dict] = None,
                         include_tags: Optional[List[str]] = None,
                         exclude_tags: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Scrape a single webpage
        
        Args:
            url: URL to scrape
            format: Output format ('markdown', 'html', 'raw-html')
            wait_for_selector: CSS selector to wait for
            extract_schema: Schema for structured data extraction
            include_tags: HTML tags to include
            exclude_tags: HTML tags to exclude
            
        Returns:
            Dict containing scraped content and metadata
        """
        try:
            scrape_params = {
                'url': url,
                'formats': [format]
            }
            
            if wait_for_selector:
                scrape_params['waitFor'] = wait_for_selector
            if include_tags:
                scrape_params['includeTags'] = include_tags
            if exclude_tags:
                scrape_params['excludeTags'] = exclude_tags
            if extract_schema:
                scrape_params['extractorOptions'] = {
                    'extractionSchema': extract_schema
                }
            
            self.logger.info(f"Scraping page: {url}")
            
            # Use asyncio to run the synchronous firecrawl method
            result = await asyncio.get_event_loop().run_in_executor(
                None, 
                lambda: self.firecrawl.scrape(**scrape_params)
            )
            
            # Firecrawl v2 returns a Document object directly
            if result and not (hasattr(result, 'error') and result.error):
                self.logger.info(f"Successfully scraped {url}")
                
                # Get content based on format
                content = ''
                if format == 'markdown' and hasattr(result, 'markdown'):
                    content = result.markdown or ''
                elif format == 'html' and hasattr(result, 'html'):
                    content = result.html or ''
                elif format == 'raw-html' and hasattr(result, 'raw_html'):
                    content = result.raw_html or ''
                else:
                    # Default to markdown if available
                    content = result.markdown if hasattr(result, 'markdown') else ''
                
                return {
                    'success': True,
                    'url': url,
                    'format': format,
                    'content': content,
                    'metadata': result.metadata.__dict__ if hasattr(result, 'metadata') else {},
                    'extracted_data': result.json if hasattr(result, 'json') else {},
                    'links': result.links if hasattr(result, 'links') else [],
                    'images': result.images if hasattr(result, 'images') else []
                }
            else:
                error_msg = result.error if hasattr(result, 'error') else 'Unknown scrape error'
                self.logger.error(f"Scrape failed for {url}: {error_msg}")
                return {
                    'success': False,
                    'url': url,
                    'error': error_msg
                }
                
        except Exception as e:
            self.logger.error(f"Exception during scrape of {url}: {str(e)}")
            return {
                'success': False,
                'url': url,
                'error': str(e)
            }
    
    async def search_web(self, 
                        query: str, 
                        num_results: int = 10,
                        search_engine: str = 'google',
                        include_domains: Optional[List[str]] = None,
                        exclude_domains: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Search the web and optionally scrape results
        
        Args:
            query: Search query
            num_results: Number of search results to return
            search_engine: Search engine to use
            include_domains: Domains to include in results
            exclude_domains: Domains to exclude from results
            
        Returns:
            Dict containing search results
        """
        try:
            search_params = {
                'query': query,
                'pageOptions': {
                    'fetchPageContent': True
                },
                'searchOptions': {
                    'limit': num_results
                }
            }
            
            if include_domains:
                search_params['searchOptions']['includeDomains'] = include_domains
            if exclude_domains:
                search_params['searchOptions']['excludeDomains'] = exclude_domains
            
            self.logger.info(f"Searching web for: {query}")
            
            # Use asyncio to run the synchronous firecrawl method
            result = await asyncio.get_event_loop().run_in_executor(
                None, 
                lambda: self.firecrawl.search(**search_params)
            )
            
            # Firecrawl v2 search returns SearchResult with data attribute
            if hasattr(result, 'data') and result.data:
                search_data = []
                for doc in result.data:
                    search_data.append({
                        'url': doc.metadata.url if hasattr(doc, 'metadata') and hasattr(doc.metadata, 'url') else '',
                        'title': doc.metadata.title if hasattr(doc, 'metadata') and hasattr(doc.metadata, 'title') else '',
                        'markdown': doc.markdown if hasattr(doc, 'markdown') else '',
                        'metadata': doc.metadata.__dict__ if hasattr(doc, 'metadata') else {}
                    })
                
                self.logger.info(f"Found {len(search_data)} results for query: {query}")
                
                return {
                    'success': True,
                    'query': query,
                    'num_results': len(search_data),
                    'results': search_data,
                    'metadata': {
                        'search_params': search_params,
                        'timestamp': asyncio.get_event_loop().time()
                    }
                }
            else:
                error_msg = result.error if hasattr(result, 'error') else 'Unknown search error'
                self.logger.error(f"Search failed for query '{query}': {error_msg}")
                return {
                    'success': False,
                    'query': query,
                    'error': error_msg
                }
                
        except Exception as e:
            self.logger.error(f"Exception during search for '{query}': {str(e)}")
            return {
                'success': False,
                'query': query,
                'error': str(e)
            }
    
    async def extract_structured_data(self, 
                                    url: str, 
                                    schema: Dict[str, Any],
                                    wait_for_selector: Optional[str] = None) -> Dict[str, Any]:
        """
        Extract structured data from a webpage using a schema
        
        Args:
            url: URL to extract data from
            schema: Extraction schema defining what data to extract
            wait_for_selector: CSS selector to wait for
            
        Returns:
            Dict containing extracted structured data
        """
        try:
            extract_params = {
                'url': url,
                'extractorOptions': {
                    'extractionSchema': schema
                }
            }
            
            if wait_for_selector:
                extract_params['waitFor'] = wait_for_selector
            
            self.logger.info(f"Extracting structured data from: {url}")
            
            # Use scrape with extraction schema
            result = await self.scrape_page(
                url=url,
                extract_schema=schema,
                wait_for_selector=wait_for_selector
            )
            
            if result['success']:
                extracted = result.get('extracted_data', {})
                return {
                    'success': True,
                    'url': url,
                    'schema': schema,
                    'extracted_data': extracted,
                    'metadata': result.get('metadata', {})
                }
            else:
                return result
                
        except Exception as e:
            self.logger.error(f"Exception during data extraction from {url}: {str(e)}")
            return {
                'success': False,
                'url': url,
                'error': str(e)
            }
    
    async def map_website(self, 
                         url: str, 
                         max_depth: int = 3,
                         include_subdomains: bool = False) -> Dict[str, Any]:
        """
        Create a sitemap of a website
        
        Args:
            url: Base URL to map
            max_depth: Maximum crawl depth
            include_subdomains: Whether to include subdomains
            
        Returns:
            Dict containing website map
        """
        try:
            map_params = {
                'url': url,
                'search': False,
                'limit': 100,
                'allowBackwardCrawling': False,
                'allowExternalContentLinks': include_subdomains
            }
            
            self.logger.info(f"Mapping website: {url}")
            
            # Use asyncio to run the synchronous firecrawl method
            result = await asyncio.get_event_loop().run_in_executor(
                None, 
                lambda: self.firecrawl.map(**map_params)
            )
            
            # Firecrawl v2 map returns MapResult with links attribute
            if hasattr(result, 'links') and result.links:
                map_data = result.links
                self.logger.info(f"Mapped {len(map_data)} links from {url}")
                
                return {
                    'success': True,
                    'url': url,
                    'total_links': len(map_data),
                    'links': map_data,
                    'metadata': {
                        'map_params': map_params,
                        'timestamp': asyncio.get_event_loop().time()
                    }
                }
            elif result and not (hasattr(result, 'error') and result.error):
                # Map might return empty links list
                return {
                    'success': True,
                    'url': url,
                    'total_links': 0,
                    'links': [],
                    'metadata': {
                        'map_params': map_params,
                        'timestamp': asyncio.get_event_loop().time()
                    }
                }
            else:
                error_msg = result.error if hasattr(result, 'error') else 'Unknown mapping error'
                self.logger.error(f"Website mapping failed for {url}: {error_msg}")
                return {
                    'success': False,
                    'url': url,
                    'error': error_msg
                }
                
        except Exception as e:
            self.logger.error(f"Exception during website mapping of {url}: {str(e)}")
            return {
                'success': False,
                'url': url,
                'error': str(e)
            }
    
    def create_extraction_schema(self, fields: Dict[str, str]) -> Dict[str, Any]:
        """
        Create a data extraction schema for structured scraping
        
        Args:
            fields: Dict mapping field names to descriptions
            
        Returns:
            Formatted extraction schema
        """
        schema = {
            "type": "object",
            "properties": {},
            "required": list(fields.keys())
        }
        
        for field_name, description in fields.items():
            schema["properties"][field_name] = {
                "type": "string",
                "description": description
            }
        
        return schema
    
    async def intelligent_research(self, 
                                 topic: str, 
                                 max_sources: int = 5,
                                 extract_facts: bool = True) -> Dict[str, Any]:
        """
        Perform intelligent research on a topic using web search + scraping
        
        Args:
            topic: Research topic/query
            max_sources: Maximum number of sources to research
            extract_facts: Whether to extract key facts
            
        Returns:
            Dict containing research results with analysis
        """
        try:
            self.logger.info(f"Starting intelligent research on: {topic}")
            
            # First, search for relevant sources
            search_result = await self.search_web(
                query=topic,
                num_results=max_sources * 2  # Get extra results to filter
            )
            
            if not search_result['success']:
                return search_result
            
            # Process top results
            sources = search_result['results'][:max_sources]
            research_data = []
            
            for source in sources:
                url = source.get('url', '')
                title = source.get('title', '')
                
                # Create extraction schema if requested
                schema = None
                if extract_facts:
                    schema = self.create_extraction_schema({
                        'key_facts': f'Key facts about {topic}',
                        'main_points': f'Main points related to {topic}',
                        'summary': f'Brief summary of content about {topic}'
                    })
                
                # Scrape detailed content
                scrape_result = await self.scrape_page(
                    url=url,
                    extract_schema=schema,
                    format='markdown'
                )
                
                if scrape_result['success']:
                    research_data.append({
                        'url': url,
                        'title': title,
                        'content': scrape_result['content'],
                        'extracted_data': scrape_result.get('extracted_data', {}),
                        'metadata': scrape_result.get('metadata', {})
                    })
            
            return {
                'success': True,
                'topic': topic,
                'sources_researched': len(research_data),
                'research_data': research_data,
                'metadata': {
                    'timestamp': asyncio.get_event_loop().time(),
                    'total_search_results': len(sources)
                }
            }
            
        except Exception as e:
            self.logger.error(f"Exception during intelligent research on '{topic}': {str(e)}")
            return {
                'success': False,
                'topic': topic,
                'error': str(e)
            }

# Async helper functions for integration
async def initialize_firecrawl_service() -> Optional[FirecrawlService]:
    """Initialize Firecrawl service with environment variables"""
    try:
        return FirecrawlService()
    except ValueError as e:
        logging.error(f"Failed to initialize Firecrawl service: {str(e)}")
        return None

async def test_firecrawl_integration():
    """Test basic Firecrawl functionality"""
    service = await initialize_firecrawl_service()
    if not service:
        return False
    
    # Test scraping a simple page
    result = await service.scrape_page("https://example.com")
    return result['success']