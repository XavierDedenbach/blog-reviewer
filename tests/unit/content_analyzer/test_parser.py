"""
Tests for the ContentParser class.
"""

import pytest
from core.content_analyzer.parser import ContentParser


class TestContentParser:
    """Test cases for ContentParser."""
    
    @pytest.fixture
    def parser(self):
        """Create a ContentParser instance."""
        return ContentParser()
    
    @pytest.fixture
    def sample_markdown(self):
        """Sample markdown content for testing."""
        return """---
title: Test Article
author: John Doe
date: 2024-01-01
---

# Introduction

This is a test article with **bold text** and *italic text*.

## Section 1

Here's some content with a [link](https://example.com) and an image ![alt text](image.jpg).

### Subsection

- List item 1
- List item 2
- List item 3

```python
def hello_world():
    print("Hello, World!")
```

> This is a blockquote.

## Section 2

More content here.
"""
    
    def test_parse_content_basic(self, parser, sample_markdown):
        """Test basic content parsing."""
        result = parser.parse_content(sample_markdown)
        
        assert 'metadata' in result
        assert 'content' in result
        assert 'structure' in result
        assert 'links' in result
        assert 'images' in result
        assert 'code_blocks' in result
        assert 'source' in result
        assert 'parsed_at' in result
    
    def test_parse_content_empty(self, parser):
        """Test parsing empty content."""
        with pytest.raises(ValueError, match="Content cannot be empty"):
            parser.parse_content("")
        
        with pytest.raises(ValueError, match="Content cannot be empty"):
            parser.parse_content("   \n   \t   ")
    
    def test_extract_metadata(self, parser):
        """Test metadata extraction."""
        content = """---
title: Test Article
author: John Doe
tags: [test, markdown]
---

# Content here
"""
        result = parser.parse_content(content)
        
        assert result['metadata']['title'] == 'Test Article'
        assert result['metadata']['author'] == 'John Doe'
        assert result['metadata']['tags'] == ['test', 'markdown']
    
    def test_extract_metadata_no_frontmatter(self, parser):
        """Test content without frontmatter."""
        content = "# Content here\n\nNo frontmatter."
        result = parser.parse_content(content)
        
        assert result['metadata'] == {}
    
    def test_extract_metadata_invalid_yaml(self, parser):
        """Test invalid YAML frontmatter."""
        content = """---
title: Test Article
author: John Doe
invalid: [unclosed bracket
---

# Content here
"""
        result = parser.parse_content(content)
        
        # Should handle invalid YAML gracefully
        assert result['metadata'] == {}
    
    def test_parse_structure_headings(self, parser):
        """Test heading extraction."""
        content = """# Main Heading

## Subheading 1

### Sub-subheading

## Subheading 2
"""
        result = parser.parse_content(content)
        structure = result['structure']
        
        assert len(structure['headings']) == 4
        assert structure['headings'][0]['text'] == 'Main Heading'
        assert structure['headings'][0]['level'] == 1
        assert structure['headings'][1]['text'] == 'Subheading 1'
        assert structure['headings'][1]['level'] == 2
    
    def test_parse_structure_paragraphs(self, parser):
        """Test paragraph extraction."""
        content = """# Heading

First paragraph.

Second paragraph with multiple sentences. This is the second sentence.

Third paragraph.
"""
        result = parser.parse_content(content)
        structure = result['structure']
        
        assert len(structure['paragraphs']) == 3
        assert "First paragraph" in structure['paragraphs'][0]
        assert "Second paragraph with multiple sentences" in structure['paragraphs'][1]
    
    def test_parse_structure_lists(self, parser):
        """Test list extraction."""
        content = """# Heading

- Item 1
- Item 2
- Item 3

1. Numbered item 1
2. Numbered item 2
"""
        result = parser.parse_content(content)
        structure = result['structure']
        
        assert len(structure['lists']) == 5
        assert "- Item 1" in structure['lists']
        assert "1. Numbered item 1" in structure['lists']
    
    def test_parse_structure_code_blocks(self, parser):
        """Test code block extraction."""
        content = """# Heading

```python
def hello():
    print("Hello")
```

More content.

```javascript
console.log("Hello");
```
"""
        result = parser.parse_content(content)
        structure = result['structure']
        
        assert len(structure['code_blocks']) == 2
        assert "def hello():" in structure['code_blocks'][0]
        assert "console.log" in structure['code_blocks'][1]
    
    def test_parse_structure_blockquotes(self, parser):
        """Test blockquote extraction."""
        content = """# Heading

> This is a blockquote.

> Another blockquote
> with multiple lines.

Regular content.
"""
        result = parser.parse_content(content)
        structure = result['structure']
        
        assert len(structure['blockquotes']) == 2
        assert "This is a blockquote" in structure['blockquotes'][0]
        assert "Another blockquote with multiple lines" in structure['blockquotes'][1]
    
    def test_extract_links(self, parser):
        """Test link extraction."""
        content = """# Heading

Here's a [link](https://example.com) and another [link text](https://test.com).

[Simple link](https://simple.com)
"""
        result = parser.parse_content(content)
        links = result['links']
        
        assert len(links) == 3
        assert links[0]['text'] == 'link'
        assert links[0]['url'] == 'https://example.com'
        assert links[1]['text'] == 'link text'
        assert links[1]['url'] == 'https://test.com'
    
    def test_extract_images(self, parser):
        """Test image extraction."""
        content = """# Heading

Here's an image ![alt text](image.jpg) and another ![logo](logo.png).

![Simple image](simple.jpg)
"""
        result = parser.parse_content(content)
        images = result['images']
        
        assert len(images) == 3
        assert images[0]['alt_text'] == 'alt text'
        assert images[0]['url'] == 'image.jpg'
        assert images[1]['alt_text'] == 'logo'
        assert images[1]['url'] == 'logo.png'
    
    def test_extract_code_blocks(self, parser):
        """Test code block extraction."""
        content = """# Heading

```python
def hello():
    print("Hello")
```

```javascript
console.log("Hello");
```
"""
        result = parser.parse_content(content)
        code_blocks = result['code_blocks']
        
        assert len(code_blocks) == 2
        assert code_blocks[0]['language'] == 'unknown'
        assert "def hello():" in code_blocks[0]['code']
        assert "console.log" in code_blocks[1]['code']
    
    def test_validate_content_valid(self, parser):
        """Test content validation with valid content."""
        valid_content = """# Test Content

This is valid content without any issues.

[Valid link](https://example.com)
"""
        issues = parser.validate_content(valid_content)
        assert issues == []
    
    def test_validate_content_empty(self, parser):
        """Test content validation with empty content."""
        issues = parser.validate_content("")
        assert "Content is empty" in issues
    
    def test_validate_content_long_lines(self, parser):
        """Test content validation with long lines."""
        long_line = "This is a very long line that exceeds the recommended length of 100 characters and should trigger a validation warning."
        content = f"# Heading\n\n{long_line}\n\nMore content."
        
        issues = parser.validate_content(content)
        assert any("too long" in issue for issue in issues)
    
    def test_validate_content_unclosed_code_block(self, parser):
        """Test content validation with unclosed code block."""
        content = """# Heading

```python
def hello():
    print("Hello")

More content.
"""
        issues = parser.validate_content(content)
        assert any("Unclosed code block" in issue for issue in issues)
    
    def test_validate_content_broken_links(self, parser):
        """Test content validation with broken links."""
        content = """# Heading

[Link](broken-link) and [Another](relative/path) and [Good](https://example.com)
"""
        issues = parser.validate_content(content)
        assert any("broken link" in issue.lower() for issue in issues)
    
    def test_parse_file_success(self, parser, tmp_path):
        """Test parsing a file successfully."""
        file_path = tmp_path / "test.md"
        content = """---
title: Test File
---

# Content

This is test content.
"""
        file_path.write_text(content)
        
        result = parser.parse_file(str(file_path))
        assert result['source'] == str(file_path)
        assert result['metadata']['title'] == 'Test File'
    
    def test_parse_file_not_found(self, parser):
        """Test parsing a non-existent file."""
        with pytest.raises(ValueError, match="File not found"):
            parser.parse_file("nonexistent.md")
    
    def test_parse_file_unicode_error(self, parser, tmp_path):
        """Test parsing a file with encoding issues."""
        file_path = tmp_path / "test.md"
        # Write binary data that's not valid UTF-8
        file_path.write_bytes(b'\xff\xfe\x00\x00')
        
        with pytest.raises(ValueError, match="Unable to decode file"):
            parser.parse_file(str(file_path))
    
    def test_parse_content_with_source(self, parser):
        """Test parsing content with source parameter."""
        content = "# Test Content"
        source = "test.md"
        
        result = parser.parse_content(content, source)
        assert result['source'] == source
