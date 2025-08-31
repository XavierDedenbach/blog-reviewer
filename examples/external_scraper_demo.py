#!/usr/bin/env python3
"""
Demonstration script for the External Content Scraping System.

This script shows how to use the external scraper to discover and scrape content.
Note: This requires API keys for Firecrawl and Brave Search to work with real data.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.external_scraper import ExternalScraper, ScrapingConfig


async def demo_basic_scraping():
    """Demonstrate basic scraping functionality."""
    print("=== External Scraper Demo ===\n")
    
    # Initialize the scraper
    scraper = ExternalScraper()
    
    # Note: In a real scenario, you would get these from environment variables
    firecrawl_api_key = os.getenv("FIRECRAWL_API_KEY", "demo_key")
    brave_search_api_key = os.getenv("BRAVE_SEARCH_API_KEY", "demo_key")
    
    print("1. Initializing scraper...")
    try:
        await scraper.initialize(firecrawl_api_key, brave_search_api_key)
        print("   ✓ Scraper initialized successfully")
    except Exception as e:
        print(f"   ⚠ Warning: Could not initialize with real API keys: {e}")
        print("   Continuing with demo mode...")
    
    print("\n2. Creating a scraping job...")
    
    # Example URLs (these would be real URLs in practice)
    test_urls = [
        "https://example.com/article1",
        "https://example.com/article2",
        "https://example.com/article3"
    ]
    
    # Create a scraping configuration
    config = ScrapingConfig(
        rate_limit_requests_per_minute=30,
        max_retries=3,
        timeout_seconds=30,
        delay_between_requests=1.0,
        min_content_length=100,
        max_content_length=50000
    )
    
    # Create a scraping job
    job = await scraper.create_scraping_job(
        urls=test_urls,
        config=config,
        metadata={"demo": True, "purpose": "testing"}
    )
    
    print(f"   ✓ Created job {job.job_id}")
    print(f"   - URLs to scrape: {len(job.urls)}")
    print(f"   - Status: {job.status}")
    
    print("\n3. Job management features:")
    
    # List all jobs
    all_jobs = scraper.list_jobs()
    print(f"   - Total jobs: {len(all_jobs)}")
    
    # Get job status
    job_status = scraper.get_job_status(job.job_id)
    print(f"   - Job status: {job_status.status if job_status else 'Not found'}")
    
    print("\n4. System status:")
    status = await scraper.get_system_status()
    print(f"   - Active jobs: {status['active_jobs']}")
    print(f"   - Total jobs: {status['total_jobs']}")
    print(f"   - Content hashes: {status['content_hashes']}")
    print(f"   - Firecrawl available: {status['firecrawl_available']}")
    print(f"   - Brave Search available: {status['brave_search_available']}")
    
    print("\n5. Content statistics:")
    stats = scraper.get_content_statistics()
    print(f"   - Total results: {stats['total_results']}")
    print(f"   - Successful results: {stats['successful_results']}")
    print(f"   - Failed results: {stats['failed_results']}")
    print(f"   - Success rate: {stats['success_rate']:.2%}")
    print(f"   - Unique content hashes: {stats['unique_content_hashes']}")
    
    print("\n6. Rate limiting demonstration:")
    
    # Show rate limiter stats
    if scraper.firecrawl_client:
        firecrawl_stats = await scraper.firecrawl_client.get_rate_limit_status()
        print(f"   - Firecrawl requests per minute: {firecrawl_stats['requests_in_minute']}")
        print(f"   - Firecrawl rate limit: {firecrawl_stats['rate_limit_per_minute']}")
    
    if scraper.brave_search_client:
        brave_stats = await scraper.brave_search_client.get_rate_limit_status()
        print(f"   - Brave Search requests per minute: {brave_stats['requests_in_minute']}")
        print(f"   - Brave Search rate limit: {brave_stats['rate_limit_per_minute']}")
    
    print("\n7. Content processing features:")
    
    # Demonstrate content processor
    from core.external_scraper.content_processor import ContentProcessor
    
    processor = ContentProcessor()
    
    # Test content hash generation
    content1 = "This is test content for demonstration purposes."
    content2 = "This is test content for demonstration purposes."
    content3 = "This is different content."
    
    hash1 = processor.generate_content_hash(content1)
    hash2 = processor.generate_content_hash(content2)
    hash3 = processor.generate_content_hash(content3)
    
    print(f"   - Content hash 1: {hash1[:16]}...")
    print(f"   - Content hash 2: {hash2[:16]}...")
    print(f"   - Content hash 3: {hash3[:16]}...")
    print(f"   - Hash 1 == Hash 2: {hash1 == hash2}")
    print(f"   - Hash 1 == Hash 3: {hash1 == hash3}")
    
    # Test duplicate detection
    is_duplicate = processor.is_duplicate(content1, content2)
    print(f"   - Content 1 and 2 are duplicates: {is_duplicate}")
    
    is_duplicate = processor.is_duplicate(content1, content3)
    print(f"   - Content 1 and 3 are duplicates: {is_duplicate}")
    
    # Test content quality validation
    metadata = {
        "title": "Test Article",
        "author": "Demo Author",
        "description": "A test article for demonstration"
    }
    
    quality_score, issues = processor.validate_content_quality(content1, metadata)
    print(f"   - Content quality score: {quality_score:.2f}")
    print(f"   - Quality issues: {len(issues)}")
    
    print("\n8. Configuration options:")
    print(f"   - Rate limit per minute: {config.rate_limit_requests_per_minute}")
    print(f"   - Max retries: {config.max_retries}")
    print(f"   - Timeout seconds: {config.timeout_seconds}")
    print(f"   - Delay between requests: {config.delay_between_requests}")
    print(f"   - Min content length: {config.min_content_length}")
    print(f"   - Max content length: {config.max_content_length}")
    print(f"   - Respect robots.txt: {config.respect_robots_txt}")
    print(f"   - Extract images: {config.extract_images}")
    print(f"   - Extract links: {config.extract_links}")
    
    print("\n=== Demo Complete ===")
    print("\nNote: This demo shows the structure and capabilities of the external scraper.")
    print("To use with real data, you would need:")
    print("1. Firecrawl API key for web scraping")
    print("2. Brave Search API key for content discovery")
    print("3. Real URLs to scrape")
    
    # Clean up
    await scraper.cleanup()


async def demo_search_functionality():
    """Demonstrate search and discovery functionality."""
    print("\n=== Search and Discovery Demo ===\n")
    
    scraper = ExternalScraper()
    
    # Initialize with demo keys
    firecrawl_api_key = os.getenv("FIRECRAWL_API_KEY", "demo_key")
    brave_search_api_key = os.getenv("BRAVE_SEARCH_API_KEY", "demo_key")
    
    try:
        await scraper.initialize(firecrawl_api_key, brave_search_api_key)
    except Exception as e:
        print(f"⚠ Warning: Could not initialize with real API keys: {e}")
        print("Search functionality requires valid API keys.")
        return
    
    print("1. Author content discovery:")
    print("   - Search for content by specific authors")
    print("   - Filter by domain")
    print("   - Discover recent articles and blog posts")
    
    print("\n2. Topic-based search:")
    print("   - Search for content on specific topics")
    print("   - Filter by content type (articles, blog posts)")
    print("   - Get recent and relevant results")
    
    print("\n3. RSS feed scraping:")
    print("   - Scrape content from RSS feeds")
    print("   - Extract structured content")
    print("   - Handle feed updates")
    
    print("\n4. Content filtering:")
    print("   - Filter by content quality")
    print("   - Remove duplicates")
    print("   - Apply content length limits")
    
    await scraper.cleanup()


if __name__ == "__main__":
    # Run the demos
    asyncio.run(demo_basic_scraping())
    asyncio.run(demo_search_functionality())
