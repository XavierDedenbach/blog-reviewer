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
        data = super().model_dump(**kwargs)
        if self.id:
            data['_id'] = self.id
        return data
