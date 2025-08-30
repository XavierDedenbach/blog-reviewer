"""
Main content analyzer service that orchestrates all analysis components.
"""

import time
from typing import Dict, Any, Optional
from .parser import ContentParser
from .structure_analyzer import ContentStructureAnalyzer
from .style_analyzer import StyleAnalyzer
from .question_generator import QuestionGenerator
from .quality_scorer import QualityScorer
from .models import AnalysisResults, ContentStructure, StyleAnalysis, PurposeAnalysis, QualityMetrics


class ContentAnalyzer:
    """Main content analyzer that orchestrates all analysis components."""
    
    def __init__(self):
        self.parser = ContentParser()
        self.structure_analyzer = ContentStructureAnalyzer()
        self.style_analyzer = StyleAnalyzer()
        self.question_generator = QuestionGenerator()
        self.quality_scorer = QualityScorer()
    
    async def analyze_content(self, content: str, purpose: str = "auto", 
                            target_audience: str = "general", content_id: Optional[str] = None) -> AnalysisResults:
        """Perform comprehensive content analysis."""
        start_time = time.time()
        
        try:
            # Step 1: Parse content
            parsed_content = self.parser.parse_content(content)
            
            # Step 2: Analyze content structure
            content_structure = self.structure_analyzer.analyze_structure(parsed_content)
            
            # Step 3: Analyze writing style
            style_analysis = self.style_analyzer.analyze_style(content)
            
            # Step 4: Generate purpose analysis and questions
            purpose_analysis = self.question_generator.generate_purpose_analysis(
                content, purpose, target_audience
            )
            
            # Step 5: Assess quality
            quality_metrics = self.quality_scorer.assess_quality(
                content,
                content_structure.model_dump(),
                style_analysis.model_dump(),
                purpose_analysis.model_dump()
            )
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            # Create comprehensive analysis results
            analysis_results = AnalysisResults(
                content_id=content_id,
                content_structure=content_structure,
                style_analysis=style_analysis,
                purpose_analysis=purpose_analysis,
                quality_metrics=quality_metrics,
                processing_time_seconds=round(processing_time, 3)
            )
            
            return analysis_results
            
        except Exception as e:
            # If analysis fails, return error information
            processing_time = time.time() - start_time
            raise ContentAnalysisError(f"Content analysis failed: {str(e)}", processing_time)
    
    async def analyze_file(self, file_path: str, purpose: str = "auto", 
                          target_audience: str = "general") -> AnalysisResults:
        """Analyze content from a file."""
        try:
            # Parse file
            parsed_content = self.parser.parse_file(file_path)
            content = parsed_content['content']
            
            # Perform analysis
            return await self.analyze_content(content, purpose, target_audience, file_path)
            
        except Exception as e:
            raise ContentAnalysisError(f"File analysis failed: {str(e)}")
    
    def get_analysis_summary(self, analysis_results: AnalysisResults) -> Dict[str, Any]:
        """Generate a summary of analysis results."""
        return {
            'content_id': analysis_results.content_id,
            'processing_time': f"{analysis_results.processing_time_seconds}s",
            'overall_quality': f"{analysis_results.quality_metrics.overall_score}/100",
            'content_stats': {
                'words': analysis_results.content_structure.total_words,
                'sentences': analysis_results.content_structure.total_sentences,
                'paragraphs': analysis_results.content_structure.total_paragraphs,
                'reading_time': f"{analysis_results.content_structure.reading_time_minutes} minutes"
            },
            'style_summary': {
                'tone': analysis_results.style_analysis.tone,
                'voice': analysis_results.style_analysis.voice,
                'readability': f"{analysis_results.style_analysis.readability_score}/100"
            },
            'purpose_summary': {
                'purpose': analysis_results.purpose_analysis.purpose,
                'target_audience': analysis_results.purpose_analysis.target_audience,
                'alignment': f"{analysis_results.purpose_analysis.purpose_alignment:.1%}"
            },
            'quality_summary': {
                'clarity': f"{analysis_results.quality_metrics.clarity_score}/100",
                'coherence': f"{analysis_results.quality_metrics.coherence_score}/100",
                'completeness': f"{analysis_results.quality_metrics.completeness_score}/100",
                'accuracy': f"{analysis_results.quality_metrics.accuracy_score}/100",
                'engagement': f"{analysis_results.quality_metrics.engagement_score}/100"
            },
            'issues_count': len(analysis_results.quality_metrics.quality_issues),
            'suggestions_count': len(analysis_results.quality_metrics.improvement_suggestions)
        }
    
    def validate_content(self, content: str) -> Dict[str, Any]:
        """Validate content before analysis."""
        validation_results = {
            'is_valid': True,
            'issues': [],
            'warnings': []
        }
        
        # Check for empty content
        if not content or not content.strip():
            validation_results['is_valid'] = False
            validation_results['issues'].append("Content is empty")
            return validation_results
        
        # Check content length
        word_count = len(content.split())
        if word_count < 50:
            validation_results['warnings'].append("Content is very short (less than 50 words)")
        elif word_count > 25000:
            validation_results['warnings'].append("Content is very long (more than 25,000 words)")
        
        # Check for common issues
        parser_issues = self.parser.validate_content(content)
        validation_results['issues'].extend(parser_issues)
        
        # Update validity based on issues
        if validation_results['issues']:
            validation_results['is_valid'] = False
        
        return validation_results
    
    def get_supported_formats(self) -> Dict[str, Any]:
        """Get information about supported content formats."""
        return {
            'markdown': {
                'supported': True,
                'features': [
                    'Headers (H1-H6)',
                    'Bold and italic text',
                    'Links and images',
                    'Code blocks and inline code',
                    'Lists (ordered and unordered)',
                    'Blockquotes',
                    'YAML frontmatter'
                ]
            },
            'plain_text': {
                'supported': True,
                'features': [
                    'Basic text analysis',
                    'Structure detection',
                    'Style analysis',
                    'Quality assessment'
                ]
            },
            'html': {
                'supported': False,
                'note': 'HTML support planned for future versions'
            },
            'docx': {
                'supported': False,
                'note': 'Word document support planned for future versions'
            }
        }
    
    def get_analysis_capabilities(self) -> Dict[str, Any]:
        """Get information about analysis capabilities."""
        return {
            'content_parsing': {
                'markdown_parsing': True,
                'metadata_extraction': True,
                'structure_analysis': True,
                'link_extraction': True,
                'image_extraction': True
            },
            'style_analysis': {
                'tone_detection': True,
                'voice_analysis': True,
                'readability_scoring': True,
                'vocabulary_analysis': True,
                'sentence_structure_analysis': True
            },
            'purpose_analysis': {
                'content_type_detection': True,
                'purpose_alignment': True,
                'audience_appropriateness': True,
                'question_generation': True
            },
            'quality_assessment': {
                'clarity_scoring': True,
                'coherence_scoring': True,
                'completeness_scoring': True,
                'accuracy_scoring': True,
                'engagement_scoring': True,
                'issue_identification': True,
                'improvement_suggestions': True
            },
            'performance': {
                'async_processing': True,
                'large_content_support': True,
                'processing_time_tracking': True
            }
        }


class ContentAnalysisError(Exception):
    """Exception raised when content analysis fails."""
    
    def __init__(self, message: str, processing_time: float = 0.0):
        self.message = message
        self.processing_time = processing_time
        super().__init__(self.message)
