"""
Database connection module for MongoDB using Motor.
"""

import os
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase


class DatabaseConnection:
    """Database connection manager for MongoDB."""
    
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.db: Optional[AsyncIOMotorDatabase] = None
    
    async def connect(self) -> None:
        """Connect to MongoDB database."""
        uri = os.getenv('MONGODB_URI', 'mongodb://admin:password123@localhost:27017/blog_reviewer')
        
        self.client = AsyncIOMotorClient(uri)
        self.db = self.client.blog_reviewer
        
        # Test the connection
        await self.client.admin.command('ping')
    
    async def disconnect(self) -> None:
        """Disconnect from MongoDB database."""
        if self.client:
            self.client.close()
            self.client = None
            self.db = None
    
    def get_database(self) -> Optional[AsyncIOMotorDatabase]:
        """Get the database instance."""
        return self.db


# Global database connection instance
db_connection = DatabaseConnection()


async def get_database() -> AsyncIOMotorDatabase:
    """Get the database instance, connecting if necessary."""
    if not db_connection.db:
        await db_connection.connect()
    return db_connection.db
