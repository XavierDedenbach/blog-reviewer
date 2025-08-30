<<<<<<< HEAD
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


class ArticleImage(BaseModel):
    """Model for article image attachments."""
    filename: str
    url: str
    alt_text: Optional[str] = None
    caption: Optional[str] = None
    size: Optional[int] = None


class Article(BaseModel):
    """Article model for storing blog posts and content."""
    
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    author_id: Optional[PyObjectId] = None
    title: str = Field(..., min_length=1, max_length=500)
    slug: Optional[str] = None
    content: str = Field(..., min_length=1)
    url: Optional[str] = None
    article_type: str = Field(..., pattern="^(draft|published|reference|review_example)$")
    review_status: str = Field(..., pattern="^(pending|in_progress|completed|approved|released)$")
    review_id: Optional[PyObjectId] = None
    version: int = Field(default=1, ge=1)
    is_current: bool = Field(default=True)
    purpose: Optional[str] = None
    word_count: Optional[int] = None
    images: List[ArticleImage] = Field(default_factory=list)
    source: Optional[str] = Field(pattern="^(scraped|uploaded|blog_review|manual)$")
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    model_config = {
        'validate_by_name': True,
        'arbitrary_types_allowed': True
    }
    
    @field_validator('slug', mode='before')
    @classmethod
    def generate_slug(cls, v, info):
        """Generate slug from title if not provided."""
        if v is None and hasattr(info, 'data') and info.data and 'title' in info.data:
            # Convert title to slug format
            slug = info.data['title'].lower()
            # Replace spaces and special characters with hyphens
            import re
            slug = re.sub(r'[^\w\s-]', '', slug)
            slug = re.sub(r'[-\s]+', '-', slug)
            return slug.strip('-')
        return v
    
    @field_validator('word_count', mode='before')
    @classmethod
    def calculate_word_count(cls, v, info):
        """Calculate word count from content if not provided."""
        if v is None and hasattr(info, 'data') and info.data and 'content' in info.data:
            return len(info.data['content'].split())
        return v
    
    @field_validator('updated_at', mode='before')
    @classmethod
    def update_timestamp(cls, v):
        """Always update the timestamp."""
        return datetime.utcnow()
    
    def model_post_init(self, __context):
        """Post-initialization hook to set computed fields."""
        if self.word_count is None and self.content:
            self.word_count = len(self.content.split())
        if self.slug is None and self.title:
            import re
            slug = self.title.lower()
            slug = re.sub(r'[^\w\s-]', '', slug)
            slug = re.sub(r'[-\s]+', '-', slug)
            self.slug = slug.strip('-')
    
    def model_dump(self, **kwargs):
        """Override to handle ObjectId serialization."""
        data = super().model_dump(**kwargs)
        if self.id:
            data['_id'] = self.id
        if self.author_id:
            data['author_id'] = self.author_id
        if self.review_id:
            data['review_id'] = self.review_id
        return data
=======
"""
Article model for the Blog Reviewer system.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, UTC
from bson import ObjectId
from pydantic import BaseModel, Field, field_validator, model_validator
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


class ArticleImage(BaseModel):
    """Model for article images."""
    url: str = Field(..., description="Image URL")
    alt_text: Optional[str] = Field(None, description="Alt text for accessibility")
    caption: Optional[str] = Field(None, description="Image caption")


class Article(BaseModel):
    """Article model for blog content."""
    
    id: Optional[PyObjectId] = Field(None, alias="_id", description="Article ID")
    title: str = Field(..., min_length=1, max_length=500, description="Article title")
    content: str = Field(..., min_length=1, description="Article content")
    article_type: str = Field(..., description="Type of article")
    review_status: str = Field(..., description="Current review status")
    purpose: str = Field(..., description="Purpose of the article")
    word_count: Optional[int] = Field(None, description="Word count")
    slug: Optional[str] = Field(None, description="URL slug")
    images: Optional[List[ArticleImage]] = Field(default=[], description="Article images")
    source: str = Field(..., description="Source of the article")
    tags: Optional[List[str]] = Field(default=[], description="Article tags")
    metadata: Optional[Dict[str, Any]] = Field(default={}, description="Additional metadata")
    author_id: Optional[PyObjectId] = Field(None, description="Author ID")
    created_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(UTC), description="Creation timestamp")
    updated_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(UTC), description="Last update timestamp")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str}
    }
    
    @field_validator('article_type')
    @classmethod
    def validate_article_type(cls, v):
        valid_types = ['draft', 'published', 'archived']
        if v not in valid_types:
            raise ValueError(f'Article type must be one of: {valid_types}')
        return v
    
    @field_validator('review_status')
    @classmethod
    def validate_review_status(cls, v):
        valid_statuses = ['pending', 'in_progress', 'completed', 'failed']
        if v not in valid_statuses:
            raise ValueError(f'Review status must be one of: {valid_statuses}')
        return v
    
    @field_validator('title')
    @classmethod
    def validate_title(cls, v):
        if not v or not v.strip():
            raise ValueError("Title cannot be empty")
        return v.strip()
    
    @field_validator('content')
    @classmethod
    def validate_content(cls, v):
        if not v or not v.strip():
            raise ValueError("Content cannot be empty")
        return v.strip()
    
    @model_validator(mode='after')
    def compute_fields(self):
        """Compute slug and word count after validation."""
        if not self.slug:
            self.slug = self.title.lower().replace(' ', '-').replace('_', '-')
            # Remove special characters
            import re
            self.slug = re.sub(r'[^a-z0-9\-]', '', self.slug)
            # Remove trailing dashes
            self.slug = self.slug.strip('-')
        
        if not self.word_count:
            self.word_count = len(self.content.split())
        
        return self
    
    def model_dump(self, **kwargs):
        """Custom model dump to handle ObjectId properly."""
        data = super().model_dump(**kwargs)
        if self.id:
            data['_id'] = self.id
        return data


# Update the PyObjectId class to be available at module level
PyObjectId = PyObjectId
>>>>>>> 378fefe (Updated to include the scope of PR-01. All tests passed for PR-01 and PR-02. All mocking removed with a instantiated MongoDb instance)
