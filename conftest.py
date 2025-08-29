import asyncio
import pytest
import pytest_asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
import os
from typing import AsyncGenerator, Generator
from datetime import datetime

# Test database configuration
TEST_DATABASE_URL = os.getenv("TEST_MONGODB_URL", "mongodb://localhost:27017")
TEST_DATABASE_NAME = "blog_reviewer_test"


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_db_client() -> AsyncGenerator[AsyncIOMotorClient, None]:
    """Create test database client."""
    client = AsyncIOMotorClient(TEST_DATABASE_URL)
    yield client
    client.close()


@pytest.fixture(scope="session")
async def test_db(test_db_client: AsyncIOMotorClient):
    """Create test database."""
    db = test_db_client[TEST_DATABASE_NAME]
    yield db
    # Cleanup after all tests
    await test_db_client.drop_database(TEST_DATABASE_NAME)


@pytest.fixture
async def clean_db(test_db):
    """Clean database before each test."""
    # Drop all collections before test
    collections = await test_db.list_collection_names()
    for collection_name in collections:
        await test_db[collection_name].drop()
    
    yield test_db
    
    # Drop all collections after test
    collections = await test_db.list_collection_names()
    for collection_name in collections:
        await test_db[collection_name].drop()


@pytest.fixture
def sync_db_client() -> Generator[MongoClient, None, None]:
    """Create synchronous database client for index operations."""
    client = MongoClient(TEST_DATABASE_URL)
    yield client
    client.close()


@pytest.fixture
def sync_test_db(sync_db_client: MongoClient):
    """Create synchronous test database."""
    db = sync_db_client[TEST_DATABASE_NAME]
    yield db
    sync_db_client.drop_database(TEST_DATABASE_NAME)


@pytest.fixture
def sample_article_data():
    """Sample article data for testing."""
    return {
        "title": "Test Article",
        "slug": "test-article",
        "content": "This is a test article content with more than 100 words to test the word count validation. " * 10,
        "article_type": "draft",
        "review_status": "pending",
        "purpose": "educational",
        "tags": ["test", "article"],
        "metadata": {
            "source": "test",
            "language": "en"
        }
    }


@pytest.fixture
def sample_author_data():
    """Sample author data for testing."""
    return {
        "name": "Test Author",
        "email": "test@example.com",
        "bio": "A test author for testing purposes",
        "expertise_areas": ["technology", "programming"],
        "writing_style": {
            "tone": "professional",
            "complexity": "intermediate",
            "typical_word_count": 1500
        },
        "social_links": {
            "twitter": "https://twitter.com/testauthor",
            "linkedin": "https://linkedin.com/in/testauthor"
        }
    }


@pytest.fixture
def sample_review_data():
    """Sample review data for testing."""
    return {
        "purpose": "educational",
        "target_audience": "developers",
        "review_config": {
            "style_weight": 0.3,
            "grammar_weight": 0.3,
            "purpose_weight": 0.4
        },
        "status": "pending"
    }


@pytest.fixture
def mock_object_id():
    """Mock ObjectId for testing."""
    from bson import ObjectId
    return ObjectId()