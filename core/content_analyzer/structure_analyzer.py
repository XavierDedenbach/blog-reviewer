"""
Content structure analyzer for analyzing headings, sections, and content metrics.
"""

import re
from typing import Dict, Any, List
from .models import ContentStructure


class ContentStructureAnalyzer:
    """Analyzer for content structure and metrics."""
    
    def __init__(self):
        self.sentence_end_pattern = re.compile(r'[.!?]+')
        self.word_pattern = re.compile(r'\b\w+\b')
        self.complex_word_pattern = re.compile(r'\b\w{7,}\b')
        self.avg_words_per_sentence = 15  # Industry standard
    
    def analyze_structure(self, parsed_content: Dict[str, Any]) -> ContentStructure:
        """Analyze content structure and generate metrics."""
        content = parsed_content['content']
        structure = parsed_content['structure']
        
        # Calculate basic metrics
        total_words = self._count_words(content)
        total_sentences = self._count_sentences(content)
        total_paragraphs = len(structure['paragraphs'])
        
        # Extract headings
        headings = [h['text'] for h in structure['headings']]
        
        # Analyze sections
        sections = self._analyze_sections(structure)
        
        # Calculate reading time
        reading_time_minutes = self._calculate_reading_time(total_words)
        
        # Calculate complexity score
        complexity_score = self._calculate_complexity_score(content, total_words, total_sentences)
        
        # Calculate structure score
        structure_score = self._calculate_structure_score(structure)
        
        return ContentStructure(
            total_words=total_words,
            total_sentences=total_sentences,
            total_paragraphs=total_paragraphs,
            headings=headings,
            sections=sections,
            reading_time_minutes=reading_time_minutes,
            complexity_score=complexity_score,
            structure_score=structure_score
        )
    
    def _count_words(self, content: str) -> int:
        """Count words in content."""
        # Count words directly from content (keeping markdown formatting)
        words = self.word_pattern.findall(content)
        # Filter out empty strings
        words = [word for word in words if word.strip()]
        return len(words)
    
    def _count_sentences(self, content: str) -> int:
        """Count sentences in content."""
        # Count sentences directly from content (keeping markdown formatting)
        sentences = self.sentence_end_pattern.split(content)
        # Filter out empty sentences
        sentences = [s.strip() for s in sentences if s.strip()]
        return len(sentences)
    

    
    def _analyze_sections(self, structure: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze content sections based on headings."""
        sections = []
        headings = structure['headings']
        paragraphs = structure['paragraphs']
        
        if not headings:
            # Single section if no headings
            sections.append({
                'title': 'Main Content',
                'level': 0,
                'word_count': sum(len(p.split()) for p in paragraphs),
                'paragraph_count': len(paragraphs),
                'content_type': 'main'
            })
            return sections
        
        # Group content by headings
        current_section = {
            'title': headings[0]['text'],
            'level': headings[0]['level'],
            'word_count': 0,
            'paragraph_count': 0,
            'content_type': self._determine_content_type(headings[0]['text'])
        }
        
        for heading in headings[1:]:
            sections.append(current_section)
            current_section = {
                'title': heading['text'],
                'level': heading['level'],
                'word_count': 0,
                'paragraph_count': 0,
                'content_type': self._determine_content_type(heading['text'])
            }
        
        sections.append(current_section)
        
        return sections
    
    def _determine_content_type(self, heading: str) -> str:
        """Determine content type based on heading."""
        heading_lower = heading.lower()
        
        if any(word in heading_lower for word in ['introduction', 'intro', 'overview']):
            return 'introduction'
        elif any(word in heading_lower for word in ['conclusion', 'summary', 'wrap']):
            return 'conclusion'
        elif any(word in heading_lower for word in ['example', 'demo', 'tutorial']):
            return 'example'
        elif any(word in heading_lower for word in ['setup', 'installation', 'config']):
            return 'setup'
        elif any(word in heading_lower for word in ['api', 'reference', 'docs']):
            return 'reference'
        else:
            return 'content'
    
    def _calculate_reading_time(self, word_count: int) -> float:
        """Calculate estimated reading time in minutes."""
        # Average reading speed: 200-250 words per minute
        # Using 225 words per minute as a reasonable average
        words_per_minute = 225
        return round(word_count / words_per_minute, 1)
    
    def _calculate_complexity_score(self, content: str, total_words: int, total_sentences: int) -> float:
        """Calculate content complexity score (0-1)."""
        if total_words == 0 or total_sentences == 0:
            return 0.0
        
        # Calculate average sentence length
        avg_sentence_length = total_words / total_sentences
        
        # Calculate percentage of complex words (7+ characters)
        complex_words = len(self.complex_word_pattern.findall(content))
        complex_word_ratio = complex_words / total_words if total_words > 0 else 0
        
        # Calculate complexity score based on multiple factors
        sentence_complexity = min(avg_sentence_length / 30, 1.0)  # Normalize to 0-1
        word_complexity = min(complex_word_ratio * 10, 1.0)  # Normalize to 0-1
        
        # Weighted average
        complexity_score = (sentence_complexity * 0.6) + (word_complexity * 0.4)
        
        return round(complexity_score, 3)
    
    def _calculate_structure_score(self, structure: Dict[str, Any]) -> float:
        """Calculate structure quality score (0-1)."""
        score = 0.0
        max_score = 0.0
        
        # Check for headings (30% weight)
        max_score += 0.3
        if structure['headings']:
            heading_levels = [h['level'] for h in structure['headings']]
            # Check for proper heading hierarchy
            if len(heading_levels) > 1:
                # Check if headings follow proper hierarchy (no skipping levels)
                hierarchy_score = 1.0
                for i in range(1, len(heading_levels)):
                    if heading_levels[i] - heading_levels[i-1] > 1:
                        hierarchy_score -= 0.2
                score += 0.3 * max(0, hierarchy_score)
            else:
                score += 0.3
        
        # Check for paragraphs (25% weight)
        max_score += 0.25
        if structure['paragraphs']:
            # Check for reasonable paragraph length
            avg_paragraph_length = sum(len(p.split()) for p in structure['paragraphs']) / len(structure['paragraphs'])
            if 10 <= avg_paragraph_length <= 100:
                score += 0.25
            elif 5 <= avg_paragraph_length <= 150:
                score += 0.2
            else:
                score += 0.1
        
        # Check for lists (20% weight)
        max_score += 0.2
        if structure['lists']:
            score += 0.2
        
        # Check for code blocks (15% weight)
        max_score += 0.15
        if structure['code_blocks']:
            score += 0.15
        
        # Check for blockquotes (10% weight)
        max_score += 0.1
        if structure['blockquotes']:
            score += 0.1
        
        return round(score / max_score, 3) if max_score > 0 else 0.0
    
    def get_content_summary(self, structure: ContentStructure) -> Dict[str, Any]:
        """Generate a summary of content structure."""
        return {
            'word_count': structure.total_words,
            'sentence_count': structure.total_sentences,
            'paragraph_count': structure.total_paragraphs,
            'heading_count': len(structure.headings),
            'reading_time': f"{structure.reading_time_minutes} minutes",
            'complexity': f"{structure.complexity_score:.1%}",
            'structure_quality': f"{structure.structure_score:.1%}",
            'sections': len(structure.sections)
        }
