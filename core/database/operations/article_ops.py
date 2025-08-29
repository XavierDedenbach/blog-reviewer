from typing import List, Optional, Dict, Any
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from core.database.models.article import Article


class ArticleOperations:
    """Database operations for Article model."""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.articles
    
    async def create(self, article: Article) -> Article:
        """Create a new article."""
        article_data = article.model_dump(exclude={'id'})
        result = await self.collection.insert_one(article_data)
        article.id = result.inserted_id
        return article
    
    async def get_by_id(self, article_id: ObjectId) -> Optional[Article]:
        """Get article by ID."""
        article_data = await self.collection.find_one({"_id": article_id})
        if article_data:
            return Article(**article_data)
        return None
    
    async def get_by_slug(self, slug: str) -> Optional[Article]:
        """Get article by slug."""
        article_data = await self.collection.find_one({"slug": slug})
        if article_data:
            return Article(**article_data)
        return None
    
    async def update(self, article_id: ObjectId, update_data: Dict[str, Any]) -> bool:
        """Update an article."""
        # Add updated_at timestamp
        from datetime import datetime
        update_data['updated_at'] = datetime.utcnow()
        
        result = await self.collection.update_one(
            {"_id": article_id},
            {"$set": update_data}
        )
        return result.modified_count > 0
    
    async def delete(self, article_id: ObjectId) -> bool:
        """Delete an article."""
        result = await self.collection.delete_one({"_id": article_id})
        return result.deleted_count > 0
    
    async def list(self, filters: Optional[Dict[str, Any]] = None, 
                   skip: int = 0, limit: int = 50, 
                   sort_by: str = "created_at", sort_order: int = -1) -> List[Article]:
        """List articles with optional filtering and pagination."""
        if filters is None:
            filters = {}
        
        cursor = self.collection.find(filters)
        cursor = cursor.skip(skip).limit(limit).sort(sort_by, sort_order)
        
        articles = []
        async for article_data in cursor:
            articles.append(Article(**article_data))
        
        return articles
    
    async def get_by_author(self, author_id: ObjectId) -> List[Article]:
        """Get all articles by a specific author."""
        cursor = self.collection.find({"author_id": author_id})
        articles = []
        async for article_data in cursor:
            articles.append(Article(**article_data))
        return articles
    
    async def get_by_type(self, article_type: str) -> List[Article]:
        """Get articles by type."""
        cursor = self.collection.find({"article_type": article_type})
        articles = []
        async for article_data in cursor:
            articles.append(Article(**article_data))
        return articles
    
    async def get_by_status(self, review_status: str) -> List[Article]:
        """Get articles by review status."""
        cursor = self.collection.find({"review_status": review_status})
        articles = []
        async for article_data in cursor:
            articles.append(Article(**article_data))
        return articles
    
    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count articles with optional filters."""
        if filters is None:
            filters = {}
        return await self.collection.count_documents(filters)
    
    async def search(self, search_term: str, limit: int = 20) -> List[Article]:
        """Search articles by title or content."""
        # Create text search query
        search_filter = {
            "$or": [
                {"title": {"$regex": search_term, "$options": "i"}},
                {"content": {"$regex": search_term, "$options": "i"}}
            ]
        }
        
        cursor = self.collection.find(search_filter).limit(limit)
        articles = []
        async for article_data in cursor:
            articles.append(Article(**article_data))
        return articles
