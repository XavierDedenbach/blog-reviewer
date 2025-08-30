"""
Tests for the ContentStructureAnalyzer class.
"""

import pytest
from core.content_analyzer.structure_analyzer import ContentStructureAnalyzer


class TestContentStructureAnalyzer:
    """Test cases for ContentStructureAnalyzer."""
    
    @pytest.fixture
    def analyzer(self):
        """Create a ContentStructureAnalyzer instance."""
        return ContentStructureAnalyzer()
    
    @pytest.fixture
    def sample_parsed_content(self):
        """Sample parsed content for testing."""
        return {
            'content': """# Introduction

This is a test article with multiple paragraphs. It contains various elements.

## Section 1

Here's some content in the first section. This paragraph has multiple sentences.

### Subsection

- List item 1
- List item 2
- List item 3

```python
def hello():
    print("Hello")
```

> This is a blockquote.

## Section 2

More content in the second section.
""",
            'structure': {
                'headings': [
                    {'level': 1, 'text': 'Introduction'},
                    {'level': 2, 'text': 'Section 1'},
                    {'level': 3, 'text': 'Subsection'},
                    {'level': 2, 'text': 'Section 2'}
                ],
                'paragraphs': [
                    'This is a test article with multiple paragraphs. It contains various elements.',
                    "Here's some content in the first section. This paragraph has multiple sentences.",
                    'More content in the second section.'
                ],
                'lists': [
                    '- List item 1',
                    '- List item 2',
                    '- List item 3'
                ],
                'code_blocks': [
                    'def hello():\n    print("Hello")'
                ],
                'blockquotes': [
                    'This is a blockquote.'
                ]
            }
        }
    
    def test_analyze_structure_basic(self, analyzer, sample_parsed_content):
        """Test basic structure analysis."""
        result = analyzer.analyze_structure(sample_parsed_content)
        
        assert result.total_words > 0
        assert result.total_sentences > 0
        assert result.total_paragraphs == 3
        assert len(result.headings) == 4
        assert result.reading_time_minutes > 0
        assert 0 <= result.complexity_score <= 1
        assert 0 <= result.structure_score <= 1
    
    def test_count_words(self, analyzer):
        """Test word counting."""
        content = "This is a test sentence with seven words."
        count = analyzer._count_words(content)
        assert count == 8  # Including the period as a word
    
    def test_count_words_with_markdown(self, analyzer):
        """Test word counting with markdown formatting."""
        content = "# Heading\n\nThis is **bold** and *italic* text with `code`."
        count = analyzer._count_words(content)
        assert count == 9  # "This is bold and italic text with code"
    
    def test_count_sentences(self, analyzer):
        """Test sentence counting."""
        content = "First sentence. Second sentence. Third sentence!"
        count = analyzer._count_sentences(content)
        assert count == 3
    
    def test_count_sentences_with_markdown(self, analyzer):
        """Test sentence counting with markdown."""
        content = "# Heading\n\nFirst sentence. Second sentence with **bold** text."
        count = analyzer._count_sentences(content)
        assert count == 2
    

    
    def test_analyze_sections_with_headings(self, analyzer):
        """Test section analysis with headings."""
        structure = {
            'headings': [
                {'level': 1, 'text': 'Introduction'},
                {'level': 2, 'text': 'Getting Started'},
                {'level': 2, 'text': 'Advanced Topics'},
                {'level': 3, 'text': 'Subsection'}
            ],
            'paragraphs': ['Para 1', 'Para 2', 'Para 3', 'Para 4']
        }
        
        sections = analyzer._analyze_sections(structure)
        
        assert len(sections) == 4
        assert sections[0]['title'] == 'Introduction'
        assert sections[0]['level'] == 1
        assert sections[1]['title'] == 'Getting Started'
        assert sections[1]['level'] == 2
    
    def test_analyze_sections_no_headings(self, analyzer):
        """Test section analysis without headings."""
        structure = {
            'headings': [],
            'paragraphs': ['Para 1', 'Para 2', 'Para 3']
        }
        
        sections = analyzer._analyze_sections(structure)
        
        assert len(sections) == 1
        assert sections[0]['title'] == 'Main Content'
        assert sections[0]['level'] == 0
    
    def test_determine_content_type(self, analyzer):
        """Test content type determination."""
        assert analyzer._determine_content_type('Introduction to Python') == 'introduction'
        assert analyzer._determine_content_type('Conclusion and Summary') == 'conclusion'
        assert analyzer._determine_content_type('Example Implementation') == 'example'
        assert analyzer._determine_content_type('Setup and Installation') == 'setup'
        assert analyzer._determine_content_type('API Reference') == 'reference'
        assert analyzer._determine_content_type('Regular Content') == 'content'
    
    def test_calculate_reading_time(self, analyzer):
        """Test reading time calculation."""
        # Test with different word counts
        assert analyzer._calculate_reading_time(225) == 1.0  # 1 minute
        assert analyzer._calculate_reading_time(450) == 2.0  # 2 minutes
        assert analyzer._calculate_reading_time(100) == 0.4  # Less than 1 minute
    
    def test_calculate_complexity_score(self, analyzer):
        """Test complexity score calculation."""
        # Simple content
        simple_content = "This is a simple sentence. Another simple sentence."
        simple_score = analyzer._calculate_complexity_score(simple_content, 8, 2)
        assert 0 <= simple_score <= 1
        
        # Complex content
        complex_content = "This is a very complex sentence with sophisticated vocabulary and intricate structure that demonstrates advanced linguistic complexity."
        complex_score = analyzer._calculate_complexity_score(complex_content, 20, 1)
        assert complex_score > simple_score
    
    def test_calculate_complexity_score_zero_content(self, analyzer):
        """Test complexity score with zero content."""
        score = analyzer._calculate_complexity_score("", 0, 0)
        assert score == 0.0
    
    def test_calculate_structure_score(self, analyzer):
        """Test structure score calculation."""
        # Good structure
        good_structure = {
            'headings': [
                {'level': 1, 'text': 'Main'},
                {'level': 2, 'text': 'Section 1'},
                {'level': 2, 'text': 'Section 2'}
            ],
            'paragraphs': ['Para 1', 'Para 2', 'Para 3'],
            'lists': ['- Item 1', '- Item 2'],
            'code_blocks': ['```code```'],
            'blockquotes': ['> Quote']
        }
        
        good_score = analyzer._calculate_structure_score(good_structure)
        assert 0 <= good_score <= 1
        
        # Poor structure
        poor_structure = {
            'headings': [],
            'paragraphs': ['One very long paragraph'],
            'lists': [],
            'code_blocks': [],
            'blockquotes': []
        }
        
        poor_score = analyzer._calculate_structure_score(poor_structure)
        assert poor_score < good_score
    
    def test_calculate_structure_score_hierarchy(self, analyzer):
        """Test structure score with proper heading hierarchy."""
        # Proper hierarchy
        proper_structure = {
            'headings': [
                {'level': 1, 'text': 'Main'},
                {'level': 2, 'text': 'Section'},
                {'level': 3, 'text': 'Subsection'}
            ],
            'paragraphs': ['Para'],
            'lists': [],
            'code_blocks': [],
            'blockquotes': []
        }
        
        proper_score = analyzer._calculate_structure_score(proper_structure)
        
        # Improper hierarchy (skipping levels)
        improper_structure = {
            'headings': [
                {'level': 1, 'text': 'Main'},
                {'level': 3, 'text': 'Subsection'}  # Skipped level 2
            ],
            'paragraphs': ['Para'],
            'lists': [],
            'code_blocks': [],
            'blockquotes': []
        }
        
        improper_score = analyzer._calculate_structure_score(improper_structure)
        assert proper_score > improper_score
    
    def test_get_content_summary(self, analyzer, sample_parsed_content):
        """Test content summary generation."""
        structure = analyzer.analyze_structure(sample_parsed_content)
        summary = analyzer.get_content_summary(structure)
        
        assert 'word_count' in summary
        assert 'sentence_count' in summary
        assert 'paragraph_count' in summary
        assert 'heading_count' in summary
        assert 'reading_time' in summary
        assert 'complexity' in summary
        assert 'structure_quality' in summary
        assert 'sections' in summary
        
        assert summary['paragraph_count'] == 3
        assert summary['heading_count'] == 4
        assert 'minutes' in summary['reading_time']
        assert '%' in summary['complexity']
        assert '%' in summary['structure_quality']
    
    def test_edge_cases(self, analyzer):
        """Test edge cases and boundary conditions."""
        # Empty content
        empty_content = {
            'content': '',
            'structure': {
                'headings': [],
                'paragraphs': [],
                'lists': [],
                'code_blocks': [],
                'blockquotes': []
            }
        }
        
        result = analyzer.analyze_structure(empty_content)
        assert result.total_words == 0
        assert result.total_sentences == 0
        assert result.total_paragraphs == 0
        assert result.reading_time_minutes == 0.0
        assert result.complexity_score == 0.0
        
        # Very long content
        long_content = "This is a very long sentence. " * 1000
        long_parsed = {
            'content': long_content,
            'structure': {
                'headings': [],
                'paragraphs': [long_content],
                'lists': [],
                'code_blocks': [],
                'blockquotes': []
            }
        }
        
        result = analyzer.analyze_structure(long_parsed)
        assert result.total_words > 1000
        assert result.reading_time_minutes > 1.0
