"""
Simple integration tests for database operations.
"""

import pytest
import pytest_asyncio
from bson import ObjectId
from datetime import datetime

from core.database.models.article import Article
from core.database.models.author import Author
from core.database.models.review import Review
from core.database.operations.article_ops import ArticleOperations
from core.database.operations.author_ops import AuthorOperations
from core.database.operations.review_ops import ReviewOperations


@pytest_asyncio.fixture
async def db_client():
    """Create a database client for testing."""
    from motor.motor_asyncio import AsyncIOMotorClient
    import os
    
    # Use the main database for simple integration tests
    mongodb_uri = os.getenv("MONGODB_URI", "mongodb://admin:password123@localhost:27017/blog_reviewer")
    client = AsyncIOMotorClient(mongodb_uri)
    
    # Test the connection
    await client.admin.command('ping')
    
    yield client
    
    # Cleanup
    client.close()


@pytest_asyncio.fixture
async def clean_db(db_client):
    """Provide a clean database for integration tests."""
    db = db_client.blog_reviewer
    
    # Clear all collections before each test
    await db.articles.delete_many({})
    await db.authors.delete_many({})
    await db.reviews.delete_many({})
    
    yield db


class TestSimpleIntegration:
    """Simple integration tests."""
    
    @pytest_asyncio.fixture
    async def article_ops(self, clean_db):
        """Create ArticleOperations instance."""
        return ArticleOperations(clean_db)
    
    @pytest_asyncio.fixture
    async def author_ops(self, clean_db):
        """Create AuthorOperations instance."""
        return AuthorOperations(clean_db)
    
    @pytest_asyncio.fixture
    async def review_ops(self, clean_db):
        """Create ReviewOperations instance."""
        return ReviewOperations(clean_db)
    
    @pytest.mark.asyncio
    async def test_create_and_retrieve_article(self, article_ops):
        """Test creating and retrieving an article."""
        # Create article data
        article_data = {
            "title": "Integration Test Article",
            "content": "This is a test article for integration testing.",
            "article_type": "draft",
            "review_status": "pending",
            "purpose": "testing",
            "source": "manual"
        }
        
        # Create article
        article = Article(**article_data)
        created_article = await article_ops.create(article)
        
        # Verify article was created
        assert created_article.id is not None
        assert created_article.title == article_data["title"]
        assert created_article.slug == "integration-test-article"
        assert created_article.word_count == 8
        
        # Retrieve article by ID
        retrieved_article = await article_ops.get_by_id(created_article.id)
        assert retrieved_article is not None
        assert retrieved_article.title == article_data["title"]
        
        # Retrieve article by slug
        slug_article = await article_ops.get_by_slug(created_article.slug)
        assert slug_article is not None
        assert slug_article.id == created_article.id
    
    @pytest.mark.asyncio
    async def test_create_and_retrieve_author(self, author_ops):
        """Test creating and retrieving an author."""
        # Create author data
        author_data = {
            "name": "Integration Test Author",
            "email": "integration@test.com",
            "bio": "A test author for integration testing",
            "expertise_areas": ["testing", "integration"],
            "writing_style": {
                "tone": "professional",
                "voice": "active",
                "sentence_structure": "varied"
            }
        }
        
        # Create author
        author = Author(**author_data)
        created_author = await author_ops.create(author)
        
        # Verify author was created
        assert created_author.id is not None
        assert created_author.name == author_data["name"]
        assert created_author.email == author_data["email"]
        assert created_author.total_articles == 0
        
        # Retrieve author by ID
        retrieved_author = await author_ops.get_by_id(created_author.id)
        assert retrieved_author is not None
        assert retrieved_author.name == author_data["name"]
        
        # Retrieve author by email
        email_author = await author_ops.get_by_email(created_author.email)
        assert email_author is not None
        assert email_author.id == created_author.id
    
    @pytest.mark.asyncio
    async def test_create_and_retrieve_review(self, review_ops):
        """Test creating and retrieving a review."""
        # Create review data
        article_id = ObjectId()
        review_data = {
            "article_id": article_id,
            "version": 1,
            "purpose": "quality_assessment",
            "target_audience": "developers",
            "review_config": {
                "check_grammar": True,
                "check_style": True,
                "check_technical_accuracy": True,
                "max_score": 100
            },
            "status": "pending"
        }
        
        # Create review
        review = Review(**review_data)
        created_review = await review_ops.create(review)
        
        # Verify review was created
        assert created_review.id is not None
        assert created_review.article_id == article_id
        assert created_review.purpose == review_data["purpose"]
        assert created_review.status == review_data["status"]
        
        # Retrieve review by ID
        retrieved_review = await review_ops.get_by_id(created_review.id)
        assert retrieved_review is not None
        assert retrieved_review.article_id == article_id
        
        # Retrieve reviews by article
        article_reviews = await review_ops.get_by_article(article_id)
        assert len(article_reviews) == 1
        assert article_reviews[0].id == created_review.id
    
    @pytest.mark.asyncio
    async def test_update_operations(self, article_ops, author_ops):
        """Test update operations."""
        # Create article
        article_data = {
            "title": "Update Test Article",
            "content": "Original content",
            "article_type": "draft",
            "review_status": "pending",
            "purpose": "testing",
            "source": "manual"
        }
        article = Article(**article_data)
        created_article = await article_ops.create(article)
        
        # Update article
        update_success = await article_ops.update(
            created_article.id, 
            {"title": "Updated Title", "content": "Updated content"}
        )
        assert update_success is True
        
        # Verify update
        updated_article = await article_ops.get_by_id(created_article.id)
        assert updated_article.title == "Updated Title"
        assert updated_article.content == "Updated content"
        
        # Create author
        author_data = {
            "name": "Update Test Author",
            "email": "update@test.com",
            "bio": "Original bio",
            "expertise_areas": ["testing"],
            "writing_style": {
                "tone": "professional",
                "voice": "active",
                "sentence_structure": "varied"
            }
        }
        author = Author(**author_data)
        created_author = await author_ops.create(author)
        
        # Update author
        author_update_success = await author_ops.update(
            created_author.id,
            {"name": "Updated Author Name", "bio": "Updated bio"}
        )
        assert author_update_success is True
        
        # Verify author update
        updated_author = await author_ops.get_by_id(created_author.id)
        assert updated_author.name == "Updated Author Name"
        assert updated_author.bio == "Updated bio"
    
    @pytest.mark.asyncio
    async def test_delete_operations(self, article_ops, author_ops):
        """Test delete operations."""
        # Create article
        article_data = {
            "title": "Delete Test Article",
            "content": "Content to be deleted",
            "article_type": "draft",
            "review_status": "pending",
            "purpose": "testing",
            "source": "manual"
        }
        article = Article(**article_data)
        created_article = await article_ops.create(article)
        
        # Delete article
        delete_success = await article_ops.delete(created_article.id)
        assert delete_success is True
        
        # Verify deletion
        deleted_article = await article_ops.get_by_id(created_article.id)
        assert deleted_article is None
        
        # Create author
        author_data = {
            "name": "Delete Test Author",
            "email": "delete@test.com",
            "bio": "Bio to be deleted",
            "expertise_areas": ["testing"],
            "writing_style": {
                "tone": "professional",
                "voice": "active",
                "sentence_structure": "varied"
            }
        }
        author = Author(**author_data)
        created_author = await author_ops.create(author)
        
        # Delete author
        author_delete_success = await author_ops.delete(created_author.id)
        assert author_delete_success is True
        
        # Verify author deletion
        deleted_author = await author_ops.get_by_id(created_author.id)
        assert deleted_author is None
