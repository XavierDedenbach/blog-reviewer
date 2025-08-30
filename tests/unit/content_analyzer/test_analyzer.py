"""
Tests for the ContentAnalyzer class.
"""

import pytest
from core.content_analyzer.analyzer import ContentAnalyzer, ContentAnalysisError


class TestContentAnalyzer:
    """Test cases for ContentAnalyzer."""
    
    @pytest.fixture
    def analyzer(self):
        """Create a ContentAnalyzer instance."""
        return ContentAnalyzer()
    
    @pytest.fixture
    def sample_content(self):
        """Sample content for testing."""
        return """# Introduction to Python Programming

Python is a versatile programming language that is widely used in various fields including web development, data science, and artificial intelligence.

## Getting Started

To begin programming in Python, you need to install Python on your computer. The installation process is straightforward and well-documented.

### Installation Steps

1. Download Python from the official website
2. Run the installer
3. Verify the installation

```python
print("Hello, World!")
```

## Basic Concepts

Python has several fundamental concepts that every programmer should understand.

### Variables and Data Types

Variables in Python are dynamically typed, meaning you don't need to declare their type explicitly.

```python
name = "John"
age = 25
height = 1.75
is_student = True
```

## Conclusion

Python is an excellent language for beginners and experienced programmers alike. Its simplicity and readability make it a great choice for various applications.

> Remember: Practice makes perfect when learning to program!
"""
    
    @pytest.mark.asyncio
    async def test_analyze_content_basic(self, analyzer, sample_content):
        """Test basic content analysis."""
        result = await analyzer.analyze_content(sample_content)
        
        # Check that all analysis components are present
        assert result.content_structure is not None
        assert result.style_analysis is not None
        assert result.purpose_analysis is not None
        assert result.quality_metrics is not None
        assert result.processing_time_seconds > 0
        
        # Check content structure
        assert result.content_structure.total_words > 0
        assert result.content_structure.total_sentences > 0
        assert result.content_structure.total_paragraphs > 0
        assert len(result.content_structure.headings) > 0
        
        # Check style analysis
        assert result.style_analysis.tone in ['formal', 'casual', 'technical', 'mixed', 'neutral']
        assert result.style_analysis.voice in ['active', 'passive', 'mixed']
        assert 0 <= result.style_analysis.readability_score <= 100
        
        # Check purpose analysis
        assert result.purpose_analysis.purpose in ['educational', 'tutorial', 'technical', 'informational', 'entertainment']
        assert result.purpose_analysis.target_audience is not None
        assert 0 <= result.purpose_analysis.purpose_alignment <= 1
        
        # Check quality metrics
        assert 0 <= result.quality_metrics.overall_score <= 100
        assert 0 <= result.quality_metrics.clarity_score <= 100
        assert 0 <= result.quality_metrics.coherence_score <= 100
        assert 0 <= result.quality_metrics.completeness_score <= 100
        assert 0 <= result.quality_metrics.accuracy_score <= 100
        assert 0 <= result.quality_metrics.engagement_score <= 100
    
    @pytest.mark.asyncio
    async def test_analyze_content_with_parameters(self, analyzer, sample_content):
        """Test content analysis with specific parameters."""
        result = await analyzer.analyze_content(
            content=sample_content,
            purpose="educational",
            target_audience="beginners",
            content_id="test-123"
        )
        
        assert result.content_id == "test-123"
        assert result.purpose_analysis.purpose == "educational"
        assert result.purpose_analysis.target_audience == "beginners"
    
    @pytest.mark.asyncio
    async def test_analyze_content_empty(self, analyzer):
        """Test analysis with empty content."""
        with pytest.raises(ContentAnalysisError):
            await analyzer.analyze_content("")
    
    @pytest.mark.asyncio
    async def test_analyze_content_whitespace_only(self, analyzer):
        """Test analysis with whitespace-only content."""
        with pytest.raises(ContentAnalysisError):
            await analyzer.analyze_content("   \n   \t   ")
    
    @pytest.mark.asyncio
    async def test_analyze_file_success(self, analyzer, tmp_path):
        """Test file analysis."""
        file_path = tmp_path / "test.md"
        content = """# Test File

This is a test file for analysis.

## Section

More content here.
"""
        file_path.write_text(content)
        
        result = await analyzer.analyze_file(str(file_path))
        assert result.content_id == str(file_path)
        assert result.content_structure.total_words > 0
    
    @pytest.mark.asyncio
    async def test_analyze_file_not_found(self, analyzer):
        """Test file analysis with non-existent file."""
        with pytest.raises(ContentAnalysisError):
            await analyzer.analyze_file("nonexistent.md")
    
    def test_get_analysis_summary(self, analyzer, sample_content):
        """Test analysis summary generation."""
        # Create a mock analysis result
        from core.content_analyzer.models import (
            AnalysisResults, ContentStructure, StyleAnalysis, 
            PurposeAnalysis, QualityMetrics
        )
        
        mock_result = AnalysisResults(
            content_id="test-123",
            content_structure=ContentStructure(
                total_words=100,
                total_sentences=10,
                total_paragraphs=5,
                headings=["Introduction", "Section 1"],
                sections=[],
                reading_time_minutes=0.5,
                complexity_score=0.3,
                structure_score=0.8
            ),
            style_analysis=StyleAnalysis(
                tone="formal",
                voice="active",
                sentence_structure="varied",
                vocabulary_level="intermediate",
                readability_score=75.0,
                style_consistency=0.8,
                engagement_score=0.7,
                style_notes=[]
            ),
            purpose_analysis=PurposeAnalysis(
                purpose="educational",
                target_audience="beginners",
                content_type="tutorial",
                purpose_alignment=0.9,
                audience_appropriateness=0.8,
                purpose_questions=[],
                purpose_notes=[]
            ),
            quality_metrics=QualityMetrics(
                overall_score=85.0,
                clarity_score=90.0,
                coherence_score=85.0,
                completeness_score=80.0,
                accuracy_score=90.0,
                engagement_score=75.0,
                quality_issues=[],
                improvement_suggestions=[]
            ),
            processing_time_seconds=0.5
        )
        
        summary = analyzer.get_analysis_summary(mock_result)
        
        assert summary['content_id'] == "test-123"
        assert summary['processing_time'] == "0.5s"
        assert summary['overall_quality'] == "85.0/100"
        assert summary['content_stats']['words'] == 100
        assert summary['content_stats']['sentences'] == 10
        assert summary['content_stats']['paragraphs'] == 5
        assert summary['style_summary']['tone'] == "formal"
        assert summary['style_summary']['voice'] == "active"
        assert summary['purpose_summary']['purpose'] == "educational"
        assert summary['purpose_summary']['target_audience'] == "beginners"
        assert summary['quality_summary']['clarity'] == "90.0/100"
        assert summary['issues_count'] == 0
        assert summary['suggestions_count'] == 0
    
    def test_validate_content_valid(self, analyzer):
        """Test content validation with valid content."""
        valid_content = """# Test Content

This is valid content with proper structure and enough words to pass validation without any issues.

## Section

More content here to ensure we have sufficient length for the validation to pass without warnings.

### Subsection

Even more content to make sure we have enough words and proper structure.
"""
        result = analyzer.validate_content(valid_content)
        
        assert result['is_valid'] is True
        assert result['issues'] == []
        # May have warnings for length, but should be valid
    
    def test_validate_content_empty(self, analyzer):
        """Test content validation with empty content."""
        result = analyzer.validate_content("")
        
        assert result['is_valid'] is False
        assert "Content is empty" in result['issues']
    
    def test_validate_content_whitespace_only(self, analyzer):
        """Test content validation with whitespace-only content."""
        result = analyzer.validate_content("   \n   \t   ")
        
        assert result['is_valid'] is False
        assert "Content is empty" in result['issues']
    
    def test_validate_content_too_short(self, analyzer):
        """Test content validation with very short content."""
        short_content = "This is very short."
        result = analyzer.validate_content(short_content)
        
        assert result['is_valid'] is True
        assert any("very short" in warning for warning in result['warnings'])
    
    def test_validate_content_too_long(self, analyzer):
        """Test content validation with very long content."""
        # Create content with more than 25,000 words to trigger the warning
        # Use shorter sentences to avoid line length issues
        long_content = "\n".join([f"This is sentence {i} with reasonable length." for i in range(4000)])
        result = analyzer.validate_content(long_content)
        
        # Should be valid but with warnings
        assert result['is_valid'] is True
        assert any("very long" in warning for warning in result['warnings'])
    
    def test_validate_content_with_issues(self, analyzer):
        """Test content validation with content issues."""
        problematic_content = """# Heading

This is a very long line that exceeds the recommended length of 100 characters and should trigger a validation warning because it's too long.

```python
def unclosed_code_block():
    print("This code block is not closed properly")

More content here.
"""
        result = analyzer.validate_content(problematic_content)
        
        assert result['is_valid'] is False
        assert any("too long" in issue for issue in result['issues'])
        assert any("Unclosed code block" in issue for issue in result['issues'])
    
    def test_get_supported_formats(self, analyzer):
        """Test supported formats information."""
        formats = analyzer.get_supported_formats()
        
        assert 'markdown' in formats
        assert 'plain_text' in formats
        assert 'html' in formats
        assert 'docx' in formats
        
        assert formats['markdown']['supported'] is True
        assert formats['html']['supported'] is False
        assert formats['docx']['supported'] is False
        
        assert 'Headers (H1-H6)' in formats['markdown']['features']
        assert 'Basic text analysis' in formats['plain_text']['features']
    
    def test_get_analysis_capabilities(self, analyzer):
        """Test analysis capabilities information."""
        capabilities = analyzer.get_analysis_capabilities()
        
        assert 'content_parsing' in capabilities
        assert 'style_analysis' in capabilities
        assert 'purpose_analysis' in capabilities
        assert 'quality_assessment' in capabilities
        assert 'performance' in capabilities
        
        # Check specific capabilities
        assert capabilities['content_parsing']['markdown_parsing'] is True
        assert capabilities['style_analysis']['tone_detection'] is True
        assert capabilities['purpose_analysis']['content_type_detection'] is True
        assert capabilities['quality_assessment']['clarity_scoring'] is True
        assert capabilities['performance']['async_processing'] is True
    
    @pytest.mark.asyncio
    async def test_analyze_content_different_purposes(self, analyzer):
        """Test analysis with different content purposes."""
        educational_content = """# Learning Python

This tutorial will teach you the basics of Python programming.

## Step 1: Installation

First, download Python from python.org.

## Step 2: Hello World

Write your first program:

```python
print("Hello, World!")
```
"""
        
        result = await analyzer.analyze_content(educational_content, purpose="educational")
        assert result.purpose_analysis.purpose == "educational"
        
        review_content = """# Product Review: Python IDE

This is a comprehensive review of the best Python IDEs available.

## Pros
- Easy to use
- Good documentation

## Cons
- Expensive
- Resource intensive

## Conclusion

Overall, this IDE is excellent for beginners.
"""
        
        result = await analyzer.analyze_content(review_content, purpose="review")
        assert result.purpose_analysis.purpose == "review"
    
    @pytest.mark.asyncio
    async def test_analyze_content_different_audiences(self, analyzer):
        """Test analysis with different target audiences."""
        beginner_content = """# Introduction to Programming

Programming is the process of creating instructions for computers.

## What is a Computer?

A computer is a machine that can process information.
"""
        
        result = await analyzer.analyze_content(beginner_content, target_audience="beginners")
        assert result.purpose_analysis.target_audience == "beginners"
        
        advanced_content = """# Advanced Algorithm Optimization

This article explores sophisticated techniques for optimizing algorithms.

## Time Complexity Analysis

The time complexity of this algorithm is O(n log n).
"""
        
        result = await analyzer.analyze_content(advanced_content, target_audience="advanced")
        assert result.purpose_analysis.target_audience == "advanced"
    
    def test_content_analysis_error(self):
        """Test ContentAnalysisError exception."""
        error = ContentAnalysisError("Test error message", 1.5)
        
        assert str(error) == "Test error message"
        assert error.processing_time == 1.5
