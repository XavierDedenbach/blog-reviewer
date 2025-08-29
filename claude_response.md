# Claude Response for PR #9

## Requirements
```json
{
  "pr_title": "PR-002: Database Models and Core Operations",
  "description": "Implement MongoDB document models and basic CRUD operations for the Blog Reviewer system. This PR establishes the core data layer with proper validation, indexing, and database connection management.\n\n**Size**: ~350 lines | **Duration**: 2-3 days  \n**Agent**: mongodb-manager with strict TDD approach",
  "claude_command": {
    "command": "implement",
    "details": "model name corrected to claude-sonnet-4-20250514 - please retry"
  },
  "requirements": [
    {
      "type": "requirement",
      "requirement": "**Article Model**: Complete document model with validation",
      "priority": "normal",
      "source": "body"
    },
    {
      "type": "requirement",
      "requirement": "**Author Model**: Author profiles with style analysis",
      "priority": "normal",
      "source": "body"
    },
    {
      "type": "requirement",
      "requirement": "**Review Model**: Review workflow and scoring",
      "priority": "normal",
      "source": "body"
    },
    {
      "type": "requirement",
      "requirement": "Database connection management and configuration",
      "priority": "normal",
      "source": "body"
    },
    {
      "type": "requirement",
      "requirement": "Basic CRUD operations for each model",
      "priority": "normal",
      "source": "body"
    },
    {
      "type": "requirement",
      "requirement": "Performance indexes based on database_schema.md",
      "priority": "normal",
      "source": "body"
    },
    {
      "type": "requirement",
      "requirement": "Data validation schemas with proper error handling",
      "priority": "normal",
      "source": "body"
    },
    {
      "type": "test",
      "requirement": "Unit tests for all model operations",
      "priority": "high",
      "source": "body"
    },
    {
      "type": "test",
      "requirement": "Integration tests with real MongoDB instance",
      "priority": "high",
      "source": "body"
    },
    {
      "type": "test",
      "requirement": "Data validation and constraint enforcement tests",
      "priority": "high",
      "source": "body"
    },
    {
      "type": "test",
      "requirement": "Index usage and query performance tests",
      "priority": "high",
      "source": "body"
    },
    {
      "type": "requirement",
      "requirement": "Error handling for database failures",
      "priority": "normal",
      "source": "body"
    },
    {
      "type": "requirement",
      "requirement": "CRUD operations verification",
      "priority": "normal",
      "source": "body"
    },
    {
      "type": "test",
      "requirement": "Database operations atomicity tests",
      "priority": "high",
      "source": "body"
    }
  ],
  "summary": {
    "total": 14,
    "tasks": 0,
    "tests": 5,
    "other": 9
  },
  "test_required": true,
  "documentation_required": false,
  "priority": "normal"
}
```

## Claude Response
Based on the project context and requirements, I'll implement the database models and core operations using TDD approach. Let me start by analyzing the database schema and then create comprehensive tests followed by the implementation.

### FILES_TO_CREATE_OR_MODIFY

1. `core/database/__init__.py` - Database package initialization
2. `core/database/connection.py` - MongoDB connection management
3. `core/database/models/__init__.py` - Models package initialization
4. `core/database/models/base.py` - Base model with common functionality
5. `core/database/models/article.py` - Article document model
6. `core/database/models/author.py` - Author document model
7. `core/database/models/review.py` - Review document model
8. `core/database/operations/__init__.py` - Operations package initialization
9. `core/database/operations/article_ops.py` - Article CRUD operations
10. `core/database/operations/author_ops.py` - Author CRUD operations
11. `core/database/operations/review_ops.py` - Review CRUD operations
12. `tests/unit/database/test_models.py` - Unit tests for models
13. `tests/unit/database/test_operations.py` - Unit tests for operations
14. `tests/integration/test_database.py` - Integration tests
15. `conftest.py` - Test configuration and fixtures

### TEST_FILES

```python
# File: conftest.py
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
```

