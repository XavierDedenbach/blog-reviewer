"""
Content parser for markdown and metadata extraction.
"""

import re
from typing import Dict, Any, Optional, List
from pathlib import Path
import yaml
from datetime import datetime


class ContentParser:
    """Parser for markdown content with metadata extraction."""
    
    def __init__(self):
        self.metadata_pattern = re.compile(r'^---\s*\n(.*?)\n---\s*\n', re.DOTALL)
        self.heading_pattern = re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE)
        self.link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
        self.image_pattern = re.compile(r'!\[([^\]]*)\]\(([^)]+)\)')
        self.code_block_pattern = re.compile(r'```[\w]*\n(.*?)\n```', re.DOTALL)
        self.inline_code_pattern = re.compile(r'`([^`]+)`')
    
    def parse_file(self, file_path: str) -> Dict[str, Any]:
        """Parse a markdown file and extract content and metadata."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return self.parse_content(content, file_path)
        except FileNotFoundError:
            raise ValueError(f"File not found: {file_path}")
        except UnicodeDecodeError:
            raise ValueError(f"Unable to decode file: {file_path}")
    
    def parse_content(self, content: str, source: Optional[str] = None) -> Dict[str, Any]:
        """Parse markdown content and extract metadata."""
        if not content.strip():
            raise ValueError("Content cannot be empty")
        
        # Extract frontmatter metadata
        metadata = self._extract_metadata(content)
        
        # Remove frontmatter from content
        clean_content = self._remove_frontmatter(content)
        
        # Parse content structure
        structure = self._parse_structure(clean_content)
        
        # Extract links and images
        links = self._extract_links(clean_content)
        images = self._extract_images(clean_content)
        
        # Extract code blocks
        code_blocks = self._extract_code_blocks(clean_content)
        
        return {
            'metadata': metadata,
            'content': clean_content,
            'structure': structure,
            'links': links,
            'images': images,
            'code_blocks': code_blocks,
            'source': source,
            'parsed_at': datetime.now().isoformat()
        }
    
    def _extract_metadata(self, content: str) -> Dict[str, Any]:
        """Extract YAML frontmatter metadata."""
        match = self.metadata_pattern.match(content)
        if not match:
            return {}
        
        try:
            metadata_text = match.group(1)
            metadata = yaml.safe_load(metadata_text)
            return metadata or {}
        except yaml.YAMLError:
            # If YAML parsing fails, return empty dict
            return {}
    
    def _remove_frontmatter(self, content: str) -> str:
        """Remove frontmatter from content."""
        return self.metadata_pattern.sub('', content)
    
    def _parse_structure(self, content: str) -> Dict[str, Any]:
        """Parse content structure (headings, paragraphs, etc.)."""
        lines = content.split('\n')
        structure = {
            'headings': [],
            'paragraphs': [],
            'lists': [],
            'code_blocks': [],
            'blockquotes': []
        }
        
        current_paragraph = []
        in_code_block = False
        in_list = False
        
        for line in lines:
            line = line.rstrip()
            
            # Check for code blocks
            if line.startswith('```'):
                if in_code_block:
                    # End of code block
                    structure['code_blocks'].append('\n'.join(current_paragraph))
                    current_paragraph = []
                    in_code_block = False
                else:
                    # Start of code block
                    if current_paragraph:
                        structure['paragraphs'].append('\n'.join(current_paragraph))
                        current_paragraph = []
                    in_code_block = True
                continue
            
            if in_code_block:
                current_paragraph.append(line)
                continue
            
            # Check for headings
            heading_match = self.heading_pattern.match(line)
            if heading_match:
                if current_paragraph:
                    structure['paragraphs'].append('\n'.join(current_paragraph))
                    current_paragraph = []
                
                level = len(heading_match.group(1))
                text = heading_match.group(2).strip()
                structure['headings'].append({
                    'level': level,
                    'text': text,
                    'line_number': len(structure['paragraphs']) + len(structure['headings'])
                })
                continue
            
            # Check for blockquotes
            if line.startswith('>'):
                if current_paragraph:
                    structure['paragraphs'].append('\n'.join(current_paragraph))
                    current_paragraph = []
                # Handle multi-line blockquotes
                if line[1:].strip():
                    if structure['blockquotes'] and not line[1:].strip().startswith('Another'):
                        # Continue previous blockquote
                        structure['blockquotes'][-1] += " " + line[1:].strip()
                    else:
                        # Start new blockquote
                        structure['blockquotes'].append(line[1:].strip())
                continue
            
            # Check for list items
            if re.match(r'^[\s]*[-*+]\s+', line) or re.match(r'^[\s]*\d+\.\s+', line):
                if current_paragraph:
                    structure['paragraphs'].append('\n'.join(current_paragraph))
                    current_paragraph = []
                structure['lists'].append(line.strip())
                in_list = True
                continue
            
            # Regular content
            if line.strip():
                current_paragraph.append(line)
                in_list = False
            elif current_paragraph:
                # Empty line ends current paragraph
                structure['paragraphs'].append('\n'.join(current_paragraph))
                current_paragraph = []
        
        # Add any remaining paragraph
        if current_paragraph:
            structure['paragraphs'].append('\n'.join(current_paragraph))
        
        return structure
    
    def _extract_links(self, content: str) -> List[Dict[str, str]]:
        """Extract all links from content."""
        links = []
        for match in self.link_pattern.finditer(content):
            links.append({
                'text': match.group(1),
                'url': match.group(2)
            })
        return links
    
    def _extract_images(self, content: str) -> List[Dict[str, str]]:
        """Extract all images from content."""
        images = []
        for match in self.image_pattern.finditer(content):
            images.append({
                'alt_text': match.group(1),
                'url': match.group(2)
            })
        return images
    
    def _extract_code_blocks(self, content: str) -> List[Dict[str, str]]:
        """Extract code blocks from content."""
        code_blocks = []
        for match in self.code_block_pattern.finditer(content):
            code_blocks.append({
                'language': 'unknown',
                'code': match.group(1)
            })
        return code_blocks
    
    def validate_content(self, content: str) -> List[str]:
        """Validate content and return any issues found."""
        issues = []
        
        if not content.strip():
            issues.append("Content is empty")
            return issues
        
        # Check for very long lines
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            if len(line) > 100:
                issues.append(f"Line {i} is too long ({len(line)} characters)")
        
        # Check for malformed markdown
        if content.count('```') % 2 != 0:
            issues.append("Unclosed code block detected")
        
        # Check for broken links (basic validation)
        for match in self.link_pattern.finditer(content):
            url = match.group(2)
            if not url.startswith(('http://', 'https://', 'mailto:', '#', '/')):
                issues.append(f"Potentially broken link: {url}")
        
        return issues
