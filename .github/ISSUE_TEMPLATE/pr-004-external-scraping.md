# PR-004: External Content Scraping System

## Overview
**Size**: ~380 lines | **Duration**: 3-4 days  
**Primary Agent**: external-scraper

Implement comprehensive web scraping system for author content collection using Firecrawl MCP and Brave Search APIs.

## Description
Build a robust web scraping system that discovers and collects author content from various online sources. The system must handle rate limiting, content validation, deduplication, and provide reliable content extraction while respecting website policies and API limits.

## Tasks
- [ ] Integrate Firecrawl MCP for advanced web scraping capabilities
- [ ] Implement Brave Search API integration for content discovery
- [ ] Create intelligent rate limiting and retry logic for all API calls
- [ ] Build comprehensive content cleaning and quality validation system
- [ ] Implement duplicate content detection and deduplication algorithms
- [ ] Create scraping job queue with progress tracking and monitoring
- [ ] Add content categorization and metadata extraction
- [ ] Implement scraping session management and analytics
- [ ] Create error handling and recovery mechanisms for network failures
- [ ] Add content storage integration with database models

## Testing Requirements
Following testing_strategy.md for External API Integration Features:

### Unit Tests (80% coverage minimum)
- [ ] Test Firecrawl API client with mocked responses for various scenarios
- [ ] Test Brave Search API integration with mocked search results
- [ ] Test rate limiting logic prevents API abuse and handles limits correctly
- [ ] Test content cleaning algorithms with various HTML structures
- [ ] Test duplicate detection algorithms with real and synthetic content
- [ ] Test scraping queue management and job processing logic
- [ ] Test error handling for network failures, timeouts, and invalid responses
- [ ] Test content validation and quality scoring algorithms

### Integration Tests (95% coverage)
- [ ] Test Firecrawl integration with recorded HTTP responses using VCR.py
- [ ] Test Brave Search integration with recorded API responses
- [ ] Test complete scraping workflow from discovery to storage
- [ ] Test rate limiting behavior under realistic API usage patterns
- [ ] Test content deduplication with real author content samples
- [ ] Test error recovery and retry mechanisms with simulated failures
- [ ] Test scraping analytics and monitoring data collection
- [ ] Test integration with database storage for scraped content

### Performance Tests  
- [ ] Scraping operations respect rate limits (< 5 requests/second per service)
- [ ] Content processing handles large articles (> 10,000 words) efficiently
- [ ] Concurrent scraping jobs scale appropriately (10+ parallel jobs)
- [ ] Memory usage remains reasonable during large scraping sessions
- [ ] Error recovery completes within 30 seconds for retry cycles

## Acceptance Criteria
- [ ] Can discover and scrape articles from provided URLs successfully
- [ ] Respects API rate limits and handles HTTP errors gracefully
- [ ] Content quality filtering removes low-value content effectively  
- [ ] Duplicate detection prevents storage of duplicate articles
- [ ] Scraping jobs provide accurate progress updates and status tracking
- [ ] System handles network failures and API outages with proper recovery
- [ ] Scraped content meets quality standards for style analysis
- [ ] Integration with database storage works correctly and efficiently
- [ ] Analytics provide useful insights into scraping performance and results

## Technical Specifications

### Firecrawl MCP Integration
```python
class FirecrawlClient:
    async def scrape_url(self, url: str, options: dict) -> ScrapingResult:
        """Scrape single URL using Firecrawl service."""
        
    async def batch_scrape(self, urls: List[str]) -> List[ScrapingResult]:
        """Scrape multiple URLs efficiently."""
        
    def configure_extraction(self, options: dict):
        """Configure content extraction parameters."""
```

### Brave Search Integration
```python
class BraveSearchClient:
    async def search_author_content(self, author: str, domain: str = None) -> SearchResults:
        """Search for author content across the web."""
        
    async def discover_author_urls(self, author: str) -> List[str]:
        """Discover URLs for author's published content."""
```

### Content Processing Pipeline
```python
class ContentProcessor:
    def clean_content(self, html: str) -> str:
        """Clean and normalize scraped HTML content."""
        
    def validate_quality(self, content: str) -> QualityScore:
        """Assess content quality and relevance."""
        
    def detect_duplicates(self, content: str, existing: List[str]) -> bool:
        """Detect if content is duplicate of existing articles."""
        
    def extract_metadata(self, html: str, url: str) -> ContentMetadata:
        """Extract article metadata (title, date, author, etc.)."""
```