```python
# File: tests/unit/database/test_models.py
import pytest
from datetime import datetime
from bson import ObjectId
from pydantic import ValidationError

from core.database.models.article import Article, ArticleImage
from core.database.models.author import Author, WritingStyle, SocialLinks
from core.database.models.review import Review, ReviewConfig, ReviewScore


class TestArticleModel:
    """Test Article model validation and serialization."""
    
    def test_article_creation_with_valid_data(self, sample_article_data):
        """Test creating article with valid data."""
        article = Article(**sample_article_data)
        
        assert article.title == sample_article_data["title"]
        assert article.slug == sample_article_data["slug"]
        assert article.content == sample_article_data["content"]
        assert article.article_type == sample_article_data["article_type"]
        assert article.review_status == sample_article_data["review_status"]
        assert article.purpose == sample_article_data["purpose"]
        assert article.version == 1  # Default version
        assert article.is_current is True  # Default
        assert isinstance(article.created_at, datetime)
        assert isinstance(article.updated_at, datetime)
    
    def test_article_word_count_calculation(self, sample_article_data):
        """Test automatic word count calculation."""
        content = "This is a test with exactly ten words in it."
        sample_article_data["content"] = content
        
        article = Article(**sample_article_data)
        assert article.word_count == 10
    
    def test_article_invalid_type(self, sample_article_data):
        """Test validation error for invalid article type."""
        sample_article_data["article_type"] = "invalid_type"
        
        with pytest.raises(ValidationError) as exc_info:
            Article(**sample_article_data)
        
        assert "article_type" in str(exc_info.value)
    
    def test_article_invalid_review_status(self, sample_article_data):
        """Test validation error for invalid review status."""
        sample_article_data["review_status"] = "invalid_status"
        
        with pytest.raises(ValidationError) as exc_info:
            Article(**sample_article_data)
        
        assert "review_status" in str(exc_info.value)
    
    def test_article_with_images(self, sample_article_data):
        """Test article with image attachments."""
        images_data = [
            {
                "filename": "image1.jpg",
                "url": "https://example.com/image1.jpg",
                "alt_text": "Test image 1",
                "size": 1024
            },
            {
                "filename": "image2.png",
                "url": "https://example.com/image2.png",
                "alt_text": "Test image 2",
                "size": 2048
            }
        ]
        sample_article_data["images"] = images_data
        
        article = Article(**sample_article_data)
        assert len(article.images) == 2
        assert all(isinstance(img, ArticleImage) for img in article.images)
        assert article.images[0].filename == "image1.jpg"
        assert article.images[1].size == 2048
    
    def test_article_slug_generation(self, sample_article_data):
        """Test automatic slug generation from title."""
        sample_article_data["title"] = "This Is A Test Title!"
        del sample_article_data["slug"]  # Remove slug to test auto-generation
        
        article = Article(**sample_article_data)
        assert article.slug == "this-is-a-test-title"
    
    def test_article_to_dict(self, sample_article_data):
        """Test article serialization to dictionary."""
        article = Article(**sample_article_data)
        article_dict = article.model_dump()
        
        assert article_dict["title"] == sample_article_data["title"]
        assert "created_at" in article_dict
        assert "updated_at" in article_dict
        assert "word_count" in article_dict


class TestAuthorModel:
    """Test Author model validation and serialization."""
    
    def test_author_creation_with_valid_data(self, sample_author_data):
        """Test creating author with valid data."""
        author = Author(**sample_author_data)
        
        assert author.name == sample_author_data["name"]
        assert author.email == sample_author_data["email"]
        assert author.bio == sample_author_data["bio"]
        assert author.expertise_areas == sample_author_data["expertise_areas"]
        assert isinstance(author.writing_style, WritingStyle)
        assert isinstance(author.social_links, SocialLinks)
        assert isinstance(author.created_at, datetime)
        assert isinstance(author.updated_at, datetime)
    
    def test_author_email_validation(self, sample_author_data):
        """Test email format validation."""
        sample_author_data["email"] = "invalid_email"
        
        with pytest.raises(ValidationError) as exc_info:
            Author(**sample_author_data)
        
        assert "email" in str(exc_info.value)
    
    def test_author_writing_style_validation(self, sample_author_data):
        """Test writing style validation."""
        sample_author_data["writing_style"]["tone"] = "invalid_tone"
        
        with pytest.raises(ValidationError) as exc_info:
            Author(**sample_author_data)
        
        assert "tone" in str(exc_info.value)
    
    def test_author_optional_fields(self, sample_author_data):
        """Test author creation with minimal required fields."""
        minimal_data = {
            "name": sample_author_data["name"],
            "email": sample_author_data["email"]
        }
        
        author = Author(**minimal_data)
        assert author.name == minimal_data["name"]
        assert author.email == minimal_data["email"]
        assert author.bio is None
        assert author.expertise_areas == []
        assert author.writing_style is None
        assert author.social_links is None
    
    def test_writing_style_model(self):
        """Test WritingStyle model validation."""
        style_data = {
            "tone": "professional",
            "complexity": "intermediate",
            "typical_word_count": 1500,
            "voice": "active",
            "sentence_structure": "varied"
        }
        
        style = WritingStyle(**style_data)
        assert style.tone == "professional"
        assert style.complexity == "intermediate"
        assert style.typical_word_count == 1500
    
    def test_social_links_model(self):
        """Test SocialLinks model validation."""
        links_data = {
            "twitter": "https://twitter.com/user",
            "linkedin": "https://linkedin.com/in/user",
            "github": "https://github.com/user",
            "website": "https://example.com"
        }
        
        links = SocialLinks(**links_data)
        assert links.twitter == "https://twitter.com/user"
        assert links.linkedin == "https://linkedin.com/in/user"


class TestReviewModel:
    """Test Review model validation and serialization."""
    
    def test_review_creation_with_valid_data(self, sample_review_data, mock_object_id):
        """Test creating review with valid data."""
        sample_review_data["article_id"] = mock_object_id
        review = Review(**sample_review_data)
        
        assert review.article_id == mock_object_id
        assert review.purpose == sample_review_data["purpose"]
        assert review.target_audience == sample_review_data["target_audience"]
        assert isinstance(review.review_config, ReviewConfig)
        assert review.status == sample_review_data["status"]
        assert isinstance(review.created_at, datetime)
        assert isinstance(review.updated_at, datetime)
    
    def test_review_invalid_status(self, sample_review_data, mock_object_id):
        """Test validation error for invalid review status."""
        sample_review_data["article_id"] = mock_object_id
        sample_review_data["status"] = "invalid_status"
        
        with pytest.raises(ValidationError) as exc_info:
            Review(**sample_review_data)
        
        assert "status" in str(exc_info.value)
    
    def test_review_config_validation(self, sample_review_data, mock_object_id):
        """Test review configuration validation."""
        sample_review_data["article_id"] = mock_object_id
        
        # Test valid weights that sum to 1.0
        config_data = {
            "style_weight": 0.3,
            "grammar_weight": 0.3,
            "purpose_weight": 0.4
        }
        sample_review_data["review_config"] = config_data
        
        review = Review(**sample_review_data)
        assert review.review_config.style_weight == 0.3
        assert review.review_config.grammar_weight == 0.3
        assert review.review_config.purpose_weight == 0.4
    
    def test_review_config_weights_validation(self, sample_review_data, mock_object_id):
        """Test review config weights sum validation."""
        sample_review_data["article_id"] = mock_object_id
        
        # Test weights that don't sum to 1.0
        config_data = {
            "style_weight": 0.5,
            "grammar_weight": 0.5,
            "purpose_weight": 0.5  # Sum = 1.5, should fail
        }
        sample_review_data["review_config"] = config_data
        
        with pytest.raises(ValidationError):
            Review(**sample_review_data)
    
    def test_review_with_scores(self, sample_review_data, mock_object_id):
        """Test review with completed scores."""
        sample_review_data["article_id"] = mock_object_id
        
        scores_data = {
            "overall_score": 85.0,
            "style_score": 80.0,
            "grammar_score": 90.0,
            "purpose_score": 85.0,
            "detailed_feedback": {
                "strengths": ["Clear writing", "Good structure"],
                "areas_for_improvement": ["Add more examples"],
                "specific_suggestions": ["Consider adding section headers"]
            }
        }
        sample_review_data["scores"] = scores_data
        sample_review_data["status"] = "completed"
        
        review = Review(**sample_review_data)
        assert isinstance(review.scores, ReviewScore)
        assert review.scores.overall_score == 85.0
        assert len(review.scores.detailed_feedback["strengths"]) == 2
    
    def test_review_score_validation(self):
        """Test ReviewScore model validation."""
        score_data = {
            "overall_score": 85.0,
            "style_score": 80.0,
            "grammar_score": 90.0,
            "purpose_score": 85.0,
            "detailed_feedback": {
                "strengths": ["Clear writing"],
                "areas_for_improvement": ["Add examples"],
                "specific_suggestions": ["Use headers"]
            }
        }
        
        score = ReviewScore(**score_data)
        assert score.overall_score == 85.0
        assert score.style_score == 80.0
    
    def test_review_score_range_validation(self):
        """Test score range validation (0-100)."""
        score_data = {
            "overall_score": 150.0,  # Invalid: > 100
            "style_score": 80.0,
            "grammar_score": 90.0,
            "purpose_score": 85.0,
            "detailed_feedback": {}
        }
        
        with pytest.raises(ValidationError):
            ReviewScore(**score_data)
```

