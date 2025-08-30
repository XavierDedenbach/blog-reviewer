"""
Data models for content analysis results.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class ContentStructure(BaseModel):
    """Content structure analysis results."""
    
    total_words: int = Field(..., description="Total word count")
    total_sentences: int = Field(..., description="Total sentence count")
    total_paragraphs: int = Field(..., description="Total paragraph count")
    headings: List[str] = Field(default=[], description="List of headings found")
    sections: List[Dict[str, Any]] = Field(default=[], description="Content sections with metadata")
    reading_time_minutes: float = Field(..., description="Estimated reading time in minutes")
    complexity_score: float = Field(..., ge=0, le=1, description="Content complexity score (0-1)")
    structure_score: float = Field(..., ge=0, le=1, description="Structure quality score (0-1)")


class StyleAnalysis(BaseModel):
    """Writing style analysis results."""
    
    tone: str = Field(..., description="Overall tone (formal, casual, technical, etc.)")
    voice: str = Field(..., description="Writing voice (active, passive, mixed)")
    sentence_structure: str = Field(..., description="Sentence structure type (varied, simple, complex)")
    vocabulary_level: str = Field(..., description="Vocabulary complexity level")
    readability_score: float = Field(..., ge=0, le=100, description="Readability score (0-100)")
    style_consistency: float = Field(..., ge=0, le=1, description="Style consistency score (0-1)")
    engagement_score: float = Field(..., ge=0, le=1, description="Engagement potential score (0-1)")
    style_notes: List[str] = Field(default=[], description="Style analysis notes")


class PurposeAnalysis(BaseModel):
    """Purpose-based content analysis results."""
    
    purpose: str = Field(..., description="Content purpose (educational, entertainment, etc.)")
    target_audience: str = Field(..., description="Identified target audience")
    content_type: str = Field(..., description="Type of content (tutorial, review, etc.)")
    purpose_alignment: float = Field(..., ge=0, le=1, description="How well content aligns with stated purpose")
    audience_appropriateness: float = Field(..., ge=0, le=1, description="Appropriateness for target audience")
    purpose_questions: List[str] = Field(default=[], description="Generated purpose-specific questions")
    purpose_notes: List[str] = Field(default=[], description="Purpose analysis notes")


class QualityMetrics(BaseModel):
    """Content quality assessment metrics."""
    
    overall_score: float = Field(..., ge=0, le=100, description="Overall quality score (0-100)")
    clarity_score: float = Field(..., ge=0, le=100, description="Content clarity score")
    coherence_score: float = Field(..., ge=0, le=100, description="Content coherence score")
    completeness_score: float = Field(..., ge=0, le=100, description="Content completeness score")
    accuracy_score: float = Field(..., ge=0, le=100, description="Content accuracy score")
    engagement_score: float = Field(..., ge=0, le=100, description="Content engagement score")
    quality_issues: List[str] = Field(default=[], description="Identified quality issues")
    improvement_suggestions: List[str] = Field(default=[], description="Suggestions for improvement")


class AnalysisResults(BaseModel):
    """Complete content analysis results."""
    
    content_id: Optional[str] = Field(None, description="Content identifier")
    analysis_timestamp: datetime = Field(default_factory=datetime.now, description="Analysis timestamp")
    content_structure: ContentStructure = Field(..., description="Content structure analysis")
    style_analysis: StyleAnalysis = Field(..., description="Writing style analysis")
    purpose_analysis: PurposeAnalysis = Field(..., description="Purpose-based analysis")
    quality_metrics: QualityMetrics = Field(..., description="Quality assessment metrics")
    metadata: Dict[str, Any] = Field(default={}, description="Additional analysis metadata")
    processing_time_seconds: float = Field(..., description="Total processing time in seconds")
