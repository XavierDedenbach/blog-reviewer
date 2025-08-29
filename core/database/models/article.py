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
