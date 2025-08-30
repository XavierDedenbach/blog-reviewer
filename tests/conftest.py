"""
Pytest configuration and fixtures for Blog Reviewer tests.
"""

import pytest
import pytest_asyncio
import asyncio
import os
from datetime import datetime, UTC
from typing import AsyncGenerator, Generator
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

# Configure asyncio for pytest
pytest_plugins = ["pytest_asyncio"]





@pytest_asyncio.fixture(scope="session")
async def real_db_client() -> AsyncGenerator[AsyncIOMotorClient, None]:
    """Create a real database client for integration tests."""
    mongodb_uri = os.getenv("MONGODB_URI", "mongodb://admin:password123@localhost:27017/blog_reviewer?authSource=admin")
    client = AsyncIOMotorClient(mongodb_uri)
    
    # Test the connection
    await client.admin.command('ping')
    
    yield client
    
    # Cleanup
    client.close()


@pytest_asyncio.fixture(scope="function")
async def clean_real_db(real_db_client: AsyncIOMotorClient) -> AsyncGenerator[AsyncIOMotorClient, None]:
    """Provide a clean real database for integration tests."""
    db = real_db_client.blog_reviewer
    
    # Clear all collections before each test
    await db.articles.delete_many({})
    await db.authors.delete_many({})
    await db.reviews.delete_many({})
    
    yield db


@pytest.fixture
def sample_article_data() -> dict:
    """Sample article data for testing."""
    return {
        "title": "Test Article Title",
        "content": "This is a test article content with some sample text for testing purposes.",
        "article_type": "draft",
        "review_status": "pending",
        "purpose": "informational",
        "word_count": 15,
        "slug": "test-article-title",
        "source": "manual",
        "tags": ["test", "sample"],
        "metadata": {
            "reading_time": 2,
            "difficulty": "beginner"
        },
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC)
    }


@pytest.fixture
def sample_author_data() -> dict:
    """Sample author data for testing."""
    return {
        "name": "Test Author",
        "email": "test@example.com",
        "bio": "A test author for testing purposes",
        "expertise_areas": ["technology", "programming"],
        "writing_style": {
            "tone": "professional",
            "voice": "active",
            "sentence_structure": "varied"
        },
        "social_links": {
            "twitter": "https://twitter.com/testauthor",
            "linkedin": "https://linkedin.com/in/testauthor"
        },
        "total_articles": 0,
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC)
    }


@pytest.fixture
def sample_review_data() -> dict:
    """Sample review data for testing."""
    return {
        "version": 1,
        "purpose": "quality_assessment",
        "target_audience": "developers",
        "review_config": {
            "check_grammar": True,
            "check_style": True,
            "check_technical_accuracy": True,
            "max_score": 100
        },
        "status": "pending",
        "scores": None,
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
        "completed_at": None
    }


@pytest.fixture
def mock_object_id() -> str:
    """Mock ObjectId for testing."""
    return "507f1f77bcf86cd799439011"


# Environment variables for testing
@pytest.fixture(autouse=True)
def setup_test_env():
    """Set up test environment variables."""
    os.environ.setdefault("ENVIRONMENT", "test")
    os.environ.setdefault("MONGODB_URI", "mongodb://admin:password123@localhost:27017/blog_reviewer?authSource=admin")
    os.environ.setdefault("OPENROUTER_API_KEY", "test_key")
    os.environ.setdefault("CLAUDE_API_KEY", "test_key")
    os.environ.setdefault("GROQ_API_KEY", "test_key")
    yield
    # Clean up environment variables after test
    for key in ["ENVIRONMENT", "MONGODB_URI", "OPENROUTER_API_KEY", "CLAUDE_API_KEY", "GROQ_API_KEY"]:
        os.environ.pop(key, None)

