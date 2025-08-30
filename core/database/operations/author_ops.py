<<<<<<< HEAD
from typing import List, Optional, Dict, Any
from bson import ObjectId
=======
"""
Author database operations for the Blog Reviewer system.
"""

from typing import List, Optional, Dict, Any
from bson import ObjectId
from datetime import datetime, UTC
>>>>>>> 378fefe (Updated to include the scope of PR-01. All tests passed for PR-01 and PR-02. All mocking removed with a instantiated MongoDb instance)
from motor.motor_asyncio import AsyncIOMotorDatabase

from core.database.models.author import Author


class AuthorOperations:
    """Database operations for Author model."""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.authors
    
    async def create(self, author: Author) -> Author:
        """Create a new author."""
        author_data = author.model_dump(exclude={'id'})
        result = await self.collection.insert_one(author_data)
        author.id = result.inserted_id
        return author
    
    async def get_by_id(self, author_id: ObjectId) -> Optional[Author]:
        """Get author by ID."""
        author_data = await self.collection.find_one({"_id": author_id})
        if author_data:
            return Author(**author_data)
        return None
    
    async def get_by_email(self, email: str) -> Optional[Author]:
        """Get author by email."""
        author_data = await self.collection.find_one({"email": email})
        if author_data:
            return Author(**author_data)
        return None
    
    async def get_by_name(self, name: str) -> Optional[Author]:
        """Get author by name."""
        author_data = await self.collection.find_one({"name": name})
        if author_data:
            return Author(**author_data)
        return None
    
    async def update(self, author_id: ObjectId, update_data: Dict[str, Any]) -> bool:
        """Update an author."""
        # Add updated_at timestamp
<<<<<<< HEAD
        from datetime import datetime
        update_data['updated_at'] = datetime.utcnow()
=======
        update_data['updated_at'] = datetime.now(UTC)
>>>>>>> 378fefe (Updated to include the scope of PR-01. All tests passed for PR-01 and PR-02. All mocking removed with a instantiated MongoDb instance)
        
        result = await self.collection.update_one(
            {"_id": author_id},
            {"$set": update_data}
        )
        return result.modified_count > 0
    
    async def delete(self, author_id: ObjectId) -> bool:
        """Delete an author."""
        result = await self.collection.delete_one({"_id": author_id})
        return result.deleted_count > 0
    
<<<<<<< HEAD
    async def list(self, filters: Optional[Dict[str, Any]] = None,
                   skip: int = 0, limit: int = 50,
                   sort_by: str = "created_at", sort_order: int = -1) -> List[Author]:
        """List authors with optional filtering and pagination."""
        if filters is None:
            filters = {}
        
        cursor = self.collection.find(filters)
        cursor = cursor.skip(skip).limit(limit).sort(sort_by, sort_order)
=======
    async def list(self, skip: int = 0, limit: int = 50) -> List[Author]:
        """List authors with pagination."""
        cursor = self.collection.find().skip(skip).limit(limit).sort("created_at", -1)
>>>>>>> 378fefe (Updated to include the scope of PR-01. All tests passed for PR-01 and PR-02. All mocking removed with a instantiated MongoDb instance)
        
        authors = []
        async for author_data in cursor:
            authors.append(Author(**author_data))
<<<<<<< HEAD
        
=======
>>>>>>> 378fefe (Updated to include the scope of PR-01. All tests passed for PR-01 and PR-02. All mocking removed with a instantiated MongoDb instance)
        return authors
    
    async def get_by_expertise(self, expertise: str) -> List[Author]:
        """Get authors by expertise area."""
        cursor = self.collection.find({"expertise_areas": expertise})
        authors = []
        async for author_data in cursor:
            authors.append(Author(**author_data))
        return authors
    
    async def search(self, search_term: str, limit: int = 20) -> List[Author]:
        """Search authors by name or bio."""
        search_filter = {
            "$or": [
                {"name": {"$regex": search_term, "$options": "i"}},
                {"bio": {"$regex": search_term, "$options": "i"}}
            ]
        }
        
        cursor = self.collection.find(search_filter).limit(limit)
        authors = []
        async for author_data in cursor:
            authors.append(Author(**author_data))
        return authors
    
<<<<<<< HEAD
    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count authors with optional filters."""
        if filters is None:
            filters = {}
        return await self.collection.count_documents(filters)
    
    async def update_article_count(self, author_id: ObjectId, count: int) -> bool:
        """Update the total article count for an author."""
        result = await self.collection.update_one(
            {"_id": author_id},
            {"$set": {"total_articles": count, "updated_at": Author().updated_at}}
=======
    async def count(self) -> int:
        """Count total authors."""
        return await self.collection.count_documents({})
    
    async def update_article_count(self, author_id: ObjectId, count: int) -> bool:
        """Update author's article count."""
        result = await self.collection.update_one(
            {"_id": author_id},
            {"$set": {"total_articles": count, "updated_at": datetime.now(UTC)}}
>>>>>>> 378fefe (Updated to include the scope of PR-01. All tests passed for PR-01 and PR-02. All mocking removed with a instantiated MongoDb instance)
        )
        return result.modified_count > 0
