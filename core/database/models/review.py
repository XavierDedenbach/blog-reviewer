<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> b2b58d2 (PR-002: Database Models and Core Operations (#9))
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
<<<<<<< HEAD
=======
"""
Review model for the Blog Reviewer system.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, UTC
from bson import ObjectId
from pydantic import BaseModel, Field, field_validator
from pydantic_core import core_schema


class PyObjectId:
    """Custom field for ObjectId validation."""
    
    @classmethod
    def _validate(cls, v, info):
        if isinstance(v, ObjectId):
            return v
        if isinstance(v, str):
            try:
                return ObjectId(v)
            except Exception:
                raise ValueError("Invalid ObjectId")
        raise ValueError("Invalid ObjectId")
    
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        return core_schema.with_info_plain_validator_function(
            cls._validate,
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda x: str(x) if x else None
            )
        )


class ReviewConfig(BaseModel):
    """Model for review configuration."""
    check_grammar: bool = Field(default=True, description="Check grammar")
    check_style: bool = Field(default=True, description="Check writing style")
    check_technical_accuracy: bool = Field(default=True, description="Check technical accuracy")
    check_readability: bool = Field(default=True, description="Check readability")
    max_score: int = Field(default=100, ge=1, le=100, description="Maximum score")


class ReviewScore(BaseModel):
    """Model for review scores."""
    overall_score: float = Field(..., ge=0, le=100, description="Overall review score")
    grammar_score: Optional[float] = Field(None, ge=0, le=100, description="Grammar score")
    style_score: Optional[float] = Field(None, ge=0, le=100, description="Style score")
    technical_score: Optional[float] = Field(None, ge=0, le=100, description="Technical accuracy score")
    readability_score: Optional[float] = Field(None, ge=0, le=100, description="Readability score")
    feedback: List[str] = Field(default=[], description="Review feedback")
    suggestions: List[str] = Field(default=[], description="Improvement suggestions")


class Review(BaseModel):
    """Review model for article reviews."""
    
    id: Optional[PyObjectId] = Field(None, alias="_id", description="Review ID")
    article_id: PyObjectId = Field(..., description="Article being reviewed")
    version: int = Field(..., ge=1, description="Review version")
    purpose: str = Field(..., description="Review purpose")
    target_audience: str = Field(..., description="Target audience")
    review_config: ReviewConfig = Field(..., description="Review configuration")
    status: str = Field(..., description="Review status")
    scores: Optional[ReviewScore] = Field(None, description="Review scores")
    created_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(UTC), description="Creation timestamp")
    updated_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(UTC), description="Last update timestamp")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str}
    }
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        valid_statuses = ['pending', 'in_progress', 'completed', 'failed']
        if v not in valid_statuses:
            raise ValueError(f'Review status must be one of: {valid_statuses}')
        return v
    
    @field_validator('purpose')
    @classmethod
    def validate_purpose(cls, v):
        valid_purposes = ['quality_assessment', 'content_improvement', 'fact_checking', 'style_review']
        if v not in valid_purposes:
            raise ValueError(f'Review purpose must be one of: {valid_purposes}')
        return v
    
    @field_validator('target_audience')
    @classmethod
    def validate_target_audience(cls, v):
        valid_audiences = ['general', 'developers', 'managers', 'students', 'professionals']
        if v not in valid_audiences:
            raise ValueError(f'Target audience must be one of: {valid_audiences}')
        return v
    
    def model_dump(self, **kwargs):
        """Custom model dump to handle ObjectId properly."""
        data = super().model_dump(**kwargs)
        if self.id:
            data['_id'] = self.id
        # Ensure article_id is an ObjectId for MongoDB
        if self.article_id:
            data['article_id'] = self.article_id
        return data
    
    def model_dump_for_db(self, **kwargs):
        """Custom model dump for database operations that preserves ObjectIds."""
        data = self.model_dump(**kwargs)
        # Convert string ObjectIds back to ObjectId for MongoDB
        if isinstance(data.get('article_id'), str):
            data['article_id'] = ObjectId(data['article_id'])
        if isinstance(data.get('_id'), str):
            data['_id'] = ObjectId(data['_id'])
        return data


# Update the PyObjectId class to be available at module level
PyObjectId = PyObjectId
>>>>>>> 378fefe (Updated to include the scope of PR-01. All tests passed for PR-01 and PR-02. All mocking removed with a instantiated MongoDb instance)
=======
>>>>>>> b2b58d2 (PR-002: Database Models and Core Operations (#9))