```python
# File: tests/unit/database/test_operations.py
import pytest
from datetime import datetime
from bson import ObjectId
from unittest.mock import AsyncMock, Mock, patch

from core.database.operations.article_ops import ArticleOperations
from core.database.operations.author_ops import AuthorOperations
from core.database.operations.review_ops import ReviewOperations
from core.database.models.article import Article
from core.database.models.author import Author
from core.database.models.review import Review


class TestArticleOperations:
    """Test article database operations."""
    
    @pytest.fixture
    def article_ops(self):
        """Create ArticleOperations instance with mocked database."""
        mock_db = AsyncMock()
        return ArticleOperations(mock_db)
    
    @pytest.mark.asyncio
    async def test_create_article(self, article_ops, sample_article_data):
        """Test creating a new article."""
        # Mock database insert
        mock_result = Mock()
        mock_result.inserted_id = ObjectId()
        article_ops.db.articles.insert_one = AsyncMock(return_value=mock_result)
        
        article = Article(**sample_article_data)
        created_article = await article_ops.create(article)
        
        assert created_article.id == mock_result.inserted_id
        article_ops.db.articles.insert_one.assert_called_once()
        
        # Verify the data passed to insert
        call_args = article_ops.db.articles.insert_one.call_args[0][0]
        assert call_args["title"] == sample_article_data["title"]
    
    @pytest.mark.asyncio
    async def test_get_article_by_id(self, article_ops, sample_article_data, mock_object_id):
        """Test retrieving article by ID."""
        # Mock database find
        article_data = sample_article_data.copy()
        article_data["_id"] = mock_object_id
        article_data["created_at"] = datetime.utcnow()
        article_data["updated_at"] = datetime.utcnow()
        article_data["word_count"] = 100
        
        article_ops.db.articles.find_one = AsyncMock(return_value=article_data)
        
        article = await article_ops.get_by_id(mock_object_id)
        
        assert article is not None
        assert article.id == mock_object_id
        assert article.title == sample_article_data["title"]
        article_ops.db.articles.find_one.assert_called_once_with({"_id": mock_object_id})
    
    @pytest.mark.asyncio
    async def test_get_article_not_found(self, article_ops, mock_object_id):
        """Test retrieving non-existent article."""
        article_ops.db.articles.find_one = AsyncMock(return_value=None)
        
        article = await article_ops.get_by_id(mock_object_id)
        
        assert article is None
        article_ops.db.articles.find_one.assert_called_once_with({"_id": mock_object_id})
    
    @pytest.mark.asyncio
    async def test_update_article(self, article_ops, mock_object_id):
        """Test updating an article."""
        update_data = {"title": "Updated Title", "content": "Updated content"}
        
        mock_result = Mock()
        mock_result.modified_count = 1
        article_ops.db.articles.update_one = AsyncMock(return_value=mock_result)
        
        result = await article_ops.update(mock_object_id, update_data)
        
        assert result is True
        article_ops.db.articles.update_one.assert_called_once()
        
        # Verify update query
        call_args = article_ops.db.articles.update_one.call_args
        assert call_args[0][0] == {"_id": mock_object_id}
        assert "$set" in call_args[0][1]
        assert call_args[0][1]["$set"]["title"] == "Updated Title"
    
    @pytest.mark.asyncio
    async def test_delete_article(self, article_ops, mock_object_id):
        """Test deleting an article."""
        mock_result = Mock()
        mock_result.deleted_count = 1
        article_ops.db.articles.delete_one = AsyncMock(return_value=mock_result)
        
        result = await article_ops.delete(mock_object_id)
        
        assert result is True
        article_ops.db.articles.delete_one.assert_called_once_with({"_id": mock_object_id})
    
    @pytest.mark.asyncio
    async def test_list_articles_with_filters(self, article_ops):
        """Test listing articles with filters."""
        # Mock database find
        mock_cursor = AsyncMock()
        mock_cursor.skip.return_value = mock_cursor
        mock_cursor.limit.return_value = mock_cursor
        mock_cursor.sort.return_value = mock_cursor
        mock_cursor.to_list.return_value = []
        
        article_ops.db.articles.find.return_value = mock_cursor
        
        filters = {"article_type": "draft", "review_status": "pending"}
        articles = await article_ops.list(filters=filters, skip=0, limit=10)
        
        assert articles == []
        article_ops.db.articles.find.assert_called_once_with(filters)
        mock_cursor.skip.assert_called_once_with(0)
        mock_cursor.limit.assert_called_once_with(10)
    
    @pytest.mark.asyncio
    async def test_get_articles_by_author(self, article_ops, mock_object_id):
        """Test retrieving articles by author ID."""
        mock_cursor = AsyncMock()
        mock_cursor.to_list.return_value = []
        article_ops.db.articles.find.return_value = mock_cursor
        
        articles = await article_ops.get_by_author(mock_object_id)
        
        assert articles == []
        article_ops.db.articles.find.assert_called_once_with({"author_id": mock_object_id})


class TestAuthorOperations:
    """Test author database operations."""
    
    @pytest.fixture
    def author_ops(self):
        """Create AuthorOperations instance with mocked database."""
        mock_db = AsyncMock()
        return AuthorOperations(mock_db)
    
    @pytest.mark.asyncio
    async def test_create_author(self, author_ops, sample_author_data):
        """Test creating a new author."""
        mock_result = Mock()
        mock_result.inserted_id = ObjectId()
        author_ops.db.authors.insert_one = AsyncMock(return_value=mock_result)
        
        author = Author(**sample_author_data)
        created_author = await author_ops.create(author)
        
        assert created_author.id == mock_result.inserted_id
        author_ops.db.authors.insert_one.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_author_by_email(self, author_ops, sample_author_data):
        """Test retrieving author by email."""
        author_data = sample_author_data.copy()
        author_data["_id"] = ObjectId()
        author_data["created_at"] = datetime.utcnow()
        author_data["updated_at"] = datetime.utcnow()
        
        author_ops.db.authors.find_one = AsyncMock(return_value=author_data)
        
        author = await author_ops.get_by_email(sample_author_data["email"])
        
        assert author is not None
        assert author.email == sample_author_data["email"]
        author_ops.db.authors.find_one.assert_called_once_with({"email": sample_author_data["email"]})
    
    @pytest.mark.asyncio
    async def test_get_authors_by_expertise(self, author_ops):
        """Test retrieving authors by expertise area."""
        mock_cursor = AsyncMock()
        mock_cursor.to_list.return_value = []
        author_ops.db.authors.find.return_value = mock_cursor
        
        authors = await author_ops.get_by_expertise("technology")
        
        assert authors == []
        author_ops.db.authors.find.assert_called_once_with({"expertise_areas": "technology"})


class TestReviewOperations:
    """Test review database operations."""
    
    @pytest.fixture
    def review_ops(self):
        """Create ReviewOperations instance with mocked database."""
        mock_db = AsyncMock()
        return ReviewOperations(mock_db)
    
    @pytest.mark.asyncio
    async def test_create_review(self, review_ops, sample_review_data, mock_object_id):
        """Test creating a new review."""
        sample_review_data["article_id"] = mock_object_id
        
        mock_result = Mock()
        mock_result.inserted_id = ObjectId()
        review_ops.db.reviews.insert_one = AsyncMock(return_value=mock_result)
        
        review = Review(**sample_review_data)
        created_review = await review_ops.create(review)
        
        assert created_review.id == mock_result.inserted_id
        review_ops.db.reviews.insert_one.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_reviews_by_article(self, review_ops, mock_object_id):
        """Test retrieving reviews by article ID."""
        mock_cursor = AsyncMock()
        mock_cursor.to_list.return_value = []
        review_ops.db.reviews.find.return_value = mock_cursor
        
        reviews = await review_ops.get_by_article(mock_object_id)
        
        assert reviews == []
        review_ops.db.reviews.find.assert_called_once_with({"article_id": mock_object_id})
    
    @pytest.mark.asyncio
    async def test_update_review_status(self, review_ops, mock_object_id):
        """Test updating review status."""
        mock_result = Mock()
        mock_result.modified_count = 1
        review_ops.db.reviews.update_one = AsyncMock(return_value=mock_result)
        
        result = await review_ops.update_status(mock_object_id, "completed")
        
        assert result is True
        review_ops.db.reviews.update_one.assert_called_once()
        
        # Verify update query
        call_args = review_ops.db.reviews.update_one.call_args
        assert call_args[0][0] == {"_id": mock_object_id}
        assert call_args[0][1]["$set"]["status"] == "completed"
```

