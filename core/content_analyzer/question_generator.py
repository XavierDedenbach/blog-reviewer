"""
Question generator for generating purpose-based questions for content analysis.
"""

import re
from typing import List, Dict, Any
from .models import PurposeAnalysis


class QuestionGenerator:
    """Generator for purpose-based questions."""
    
    def __init__(self):
        # Question templates by purpose
        self.purpose_questions = {
            'educational': [
                "What are the main learning objectives of this content?",
                "How well does the content explain complex concepts?",
                "Are there sufficient examples to illustrate key points?",
                "Does the content follow a logical learning progression?",
                "How accessible is the content for the target audience?",
                "Are there clear definitions for technical terms?",
                "Does the content encourage critical thinking?",
                "How practical and applicable are the concepts presented?"
            ],
            'tutorial': [
                "Are the step-by-step instructions clear and complete?",
                "How well does the content guide users through the process?",
                "Are there sufficient screenshots or visual aids?",
                "Does the content anticipate common user errors?",
                "How well does it explain the reasoning behind each step?",
                "Are there alternative approaches or troubleshooting tips?",
                "Does the content provide context for why each step matters?",
                "How well does it accommodate different skill levels?"
            ],
            'review': [
                "How comprehensive is the evaluation of the subject?",
                "Are the criteria for assessment clearly defined?",
                "How balanced is the review (pros and cons)?",
                "Does the content provide actionable insights?",
                "How well does it compare to alternatives?",
                "Are the conclusions supported by evidence?",
                "How relevant is the review to the target audience?",
                "Does it address the most important aspects of the subject?"
            ],
            'technical': [
                "How accurate are the technical specifications?",
                "Does the content provide sufficient technical depth?",
                "How well does it explain the underlying principles?",
                "Are there code examples or technical diagrams?",
                "How well does it address implementation challenges?",
                "Does it consider performance and scalability aspects?",
                "How well does it explain trade-offs and decisions?",
                "Does it provide best practices and guidelines?"
            ],
            'informational': [
                "How comprehensive is the information coverage?",
                "How well does it organize and present the information?",
                "Are the facts accurate and up-to-date?",
                "How well does it address the audience's information needs?",
                "Does it provide context and background information?",
                "How well does it distinguish between facts and opinions?",
                "Does it provide multiple perspectives on the topic?",
                "How well does it help readers understand the significance?"
            ],
            'entertainment': [
                "How engaging and entertaining is the content?",
                "Does it maintain reader interest throughout?",
                "How well does it use storytelling techniques?",
                "Are there elements of humor or creativity?",
                "How well does it create emotional connection?",
                "Does it provide value beyond entertainment?",
                "How well does it balance entertainment with substance?",
                "Does it appeal to the target audience's interests?"
            ]
        }
        
        # Content type detection patterns
        self.content_patterns = {
            'tutorial': [
                r'step\s*by\s*step', r'how\s*to', r'tutorial', r'guide', r'walkthrough',
                r'instructions', r'procedure', r'process', r'steps', r'follow'
            ],
            'review': [
                r'review', r'evaluation', r'assessment', r'analysis', r'comparison',
                r'pros?\s*and\s*cons?', r'advantages?\s*and\s*disadvantages?', r'rating'
            ],
            'technical': [
                r'technical', r'implementation', r'code', r'programming', r'development',
                r'architecture', r'design', r'algorithm', r'framework', r'api'
            ],
            'educational': [
                r'learn', r'education', r'teaching', r'learning', r'course', r'lesson',
                r'concept', r'principle', r'theory', r'understanding', r'knowledge'
            ],
            'entertainment': [
                r'fun', r'entertaining', r'story', r'anecdote', r'humor', r'joke',
                r'interesting', r'fascinating', r'amazing', r'incredible'
            ]
        }
    
    def generate_questions(self, content: str, purpose: str, target_audience: str) -> List[str]:
        """Generate purpose-based questions for content analysis."""
        # Determine content type if not specified
        if purpose == 'auto':
            purpose = self._detect_content_type(content)
        
        # Get base questions for the purpose
        base_questions = self.purpose_questions.get(purpose, self.purpose_questions['informational'])
        
        # Generate audience-specific questions
        audience_questions = self._generate_audience_questions(target_audience)
        
        # Generate content-specific questions
        content_questions = self._generate_content_specific_questions(content, purpose)
        
        # Combine and return questions
        all_questions = base_questions + audience_questions + content_questions
        
        # Limit to reasonable number and remove duplicates
        unique_questions = list(dict.fromkeys(all_questions))
        return unique_questions[:15]  # Limit to 15 questions
    
    def _detect_content_type(self, content: str) -> str:
        """Detect content type based on content analysis."""
        content_lower = content.lower()
        
        # Count matches for each content type
        type_scores = {}
        for content_type, patterns in self.content_patterns.items():
            score = sum(len(re.findall(pattern, content_lower)) for pattern in patterns)
            type_scores[content_type] = score
        
        # Return the content type with highest score
        if type_scores:
            return max(type_scores, key=type_scores.get)
        else:
            return 'informational'
    
    def _generate_audience_questions(self, target_audience: str) -> List[str]:
        """Generate audience-specific questions."""
        audience_questions = {
            'beginners': [
                "How well does the content accommodate readers with no prior knowledge?",
                "Are complex concepts explained in simple terms?",
                "Does it provide sufficient background information?",
                "Are there clear definitions for all technical terms?"
            ],
            'intermediate': [
                "How well does the content build on existing knowledge?",
                "Does it provide sufficient depth for intermediate learners?",
                "Are there opportunities for practical application?",
                "Does it address common misconceptions?"
            ],
            'advanced': [
                "How well does the content challenge advanced readers?",
                "Does it provide insights beyond basic knowledge?",
                "Are there advanced techniques or approaches covered?",
                "Does it address edge cases and advanced scenarios?"
            ],
            'developers': [
                "How well does the content address implementation details?",
                "Are there code examples or technical specifications?",
                "Does it consider performance and best practices?",
                "How well does it explain technical trade-offs?"
            ],
            'managers': [
                "How well does the content address business implications?",
                "Does it provide strategic insights and decision-making guidance?",
                "Are there cost-benefit analyses or ROI considerations?",
                "How well does it address team and organizational aspects?"
            ],
            'students': [
                "How well does the content support academic learning?",
                "Does it provide clear learning objectives and outcomes?",
                "Are there opportunities for critical thinking and analysis?",
                "How well does it connect to broader concepts and theories?"
            ]
        }
        
        return audience_questions.get(target_audience.lower(), [])
    
    def _generate_content_specific_questions(self, content: str, purpose: str) -> List[str]:
        """Generate questions specific to the content characteristics."""
        questions = []
        
        # Analyze content length
        word_count = len(content.split())
        if word_count < 500:
            questions.append("Is the content comprehensive enough for the topic?")
        elif word_count > 3000:
            questions.append("Is the content appropriately concise and focused?")
        
        # Analyze content structure
        if '#' in content:
            questions.append("How well does the content structure guide the reader?")
        
        # Analyze code presence
        if '```' in content:
            questions.append("How well do the code examples illustrate the concepts?")
        
        # Analyze links and references
        if '[' in content and '](' in content:
            questions.append("How well do the references support the content?")
        
        # Analyze lists and bullet points
        if any(marker in content for marker in ['- ', '* ', '+ ']):
            questions.append("How well do the lists organize and present information?")
        
        return questions
    
    def analyze_purpose_alignment(self, content: str, stated_purpose: str) -> float:
        """Analyze how well content aligns with stated purpose."""
        # Detect actual content type
        detected_type = self._detect_content_type(content)
        
        # Calculate alignment score
        if detected_type == stated_purpose:
            return 1.0
        elif self._are_types_related(detected_type, stated_purpose):
            return 0.7
        else:
            return 0.3
    
    def _are_types_related(self, type1: str, type2: str) -> bool:
        """Check if two content types are related."""
        related_types = {
            'tutorial': ['educational', 'technical'],
            'educational': ['tutorial', 'informational'],
            'technical': ['tutorial', 'educational'],
            'review': ['informational'],
            'informational': ['educational', 'review'],
            'entertainment': ['informational']
        }
        
        return type2 in related_types.get(type1, []) or type1 in related_types.get(type2, [])
    
    def generate_purpose_analysis(self, content: str, purpose: str, target_audience: str) -> PurposeAnalysis:
        """Generate comprehensive purpose analysis."""
        # Determine actual purpose if auto-detection is requested
        actual_purpose = purpose
        if purpose == "auto":
            actual_purpose = self._detect_content_type(content)
        
        # Generate questions
        purpose_questions = self.generate_questions(content, actual_purpose, target_audience)
        
        # Analyze purpose alignment
        purpose_alignment = self.analyze_purpose_alignment(content, actual_purpose)
        
        # Determine content type
        content_type = self._detect_content_type(content)
        
        # Analyze audience appropriateness
        audience_appropriateness = self._analyze_audience_appropriateness(content, target_audience)
        
        # Generate purpose notes
        purpose_notes = self._generate_purpose_notes(content, actual_purpose, target_audience, purpose_alignment)
        
        return PurposeAnalysis(
            purpose=actual_purpose,
            target_audience=target_audience,
            content_type=content_type,
            purpose_alignment=purpose_alignment,
            audience_appropriateness=audience_appropriateness,
            purpose_questions=purpose_questions,
            purpose_notes=purpose_notes
        )
    
    def _analyze_audience_appropriateness(self, content: str, target_audience: str) -> float:
        """Analyze how appropriate the content is for the target audience."""
        content_lower = content.lower()
        
        # Define audience-specific indicators
        audience_indicators = {
            'beginners': [
                'introduction', 'basics', 'fundamentals', 'getting started', 'first time',
                'simple', 'easy', 'basic', 'overview', 'prerequisites'
            ],
            'intermediate': [
                'advanced', 'intermediate', 'experienced', 'deep dive', 'detailed',
                'implementation', 'practical', 'hands-on', 'real-world'
            ],
            'advanced': [
                'expert', 'advanced', 'complex', 'sophisticated', 'optimization',
                'architecture', 'design patterns', 'best practices', 'performance'
            ],
            'developers': [
                'code', 'programming', 'development', 'implementation', 'api',
                'framework', 'library', 'debugging', 'testing', 'deployment'
            ],
            'managers': [
                'strategy', 'business', 'management', 'leadership', 'team',
                'project', 'planning', 'budget', 'timeline', 'stakeholder'
            ],
            'students': [
                'learning', 'education', 'study', 'academic', 'research',
                'theory', 'concept', 'principle', 'analysis', 'evaluation'
            ]
        }
        
        indicators = audience_indicators.get(target_audience.lower(), [])
        if not indicators:
            return 0.5  # Neutral score for unknown audience
        
        # Count indicator matches
        matches = sum(1 for indicator in indicators if indicator in content_lower)
        max_matches = len(indicators)
        
        if max_matches == 0:
            return 0.5
        
        # Calculate appropriateness score
        appropriateness = min(1.0, matches / max_matches * 2)  # Scale to 0-1
        return round(appropriateness, 3)
    
    def _generate_purpose_notes(self, content: str, purpose: str, target_audience: str, alignment: float) -> List[str]:
        """Generate notes about purpose analysis."""
        notes = []
        
        # Purpose alignment notes
        if alignment >= 0.8:
            notes.append("Content strongly aligns with stated purpose")
        elif alignment >= 0.6:
            notes.append("Content moderately aligns with stated purpose")
        else:
            notes.append("Content has weak alignment with stated purpose")
        
        # Audience appropriateness notes
        audience_score = self._analyze_audience_appropriateness(content, target_audience)
        if audience_score >= 0.8:
            notes.append("Content is highly appropriate for target audience")
        elif audience_score >= 0.6:
            notes.append("Content is moderately appropriate for target audience")
        else:
            notes.append("Content may not be well-suited for target audience")
        
        # Content type notes
        detected_type = self._detect_content_type(content)
        if detected_type != purpose:
            notes.append(f"Content appears to be {detected_type} rather than {purpose}")
        
        return notes
