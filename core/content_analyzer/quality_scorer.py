"""
Quality scorer for assessing content quality metrics.
"""

import re
from typing import Dict, Any, List
from .models import QualityMetrics


class QualityScorer:
    """Scorer for content quality assessment."""
    
    def __init__(self):
        # Quality indicators
        self.clarity_indicators = {
            'positive': [
                'clear', 'concise', 'simple', 'straightforward', 'easy to understand',
                'well-explained', 'logical', 'organized', 'structured', 'coherent'
            ],
            'negative': [
                'confusing', 'unclear', 'vague', 'ambiguous', 'complex', 'complicated',
                'difficult', 'hard to follow', 'unorganized', 'disjointed'
            ]
        }
        
        self.coherence_indicators = {
            'positive': [
                'flow', 'transition', 'connection', 'link', 'follow', 'lead to',
                'therefore', 'thus', 'consequently', 'as a result', 'because'
            ],
            'negative': [
                'jump', 'disconnect', 'unrelated', 'random', 'out of place',
                'doesn\'t follow', 'no connection', 'irrelevant'
            ]
        }
        
        self.completeness_indicators = {
            'positive': [
                'complete', 'comprehensive', 'thorough', 'detailed', 'full',
                'all aspects', 'everything', 'complete picture', 'whole story'
            ],
            'negative': [
                'incomplete', 'missing', 'partial', 'inadequate', 'insufficient',
                'lacks', 'doesn\'t cover', 'missing information', 'gaps'
            ]
        }
        
        self.accuracy_indicators = {
            'positive': [
                'accurate', 'correct', 'precise', 'exact', 'verified', 'confirmed',
                'reliable', 'trustworthy', 'factual', 'evidence-based'
            ],
            'negative': [
                'inaccurate', 'incorrect', 'wrong', 'false', 'misleading',
                'unverified', 'unreliable', 'questionable', 'doubtful'
            ]
        }
        
        self.engagement_indicators = {
            'positive': [
                'interesting', 'engaging', 'captivating', 'fascinating', 'exciting',
                'compelling', 'intriguing', 'thought-provoking', 'stimulating'
            ],
            'negative': [
                'boring', 'dull', 'uninteresting', 'tedious', 'monotonous',
                'repetitive', 'dry', 'lifeless', 'uninspiring'
            ]
        }
    
    def assess_quality(self, content: str, structure_analysis: Dict[str, Any], 
                      style_analysis: Dict[str, Any], purpose_analysis: Dict[str, Any]) -> QualityMetrics:
        """Assess overall content quality and generate metrics."""
        # Calculate individual quality scores
        clarity_score = self._calculate_clarity_score(content)
        coherence_score = self._calculate_coherence_score(content, structure_analysis)
        completeness_score = self._calculate_completeness_score(content, purpose_analysis)
        accuracy_score = self._calculate_accuracy_score(content)
        engagement_score = self._calculate_engagement_score(content, style_analysis)
        
        # Calculate overall score (weighted average)
        overall_score = self._calculate_overall_score(
            clarity_score, coherence_score, completeness_score, 
            accuracy_score, engagement_score
        )
        
        # Identify quality issues
        quality_issues = self._identify_quality_issues(
            content, clarity_score, coherence_score, completeness_score,
            accuracy_score, engagement_score
        )
        
        # Generate improvement suggestions
        improvement_suggestions = self._generate_improvement_suggestions(
            content, clarity_score, coherence_score, completeness_score,
            accuracy_score, engagement_score, quality_issues
        )
        
        return QualityMetrics(
            overall_score=overall_score,
            clarity_score=clarity_score,
            coherence_score=coherence_score,
            completeness_score=completeness_score,
            accuracy_score=accuracy_score,
            engagement_score=engagement_score,
            quality_issues=quality_issues,
            improvement_suggestions=improvement_suggestions
        )
    
    def _calculate_clarity_score(self, content: str) -> float:
        """Calculate clarity score based on content analysis."""
        content_lower = content.lower()
        
        # Count positive and negative clarity indicators
        positive_count = sum(1 for indicator in self.clarity_indicators['positive'] 
                           if indicator in content_lower)
        negative_count = sum(1 for indicator in self.clarity_indicators['negative'] 
                           if indicator in content_lower)
        
        # Calculate clarity score
        total_indicators = positive_count + negative_count
        if total_indicators == 0:
            return 75.0  # Neutral score if no indicators found
        
        clarity_ratio = positive_count / total_indicators
        clarity_score = clarity_ratio * 100
        
        # Adjust based on content characteristics
        # Check for long sentences (clarity issue)
        sentences = re.split(r'[.!?]+', content)
        long_sentences = sum(1 for s in sentences if len(s.split()) > 25)
        if long_sentences > 0:
            clarity_score -= min(20, long_sentences * 5)
        
        # Check for complex vocabulary (clarity issue)
        complex_words = sum(1 for word in content.split() if len(word) > 12)
        if complex_words > 0:
            clarity_score -= min(15, complex_words * 2)
        
        return max(0.0, min(100.0, clarity_score))
    
    def _calculate_coherence_score(self, content: str, structure_analysis: Dict[str, Any]) -> float:
        """Calculate coherence score based on content structure and flow."""
        content_lower = content.lower()
        
        # Count positive and negative coherence indicators
        positive_count = sum(1 for indicator in self.coherence_indicators['positive'] 
                           if indicator in content_lower)
        negative_count = sum(1 for indicator in self.coherence_indicators['negative'] 
                           if indicator in content_lower)
        
        # Base coherence score
        total_indicators = positive_count + negative_count
        if total_indicators == 0:
            base_score = 75.0
        else:
            coherence_ratio = positive_count / total_indicators
            base_score = coherence_ratio * 100
        
        # Adjust based on structure analysis
        structure_score = structure_analysis.get('structure_score', 0.5) * 100
        
        # Check for logical flow indicators
        flow_indicators = ['first', 'second', 'third', 'next', 'then', 'finally', 'lastly']
        flow_count = sum(1 for indicator in flow_indicators if indicator in content_lower)
        flow_bonus = min(10, flow_count * 2)
        
        # Check for transition words
        transition_words = ['however', 'moreover', 'furthermore', 'additionally', 'in addition']
        transition_count = sum(1 for word in transition_words if word in content_lower)
        transition_bonus = min(10, transition_count * 2)
        
        coherence_score = (base_score + structure_score) / 2 + flow_bonus + transition_bonus
        
        return max(0.0, min(100.0, coherence_score))
    
    def _calculate_completeness_score(self, content: str, purpose_analysis: Dict[str, Any]) -> float:
        """Calculate completeness score based on content coverage."""
        content_lower = content.lower()
        
        # Count positive and negative completeness indicators
        positive_count = sum(1 for indicator in self.completeness_indicators['positive'] 
                           if indicator in content_lower)
        negative_count = sum(1 for indicator in self.completeness_indicators['negative'] 
                           if indicator in content_lower)
        
        # Base completeness score
        total_indicators = positive_count + negative_count
        if total_indicators == 0:
            base_score = 75.0
        else:
            completeness_ratio = positive_count / total_indicators
            base_score = completeness_ratio * 100
        
        # Adjust based on content length and purpose
        word_count = len(content.split())
        purpose = purpose_analysis.get('purpose', 'informational')
        
        # Expected word count ranges by purpose
        expected_ranges = {
            'tutorial': (500, 2000),
            'educational': (800, 3000),
            'review': (600, 2500),
            'technical': (1000, 4000),
            'informational': (400, 2000),
            'entertainment': (300, 1500)
        }
        
        min_expected, max_expected = expected_ranges.get(purpose, (400, 2000))
        
        if word_count < min_expected:
            # Penalize for being too short
            length_penalty = (min_expected - word_count) / min_expected * 30
            base_score -= length_penalty
        elif word_count > max_expected:
            # Slight penalty for being too long
            length_penalty = (word_count - max_expected) / max_expected * 10
            base_score -= min(20, length_penalty)
        
        # Check for essential content elements
        essential_elements = ['introduction', 'conclusion', 'summary']
        if purpose in ['educational', 'tutorial', 'technical']:
            essential_elements.extend(['example', 'explanation', 'step'])
        
        missing_elements = sum(1 for element in essential_elements if element not in content_lower)
        element_penalty = missing_elements * 10
        
        completeness_score = base_score - element_penalty
        
        return max(0.0, min(100.0, completeness_score))
    
    def _calculate_accuracy_score(self, content: str) -> float:
        """Calculate accuracy score based on content analysis."""
        content_lower = content.lower()
        
        # Count positive and negative accuracy indicators
        positive_count = sum(1 for indicator in self.accuracy_indicators['positive'] 
                           if indicator in content_lower)
        negative_count = sum(1 for indicator in self.accuracy_indicators['negative'] 
                           if indicator in content_lower)
        
        # Base accuracy score
        total_indicators = positive_count + negative_count
        if total_indicators == 0:
            base_score = 75.0  # Neutral score if no indicators found
        else:
            accuracy_ratio = positive_count / total_indicators
            base_score = accuracy_ratio * 100
        
        # Check for citation and reference indicators
        citation_indicators = ['according to', 'research shows', 'study', 'source', 'reference']
        citation_count = sum(1 for indicator in citation_indicators if indicator in content_lower)
        citation_bonus = min(15, citation_count * 3)
        
        # Check for hedging language (indicates uncertainty)
        hedging_words = ['maybe', 'perhaps', 'possibly', 'might', 'could', 'seems', 'appears']
        hedging_count = sum(1 for word in hedging_words if word in content_lower)
        hedging_penalty = min(20, hedging_count * 2)
        
        accuracy_score = base_score + citation_bonus - hedging_penalty
        
        return max(0.0, min(100.0, accuracy_score))
    
    def _calculate_engagement_score(self, content: str, style_analysis: Dict[str, Any]) -> float:
        """Calculate engagement score based on content and style analysis."""
        content_lower = content.lower()
        
        # Count positive and negative engagement indicators
        positive_count = sum(1 for indicator in self.engagement_indicators['positive'] 
                           if indicator in content_lower)
        negative_count = sum(1 for indicator in self.engagement_indicators['negative'] 
                           if indicator in content_lower)
        
        # Base engagement score
        total_indicators = positive_count + negative_count
        if total_indicators == 0:
            base_score = 75.0
        else:
            engagement_ratio = positive_count / total_indicators
            base_score = engagement_ratio * 100
        
        # Adjust based on style analysis
        style_engagement = style_analysis.get('engagement_score', 0.5) * 100
        
        # Check for interactive elements
        interactive_elements = ['question', 'think about', 'consider', 'imagine', 'suppose']
        interactive_count = sum(1 for element in interactive_elements if element in content_lower)
        interactive_bonus = min(15, interactive_count * 3)
        
        # Check for storytelling elements
        story_elements = ['story', 'example', 'case study', 'scenario', 'situation']
        story_count = sum(1 for element in story_elements if element in content_lower)
        story_bonus = min(10, story_count * 2)
        
        engagement_score = (base_score + style_engagement) / 2 + interactive_bonus + story_bonus
        
        return max(0.0, min(100.0, engagement_score))
    
    def _calculate_overall_score(self, clarity: float, coherence: float, 
                                completeness: float, accuracy: float, engagement: float) -> float:
        """Calculate overall quality score as weighted average."""
        # Weights for different quality dimensions
        weights = {
            'clarity': 0.25,
            'coherence': 0.20,
            'completeness': 0.20,
            'accuracy': 0.25,
            'engagement': 0.10
        }
        
        overall_score = (
            clarity * weights['clarity'] +
            coherence * weights['coherence'] +
            completeness * weights['completeness'] +
            accuracy * weights['accuracy'] +
            engagement * weights['engagement']
        )
        
        return round(overall_score, 1)
    
    def _identify_quality_issues(self, content: str, clarity: float, coherence: float,
                                completeness: float, accuracy: float, engagement: float) -> List[str]:
        """Identify specific quality issues in the content."""
        issues = []
        
        # Clarity issues
        if clarity < 60:
            issues.append("Content lacks clarity and may be difficult to understand")
        elif clarity < 80:
            issues.append("Content could be clearer in some sections")
        
        # Coherence issues
        if coherence < 60:
            issues.append("Content lacks logical flow and organization")
        elif coherence < 80:
            issues.append("Content flow could be improved with better transitions")
        
        # Completeness issues
        if completeness < 60:
            issues.append("Content is incomplete and missing important information")
        elif completeness < 80:
            issues.append("Content could be more comprehensive")
        
        # Accuracy issues
        if accuracy < 60:
            issues.append("Content accuracy is questionable and needs verification")
        elif accuracy < 80:
            issues.append("Content could benefit from more reliable sources")
        
        # Engagement issues
        if engagement < 60:
            issues.append("Content lacks engagement and may be boring to readers")
        elif engagement < 80:
            issues.append("Content could be more engaging and interactive")
        
        # Content-specific issues
        if len(content.split()) < 200:
            issues.append("Content is too short and may lack sufficient detail")
        elif len(content.split()) > 5000:
            issues.append("Content is very long and may lose reader attention")
        
        # Check for common writing issues
        if content.count('!') > content.count('.') * 0.3:
            issues.append("Overuse of exclamation marks may seem unprofessional")
        
        if content.count('?') == 0:
            issues.append("No questions found - consider adding interactive elements")
        
        return issues
    
    def _generate_improvement_suggestions(self, content: str, clarity: float, coherence: float,
                                        completeness: float, accuracy: float, engagement: float,
                                        issues: List[str]) -> List[str]:
        """Generate specific improvement suggestions."""
        suggestions = []
        
        # Clarity improvements
        if clarity < 80:
            suggestions.append("Break down complex sentences into shorter, clearer ones")
            suggestions.append("Define technical terms and acronyms when first used")
            suggestions.append("Use active voice instead of passive voice")
        
        # Coherence improvements
        if coherence < 80:
            suggestions.append("Add transition words to improve flow between paragraphs")
            suggestions.append("Organize content with clear headings and subheadings")
            suggestions.append("Ensure logical progression from introduction to conclusion")
        
        # Completeness improvements
        if completeness < 80:
            suggestions.append("Add more examples and case studies to illustrate points")
            suggestions.append("Include a clear introduction and conclusion")
            suggestions.append("Address potential counterarguments or alternative viewpoints")
        
        # Accuracy improvements
        if accuracy < 80:
            suggestions.append("Add citations and references to support claims")
            suggestions.append("Verify facts and statistics with reliable sources")
            suggestions.append("Distinguish between facts and opinions clearly")
        
        # Engagement improvements
        if engagement < 80:
            suggestions.append("Add questions to encourage reader interaction")
            suggestions.append("Include relevant examples and stories")
            suggestions.append("Use varied sentence structures to maintain interest")
        
        # General improvements
        if len(content.split()) < 500:
            suggestions.append("Expand content with more detailed explanations")
        
        if len(content.split()) > 3000:
            suggestions.append("Consider breaking content into multiple articles")
        
        return suggestions
