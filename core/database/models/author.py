<<<<<<< HEAD
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator, EmailStr
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


class WritingStyle(BaseModel):
    """Model for author writing style preferences."""
    tone: Optional[str] = Field(pattern="^(conversational|professional|technical|casual|formal)$")
    complexity: Optional[str] = Field(pattern="^(simple|intermediate|complex)$")
    typical_word_count: Optional[int] = Field(ge=100, le=10000)
    voice: Optional[str] = Field(pattern="^(active|passive|mixed)$")
    sentence_structure: Optional[str] = Field(pattern="^(simple|varied|complex)$")


class SocialLinks(BaseModel):
    """Model for author social media links."""
    twitter: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    website: Optional[str] = None
    blog: Optional[str] = None
    
    @field_validator('twitter', 'linkedin', 'github', 'website', 'blog')
    @classmethod
    def validate_urls(cls, v):
        """Validate URL format."""
        if v and not v.startswith(('http://', 'https://')):
            raise ValueError("URL must start with http:// or https://")
        return v


class Author(BaseModel):
    """Author model for storing author profiles."""
    
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    name: str = Field(..., min_length=1, max_length=200)
    email: EmailStr
    bio: Optional[str] = None
    expertise_areas: List[str] = Field(default_factory=list)
    writing_style: Optional[WritingStyle] = None
    social_links: Optional[SocialLinks] = None
    total_articles: int = Field(default=0, ge=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
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
=======
"""
Author model for the Blog Reviewer system.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, UTC
from bson import ObjectId
from pydantic import BaseModel, Field, field_validator, EmailStr
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


class WritingStyle(BaseModel):
    """Model for author's writing style."""
    tone: str = Field(..., description="Writing tone")
    voice: str = Field(..., description="Writing voice")
    sentence_structure: str = Field(..., description="Sentence structure preference")


class SocialLinks(BaseModel):
    """Model for author's social media links."""
    twitter: Optional[str] = Field(None, description="Twitter profile URL")
    linkedin: Optional[str] = Field(None, description="LinkedIn profile URL")
    github: Optional[str] = Field(None, description="GitHub profile URL")
    website: Optional[str] = Field(None, description="Personal website URL")


class Author(BaseModel):
    """Author model for blog writers."""
    
    id: Optional[PyObjectId] = Field(None, alias="_id", description="Author ID")
    name: str = Field(..., min_length=1, max_length=200, description="Author name")
    email: EmailStr = Field(..., description="Author email")
    bio: str = Field(..., min_length=1, max_length=1000, description="Author biography")
    expertise_areas: List[str] = Field(..., description="Areas of expertise")
    writing_style: WritingStyle = Field(..., description="Writing style preferences")
    social_links: Optional[SocialLinks] = Field(None, description="Social media links")
    total_articles: int = Field(default=0, ge=0, description="Total articles written")
    created_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(UTC), description="Creation timestamp")
    updated_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(UTC), description="Last update timestamp")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str}
    }
    
    @field_validator('expertise_areas')
    @classmethod
    def validate_expertise_areas(cls, v):
        if not v:
            raise ValueError("At least one expertise area is required")
        stripped_areas = [area.strip() for area in v if area.strip()]
        if not stripped_areas:
            raise ValueError("At least one expertise area is required")
        return stripped_areas
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError("Name cannot be empty")
        return v.strip()
    
    @field_validator('bio')
    @classmethod
    def validate_bio(cls, v):
        if not v or not v.strip():
            raise ValueError("Bio cannot be empty")
        return v.strip()
    
    def model_dump(self, **kwargs):
        """Custom model dump to handle ObjectId properly."""
>>>>>>> 378fefe (Updated to include the scope of PR-01. All tests passed for PR-01 and PR-02. All mocking removed with a instantiated MongoDb instance)
        data = super().model_dump(**kwargs)
        if self.id:
            data['_id'] = self.id
        return data
<<<<<<< HEAD
=======


# Update the PyObjectId class to be available at module level
PyObjectId = PyObjectId
>>>>>>> 378fefe (Updated to include the scope of PR-01. All tests passed for PR-01 and PR-02. All mocking removed with a instantiated MongoDb instance)
