<<<<<<< HEAD
from typing import List, Optional, Dict, Any
from bson import ObjectId
=======
"""
Review database operations for the Blog Reviewer system.
"""

from typing import List, Optional, Dict, Any
from bson import ObjectId
from datetime import datetime, UTC
>>>>>>> 378fefe (Updated to include the scope of PR-01. All tests passed for PR-01 and PR-02. All mocking removed with a instantiated MongoDb instance)
from motor.motor_asyncio import AsyncIOMotorDatabase

from core.database.models.review import Review


class ReviewOperations:
    """Database operations for Review model."""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.reviews
    
    async def create(self, review: Review) -> Review:
        """Create a new review."""
<<<<<<< HEAD
        review_data = review.model_dump(exclude={'id'})
=======
        review_data = review.model_dump_for_db(exclude={'id'})
>>>>>>> 378fefe (Updated to include the scope of PR-01. All tests passed for PR-01 and PR-02. All mocking removed with a instantiated MongoDb instance)
        result = await self.collection.insert_one(review_data)
        review.id = result.inserted_id
        return review
    
    async def get_by_id(self, review_id: ObjectId) -> Optional[Review]:
        """Get review by ID."""
        review_data = await self.collection.find_one({"_id": review_id})
        if review_data:
            return Review(**review_data)
        return None
    
    async def get_by_article(self, article_id: ObjectId) -> List[Review]:
<<<<<<< HEAD
        """Get all reviews for a specific article."""
        cursor = self.collection.find({"article_id": article_id})
=======
        """Get all reviews for an article."""
        cursor = self.collection.find({"article_id": article_id}).sort("version", -1)
>>>>>>> 378fefe (Updated to include the scope of PR-01. All tests passed for PR-01 and PR-02. All mocking removed with a instantiated MongoDb instance)
        reviews = []
        async for review_data in cursor:
            reviews.append(Review(**review_data))
        return reviews
    
    async def get_by_status(self, status: str) -> List[Review]:
        """Get reviews by status."""
<<<<<<< HEAD
        cursor = self.collection.find({"status": status})
=======
        cursor = self.collection.find({"status": status}).sort("created_at", -1)
>>>>>>> 378fefe (Updated to include the scope of PR-01. All tests passed for PR-01 and PR-02. All mocking removed with a instantiated MongoDb instance)
        reviews = []
        async for review_data in cursor:
            reviews.append(Review(**review_data))
        return reviews
    
    async def update(self, review_id: ObjectId, update_data: Dict[str, Any]) -> bool:
        """Update a review."""
        # Add updated_at timestamp
<<<<<<< HEAD
        from datetime import datetime
        update_data['updated_at'] = datetime.utcnow()
=======
        update_data['updated_at'] = datetime.now(UTC)
>>>>>>> 378fefe (Updated to include the scope of PR-01. All tests passed for PR-01 and PR-02. All mocking removed with a instantiated MongoDb instance)
        
        result = await self.collection.update_one(
            {"_id": review_id},
            {"$set": update_data}
        )
        return result.modified_count > 0
    
    async def update_status(self, review_id: ObjectId, status: str) -> bool:
        """Update review status."""
<<<<<<< HEAD
        from datetime import datetime
        update_data = {
            "status": status,
            "updated_at": datetime.utcnow()
        }
        
        # If status is completed, set completed_at timestamp
        if status == "completed":
            update_data["completed_at"] = datetime.utcnow()
=======
        update_data = {
            "status": status,
            "updated_at": datetime.now(UTC)
        }
        
        # If status is completed, add completed_at timestamp
        if status == "completed":
            update_data["completed_at"] = datetime.now(UTC)
>>>>>>> 378fefe (Updated to include the scope of PR-01. All tests passed for PR-01 and PR-02. All mocking removed with a instantiated MongoDb instance)
        
        result = await self.collection.update_one(
            {"_id": review_id},
            {"$set": update_data}
        )
        return result.modified_count > 0
    
    async def delete(self, review_id: ObjectId) -> bool:
        """Delete a review."""
        result = await self.collection.delete_one({"_id": review_id})
        return result.deleted_count > 0
    
<<<<<<< HEAD
    async def list(self, filters: Optional[Dict[str, Any]] = None,
                   skip: int = 0, limit: int = 50,
                   sort_by: str = "created_at", sort_order: int = -1) -> List[Review]:
        """List reviews with optional filtering and pagination."""
        if filters is None:
            filters = {}
        
        cursor = self.collection.find(filters)
        cursor = cursor.skip(skip).limit(limit).sort(sort_by, sort_order)
=======
    async def list(self, skip: int = 0, limit: int = 50) -> List[Review]:
        """List reviews with pagination."""
        cursor = self.collection.find().skip(skip).limit(limit).sort("created_at", -1)
>>>>>>> 378fefe (Updated to include the scope of PR-01. All tests passed for PR-01 and PR-02. All mocking removed with a instantiated MongoDb instance)
        
        reviews = []
        async for review_data in cursor:
            reviews.append(Review(**review_data))
<<<<<<< HEAD
        
=======
>>>>>>> 378fefe (Updated to include the scope of PR-01. All tests passed for PR-01 and PR-02. All mocking removed with a instantiated MongoDb instance)
        return reviews
    
    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count reviews with optional filters."""
        if filters is None:
            filters = {}
        return await self.collection.count_documents(filters)
    
    async def get_latest_by_article(self, article_id: ObjectId) -> Optional[Review]:
        """Get the latest review for an article."""
        review_data = await self.collection.find_one(
            {"article_id": article_id},
<<<<<<< HEAD
            sort=[("created_at", -1)]
=======
            sort=[("version", -1)]
>>>>>>> 378fefe (Updated to include the scope of PR-01. All tests passed for PR-01 and PR-02. All mocking removed with a instantiated MongoDb instance)
        )
        if review_data:
            return Review(**review_data)
        return None
    
    async def get_by_purpose(self, purpose: str) -> List[Review]:
        """Get reviews by purpose."""
<<<<<<< HEAD
        cursor = self.collection.find({"purpose": purpose})
=======
        cursor = self.collection.find({"purpose": purpose}).sort("created_at", -1)
>>>>>>> 378fefe (Updated to include the scope of PR-01. All tests passed for PR-01 and PR-02. All mocking removed with a instantiated MongoDb instance)
        reviews = []
        async for review_data in cursor:
            reviews.append(Review(**review_data))
        return reviews