```python
# File: tests/integration/test_database.py
import pytest
import pytest_asyncio
from datetime import datetime
from bson import ObjectId

from core.database.connection import DatabaseManager
from core.database.operations.article_ops import ArticleOperations
from core.database.operations.author_ops import AuthorOperations
from core.database.operations.review_ops import ReviewOperations
from core.database.models.article import Article
from core.database.models.author import Author
from core.database.models.review import Review


class TestDatabaseIntegration:
    """Integration tests with real MongoDB instance."""
    
    @pytest.fixture
    async def db_manager(self):
        """Create database manager for testing."""
        manager = DatabaseManager()
        await manager.connect(test_mode=True)
        yield manager
        await manager.disconnect()
    
    @pytest.fixture
    async def operations(self, db_manager, clean_db):
        """Create operation instances."""
        article_ops = ArticleOperations(clean_db)
        author_ops = AuthorOperations(clean_db)
        review_ops = ReviewOperations(clean_db)
        
        return {
            "articles": article_ops,
            "authors": author_ops,
            "reviews": review_ops
        }
    
    @pytest.mark.asyncio
    async def test_article_crud_operations(self, operations, sample_article_data):
        """Test complete article CRUD operations."""
        article_ops = operations["articles"]
        
        # Create article
        article = Article(**sample_article_data)
        created_article = await article_ops.create(article)
        
        assert created_article.id is not None
        assert created_article.title == sample_article_data["title"]
        
        # Read article
        retrieved_article = await article_ops.get_by_id(created_article.id)
        assert retrieved_article is not None
        assert retrieved_article.title == sample_article_data["title"]
        
        # Update article
        update_data = {"title": "Updated Title"}
        update_result = await article_ops.update(created_article.id, update_data)
        assert update_result is True
        
        # Verify update
        updated_article = await article_ops.get_by_id(created_article.id)
        assert updated_article.title == "Updated Title"
        
        # Delete article
        delete_result = await article_ops.delete(created_article.id)
        assert delete_result is True
        
        # Verify deletion
        deleted_article = await article_ops.get_by_id(created_article.id)
        assert deleted_article is None
    
    @pytest.mark.asyncio
    async def test_author_crud_operations(self, operations, sample_author_data):
        """Test complete author CRUD operations."""
        author_ops = operations["authors"]
        
        # Create author
        author = Author(**sample_author_data)
        created_author = await author_ops.create(author)
        
        assert created_author.id is not None
        assert created_author.email == sample_author_data["email"]
        
        # Read by ID
        retrieved_author = await author_ops.get_by_id(
