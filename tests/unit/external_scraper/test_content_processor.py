"""
Unit tests for content processor.
"""

import pytest
from datetime import datetime
from core.external_scraper.content_processor import ContentProcessor


class TestContentProcessor:
    """Test ContentProcessor class."""
    
    def test_content_processor_creation(self):
        """Test creating ContentProcessor."""
        processor = ContentProcessor()
        
        assert processor.config == {}
        assert processor.content_selectors
        assert processor.remove_selectors
    
    def test_content_processor_with_config(self):
        """Test creating ContentProcessor with config."""
        config = {"test": "value"}
        processor = ContentProcessor(config)
        
        assert processor.config == config
    
    def test_generate_content_hash(self):
        """Test content hash generation."""
        processor = ContentProcessor()
        
        content1 = "Test content"
        content2 = "Test content"
        content3 = "Different content"
        
        hash1 = processor.generate_content_hash(content1)
        hash2 = processor.generate_content_hash(content2)
        hash3 = processor.generate_content_hash(content3)
        
        # Same content should have same hash
        assert hash1 == hash2
        
        # Different content should have different hash
        assert hash1 != hash3
        
        # Hash should be a valid SHA-256 hash (64 hex characters)
        assert len(hash1) == 64
        assert all(c in '0123456789abcdef' for c in hash1)
    
    def test_is_duplicate_exact_match(self):
        """Test duplicate detection with exact match."""
        processor = ContentProcessor()
        
        content1 = "This is test content"
        content2 = "This is test content"
        
        assert processor.is_duplicate(content1, content2)
    
    def test_is_duplicate_different_content(self):
        """Test duplicate detection with different content."""
        processor = ContentProcessor()
        
        content1 = "This is test content"
        content2 = "This is different content"
        
        assert not processor.is_duplicate(content1, content2)
    
    def test_is_duplicate_empty_content(self):
        """Test duplicate detection with empty content."""
        processor = ContentProcessor()
        
        assert not processor.is_duplicate("", "Some content")
        assert not processor.is_duplicate("Some content", "")
        assert not processor.is_duplicate("", "")
    
    def test_is_duplicate_with_threshold(self):
        """Test duplicate detection with custom threshold."""
        processor = ContentProcessor()
        
        content1 = "This is test content with some words"
        content2 = "This is test content with different words"
        
        # Should not be duplicate with high threshold
        assert not processor.is_duplicate(content1, content2, threshold=0.9)
        
        # Should be duplicate with low threshold
        assert processor.is_duplicate(content1, content2, threshold=0.3)
    
    def test_validate_content_quality_good_content(self):
        """Test content quality validation with good content."""
        processor = ContentProcessor()
        
        content = "This is a good article with sufficient length and proper structure. It contains multiple sentences and provides enough content to pass the minimum length validation. The content should be long enough to avoid being flagged as too short."
        metadata = {
            "title": "Test Article",
            "author": "John Doe",
            "description": "A test article"
        }
        
        score, issues = processor.validate_content_quality(content, metadata)
        
        assert score > 0.5  # Should have good score
        assert len(issues) == 0  # No issues
    
    def test_validate_content_quality_short_content(self):
        """Test content quality validation with short content."""
        processor = ContentProcessor()
        
        content = "Short"
        metadata = {"title": "Test"}
        
        score, issues = processor.validate_content_quality(content, metadata)
        
        assert score < 0.7  # Should have lower score
        assert "Content too short" in [issue for issue in issues]
    
    def test_validate_content_quality_missing_title(self):
        """Test content quality validation with missing title."""
        processor = ContentProcessor()
        
        content = "This is a longer article with sufficient content to pass validation."
        metadata = {"author": "John Doe"}
        
        score, issues = processor.validate_content_quality(content, metadata)
        
        assert score < 0.9  # Should have lower score due to missing title
        assert "Missing title" in [issue for issue in issues]
    
    def test_validate_content_quality_excessive_whitespace(self):
        """Test content quality validation with excessive whitespace."""
        processor = ContentProcessor()
        
        content = "This is content.\n\n\n\n\nToo much whitespace.\n\n\n\n\n"
        metadata = {"title": "Test", "author": "John"}
        
        score, issues = processor.validate_content_quality(content, metadata)
        
        assert score < 1.0  # Should have lower score
        assert "Excessive whitespace" in [issue for issue in issues]
    
    def test_clean_content(self):
        """Test content cleaning."""
        processor = ContentProcessor()
        
        content = "  This   has   extra   spaces  \n\n\n\nAnd   excessive   newlines  "
        cleaned = processor._clean_content(content)
        
        # Should remove excessive whitespace
        assert "   " not in cleaned  # No triple spaces
        assert "\n\n\n\n" not in cleaned  # No excessive newlines
        assert cleaned.strip() == cleaned  # No leading/trailing whitespace
    
    def test_calculate_content_metrics(self):
        """Test content metrics calculation."""
        processor = ContentProcessor()
        
        content = "This is a test article. It has multiple sentences. This should give us some metrics."
        
        metrics = processor._calculate_content_metrics(content)
        
        assert metrics["word_count"] > 0
        assert metrics["reading_time"] > 0
        assert metrics["language"] == "en"
    
    def test_calculate_content_metrics_empty(self):
        """Test content metrics calculation with empty content."""
        processor = ContentProcessor()
        
        metrics = processor._calculate_content_metrics("")
        
        assert metrics["word_count"] == 0
        assert metrics["reading_time"] == 0
        assert metrics["language"] == "en"
    
    def test_parse_date_valid_formats(self):
        """Test date parsing with valid formats."""
        processor = ContentProcessor()
        
        # Test ISO format
        date1 = processor._parse_date("2024-01-15T10:30:00")
        assert date1 == datetime(2024, 1, 15, 10, 30, 0)
        
        # Test date only
        date2 = processor._parse_date("2024-01-15")
        assert date2 == datetime(2024, 1, 15)
        
        # Test readable format
        date3 = processor._parse_date("January 15, 2024")
        assert date3 == datetime(2024, 1, 15)
    
    def test_parse_date_invalid_formats(self):
        """Test date parsing with invalid formats."""
        processor = ContentProcessor()
        
        # Invalid format
        date1 = processor._parse_date("invalid-date")
        assert date1 is None
        
        # Empty string
        date2 = processor._parse_date("")
        assert date2 is None
        
        # None
        date3 = processor._parse_date(None)
        assert date3 is None
