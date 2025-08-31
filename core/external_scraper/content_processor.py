"""
Content processing utilities for cleaning and normalizing scraped content.
"""

import re
import hashlib
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from urllib.parse import urlparse, urljoin
import logging
from bs4 import BeautifulSoup, Tag
import html2text

logger = logging.getLogger(__name__)


class ContentProcessor:
    """Process and clean scraped content."""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.html_converter = html2text.HTML2Text()
        self.html_converter.ignore_links = False
        self.html_converter.ignore_images = True
        self.html_converter.body_width = 0  # No line wrapping
        
        # Common content selectors
        self.content_selectors = [
            'article',
            '[role="main"]',
            '.post-content',
            '.entry-content',
            '.article-content',
            '.blog-post',
            '.content',
            'main',
            '.post-body',
            '.article-body'
        ]
        
        # Elements to remove
        self.remove_selectors = [
            'script',
            'style',
            'nav',
            'header',
            'footer',
            '.sidebar',
            '.comments',
            '.advertisement',
            '.ads',
            '.social-share',
            '.related-posts',
            '.newsletter-signup'
        ]
    
    def extract_content(self, html: str, url: str) -> Tuple[str, Dict[str, Any]]:
        """Extract and clean content from HTML."""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Remove unwanted elements
            self._remove_unwanted_elements(soup)
            
            # Extract metadata
            metadata = self._extract_metadata(soup, url)
            
            # Find main content
            content_element = self._find_main_content(soup)
            
            if content_element:
                # Convert to markdown
                content = self.html_converter.handle(str(content_element))
            else:
                # Fallback: extract from body
                content = self.html_converter.handle(str(soup.body or soup))
            
            # Clean and normalize content
            content = self._clean_content(content)
            
            # Calculate content metrics
            metadata.update(self._calculate_content_metrics(content))
            
            return content, metadata
            
        except Exception as e:
            logger.error(f"Error extracting content from {url}: {e}")
            return "", {}
    
    def _remove_unwanted_elements(self, soup: BeautifulSoup) -> None:
        """Remove unwanted elements from the HTML."""
        for selector in self.remove_selectors:
            for element in soup.select(selector):
                element.decompose()
    
    def _find_main_content(self, soup: BeautifulSoup) -> Optional[Tag]:
        """Find the main content element."""
        # Try content-specific selectors first
        for selector in self.content_selectors:
            element = soup.select_one(selector)
            if element and self._is_valid_content(element):
                return element
        
        # Fallback: find the largest text block
        return self._find_largest_text_block(soup)
    
    def _is_valid_content(self, element: Tag) -> bool:
        """Check if an element contains valid content."""
        text = element.get_text(strip=True)
        return len(text) > 200  # Minimum content length
    
    def _find_largest_text_block(self, soup: BeautifulSoup) -> Optional[Tag]:
        """Find the largest text block in the document."""
        candidates = []
        
        for element in soup.find_all(['div', 'article', 'section', 'main']):
            text = element.get_text(strip=True)
            if len(text) > 200:
                candidates.append((element, len(text)))
        
        if candidates:
            # Return the element with the most text
            return max(candidates, key=lambda x: x[1])[0]
        
        return None
    
    def _extract_metadata(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """Extract metadata from HTML."""
        metadata = {
            'title': None,
            'author': None,
            'published_date': None,
            'last_modified': None,
            'language': 'en',
            'description': None,
            'canonical_url': None,
            'og_image': None,
            'og_description': None,
            'tags': []
        }
        
        # Extract title
        title_element = soup.find('title')
        if title_element:
            metadata['title'] = title_element.get_text(strip=True)
        
        # Extract Open Graph title
        og_title = soup.find('meta', property='og:title')
        if og_title and og_title.get('content'):
            metadata['title'] = og_title['content']
        
        # Extract author
        author_selectors = [
            'meta[name="author"]',
            '[rel="author"]',
            '.author',
            '.byline',
            '[itemprop="author"]'
        ]
        
        for selector in author_selectors:
            element = soup.select_one(selector)
            if element:
                if element.name == 'meta':
                    metadata['author'] = element.get('content')
                else:
                    metadata['author'] = element.get_text(strip=True)
                break
        
        # Extract dates
        date_selectors = [
            'meta[property="article:published_time"]',
            'meta[name="published_date"]',
            'time[datetime]',
            '.published-date',
            '[itemprop="datePublished"]'
        ]
        
        for selector in date_selectors:
            element = soup.select_one(selector)
            if element:
                date_str = element.get('datetime') or element.get('content') or element.get_text(strip=True)
                try:
                    metadata['published_date'] = self._parse_date(date_str)
                    break
                except:
                    continue
        
        # Extract description
        desc_selectors = [
            'meta[name="description"]',
            'meta[property="og:description"]',
            '.description',
            '.excerpt'
        ]
        
        for selector in desc_selectors:
            element = soup.select_one(selector)
            if element:
                if element.name == 'meta':
                    metadata['description'] = element.get('content')
                else:
                    metadata['description'] = element.get_text(strip=True)
                break
        
        # Extract canonical URL
        canonical = soup.find('link', rel='canonical')
        if canonical:
            metadata['canonical_url'] = canonical.get('href')
        
        # Extract Open Graph image
        og_image = soup.find('meta', property='og:image')
        if og_image:
            metadata['og_image'] = og_image.get('content')
        
        # Extract Open Graph description
        og_desc = soup.find('meta', property='og:description')
        if og_desc:
            metadata['og_description'] = og_desc.get('content')
        
        # Extract tags/categories
        tag_selectors = [
            'meta[name="keywords"]',
            '.tags a',
            '.categories a',
            '[rel="tag"]'
        ]
        
        for selector in tag_selectors:
            elements = soup.select(selector)
            if elements:
                for element in elements:
                    if element.name == 'meta':
                        tags = element.get('content', '').split(',')
                    else:
                        tags = [element.get_text(strip=True)]
                    
                    metadata['tags'].extend([tag.strip() for tag in tags if tag.strip()])
                break
        
        return metadata
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string into datetime object."""
        if not date_str:
            return None
        
        # Common date formats
        formats = [
            '%Y-%m-%dT%H:%M:%S%z',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d',
            '%B %d, %Y',
            '%b %d, %Y',
            '%d %B %Y',
            '%d %b %Y'
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        return None
    
    def _clean_content(self, content: str) -> str:
        """Clean and normalize content."""
        if not content:
            return ""
        
        # Remove excessive whitespace
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
        content = re.sub(r' +', ' ', content)
        
        # Remove empty lines at start and end
        content = content.strip()
        
        # Normalize line endings
        content = content.replace('\r\n', '\n').replace('\r', '\n')
        
        # Remove markdown artifacts
        content = re.sub(r'^#+\s*$', '', content, flags=re.MULTILINE)
        
        return content
    
    def _calculate_content_metrics(self, content: str) -> Dict[str, Any]:
        """Calculate content metrics."""
        if not content:
            return {
                'word_count': 0,
                'reading_time': 0,
                'language': 'en'
            }
        
        # Word count
        words = re.findall(r'\b\w+\b', content.lower())
        word_count = len(words)
        
        # Reading time (average 200 words per minute)
        reading_time = max(1, word_count // 200)
        
        # Simple language detection (basic English check)
        language = 'en'  # Default to English
        
        return {
            'word_count': word_count,
            'reading_time': reading_time,
            'language': language
        }
    
    def generate_content_hash(self, content: str) -> str:
        """Generate SHA-256 hash of content for deduplication."""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def is_duplicate(self, content1: str, content2: str, threshold: float = 0.9) -> bool:
        """Check if two content pieces are duplicates."""
        if not content1 or not content2:
            return False
        
        # Generate hashes
        hash1 = self.generate_content_hash(content1)
        hash2 = self.generate_content_hash(content2)
        
        # Exact match
        if hash1 == hash2:
            return True
        
        # Calculate similarity (simple approach)
        similarity = self._calculate_similarity(content1, content2)
        return similarity >= threshold
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts."""
        # Simple word-based similarity
        words1 = set(re.findall(r'\b\w+\b', text1.lower()))
        words2 = set(re.findall(r'\b\w+\b', text2.lower()))
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    def validate_content_quality(self, content: str, metadata: Dict[str, Any]) -> Tuple[float, List[str]]:
        """Validate content quality and return score and issues."""
        issues = []
        score = 1.0
        
        # Check content length
        if len(content) < 100:
            issues.append("Content too short")
            score -= 0.3
        
        if len(content) > 100000:
            issues.append("Content too long")
            score -= 0.1
        
        # Check for title
        if not metadata.get('title'):
            issues.append("Missing title")
            score -= 0.2
        
        # Check for author
        if not metadata.get('author'):
            issues.append("Missing author")
            score -= 0.1
        
        # Check for excessive whitespace
        if re.search(r'\n\s*\n\s*\n\s*\n', content):
            issues.append("Excessive whitespace")
            score -= 0.1
        
        # Check for broken links
        broken_links = re.findall(r'\[([^\]]+)\]\([^)]*\)', content)
        if len(broken_links) > 10:
            issues.append("Too many potential broken links")
            score -= 0.1
        
        return max(0.0, score), issues