### Scraping Result Format
```python
{
  "scraping_metadata": {
    "source_url": str,
    "scraped_at": datetime,
    "scraper_version": str,
    "processing_time": float,
    "success": bool
  },
  "article_data": {
    "title": str,
    "content": str,              # Clean markdown content
    "word_count": int,
    "author": str,
    "published_date": datetime,
    "canonical_url": str,
    "images": List[dict],
    "metadata": dict
  },
  "quality_assessment": {
    "content_completeness": float,    # 0-1 score
    "extraction_confidence": float,   # 0-1 score  
    "quality_score": float,          # 1-10 score
    "issues": List[str]              # Quality issues found
  }
}
```

### Rate Limiting Strategy
- **Firecrawl**: Maximum 2 requests per second with exponential backoff
- **Brave Search**: Respect API plan limits with intelligent queuing
- **Website Scraping**: 1-3 second delays between requests to same domain
- **Global Limits**: Coordinate rate limiting across all scraping services
- **Retry Logic**: Exponential backoff with maximum retry limits

### Content Quality Validation
```python
class QualityValidator:
    def validate_content(self, content: str, metadata: dict) -> ValidationResult:
        """Comprehensive content quality validation."""
        
    def check_minimum_length(self, content: str) -> bool:
        """Ensure content meets minimum word count (500 words)."""
        
    def detect_spam_content(self, content: str) -> bool:
        """Detect promotional or low-quality content."""
        
    def validate_language(self, content: str) -> bool:
        """Ensure content is primarily in target language (English)."""
```

### Error Handling and Recovery
- **Network Failures**: Automatic retry with exponential backoff
- **API Rate Limits**: Queue management with respect for limits
- **Content Processing Errors**: Graceful degradation with error logging
- **Service Outages**: Fallback strategies and status monitoring
- **Partial Failures**: Continue processing successful results

## Performance Requirements
- API requests respect rate limits: Firecrawl < 2/sec, Brave Search per plan limits
- Content processing: < 10 seconds per article for typical blog posts
- Duplicate detection: < 5 seconds comparison against existing content database
- Scraping sessions: Handle 100+ URLs with progress tracking
- Memory usage: < 1GB for large scraping operations
- Error recovery: Complete retry cycles within 30 seconds

## External Service Configuration

### Firecrawl MCP Settings
```python
FIRECRAWL_CONFIG = {
    "formats": ["markdown", "html"],
    "include_tags": ["title", "meta", "time", "author"],
    "exclude_tags": ["nav", "footer", "ads", "sidebar"],
    "wait_for": 2000,                # Wait for page load
    "screenshot": False,             # Don't capture screenshots
    "extract_main_content": True     # Focus on main article content
}
```

### Brave Search Configuration  
```python
BRAVE_SEARCH_CONFIG = {
    "count": 20,                     # Results per query
    "offset": 0,                     # Pagination offset
    "freshness": "py",               # Past year content
    "content_type": "article",       # Focus on articles
    "extra_snippets": True           # Get content snippets
}
```

## Dependencies
- **PR-001**: Requires project infrastructure and environment setup
- **PR-002**: Requires database models for content storage
- **External Services**: Firecrawl MCP, Brave Search API access
- **Python Libraries**: aiohttp, beautifulsoup4, dateparser, urllib3

## Claude Code Agent Guidance
Use the **external-scraper** agent for:
- Web scraping architecture and best practices
- API integration patterns and error handling
- Rate limiting strategies and queue management
- Content extraction and cleaning algorithms
- Duplicate detection and content validation methods

Ask the external-scraper agent specific questions like:
- "Design a robust web scraping system using Firecrawl MCP with proper rate limiting"
- "Implement content quality validation that filters out low-value scraped content"
- "Create duplicate detection algorithm for identifying similar articles across sources"
- "Design error handling and recovery system for network failures and API outages"

## Related Issues
- **Depends on**: PR-001 (Infrastructure), PR-002 (Database models)
- **Blocks**: PR-008 (Author Management API needs scraping), PR-012 (Advanced scraping features)

---

**Ready for Development**  
@claude Please begin implementation of PR-004 using the external-scraper agent for web scraping architecture and API integrations.