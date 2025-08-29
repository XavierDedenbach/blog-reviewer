from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator
from bson import ObjectId


class PyObjectId(ObjectId):
    """Custom ObjectId field for Pydantic models."""
    
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        return {
            'type': 'any',
            'validator': cls.validate,
        }
    
    @classmethod
    def validate(cls, v):
        if isinstance(v, str):
            if not ObjectId.is_valid(v):
                raise ValueError("Invalid ObjectId")
            return ObjectId(v)
        elif isinstance(v, ObjectId):
            return v
        else:
            raise ValueError("Invalid ObjectId")


class ReviewConfig(BaseModel):
    """Model for review configuration and weights."""
    style_weight: float = Field(..., ge=0.0, le=1.0)
    grammar_weight: float = Field(..., ge=0.0, le=1.0)
    purpose_weight: float = Field(..., ge=0.0, le=1.0)
    
    @field_validator('style_weight', 'grammar_weight', 'purpose_weight')
    @classmethod
    def validate_weights(cls, v):
        """Validate individual weights are between 0 and 1."""
        if not 0.0 <= v <= 1.0:
            raise ValueError("Weight must be between 0.0 and 1.0")
        return v
    
    @field_validator('purpose_weight')
    @classmethod
    def validate_total_weights(cls, v, info):
        """Validate that all weights sum to 1.0."""
        if hasattr(info, 'data') and info.data and 'style_weight' in info.data and 'grammar_weight' in info.data:
            total = info.data['style_weight'] + info.data['grammar_weight'] + v
            if abs(total - 1.0) > 0.001:  # Allow small floating point errors
                raise ValueError("Weights must sum to 1.0")
        return v


class ReviewScore(BaseModel):
    """Model for review scores and feedback."""
    overall_score: float = Field(..., ge=0.0, le=100.0)
    style_score: float = Field(..., ge=0.0, le=100.0)
    grammar_score: float = Field(..., ge=0.0, le=100.0)
    purpose_score: float = Field(..., ge=0.0, le=100.0)
    detailed_feedback: Dict[str, List[str]] = Field(default_factory=dict)
    
    @field_validator('overall_score', 'style_score', 'grammar_score', 'purpose_score')
    @classmethod
    def validate_scores(cls, v):
        """Validate scores are between 0 and 100."""
        if not 0.0 <= v <= 100.0:
            raise ValueError("Score must be between 0.0 and 100.0")
        return v


class Review(BaseModel):
    """Review model for storing review reports and scores."""
    
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    article_id: PyObjectId
    version: int = Field(default=1, ge=1)
    purpose: str = Field(..., min_length=1)
    target_audience: Optional[str] = None
    review_config: ReviewConfig
    status: str = Field(..., pattern="^(pending|in_progress|completed|approved|failed)$")
    scores: Optional[ReviewScore] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    
    model_config = {
        'validate_by_name': True,
        'arbitrary_types_allowed': True
    }
    
    @field_validator('updated_at', mode='before')
    @classmethod
    def update_timestamp(cls, v):
        """Always update the timestamp."""
        return datetime.utcnow()
    
    def model_dump(self, **kwargs):
        """Override to handle ObjectId serialization."""
        data = super().model_dump(**kwargs)
        if self.id:
            data['_id'] = self.id
        if self.article_id:
            data['article_id'] = self.article_id
        return data
