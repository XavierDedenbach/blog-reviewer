"""
Integration tests for database operations.
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


class TestArticleOperations:
    """Test article database operations."""
    
    @pytest_asyncio.fixture
    async def article_ops(self, clean_real_db):
        """Create ArticleOperations instance."""
        return ArticleOperations(clean_real_db)
    
    @pytest.mark.asyncio
    async def test_create_article(self, article_ops, sample_article_data):
        """Test creating a new article."""
        article = Article(**sample_article_data)
        created_article = await article_ops.create(article)
        
        assert created_article.id is not None
        assert created_article.title == sample_article_data["title"]
        assert created_article.content == sample_article_data["content"]
        assert created_article.slug == "test-article-title"
        assert created_article.word_count == 15
    
    @pytest.mark.asyncio
    async def test_get_article_by_id(self, article_ops, sample_article_data):
        """Test retrieving article by ID."""
        article = Article(**sample_article_data)
        created_article = await article_ops.create(article)
        
        retrieved_article = await article_ops.get_by_id(created_article.id)
        
        assert retrieved_article is not None
        assert retrieved_article.id == created_article.id
        assert retrieved_article.title == sample_article_data["title"]
    
    @pytest.mark.asyncio
    async def test_get_article_by_slug(self, article_ops, sample_article_data):
        """Test retrieving article by slug."""
        article = Article(**sample_article_data)
        created_article = await article_ops.create(article)
        
        retrieved_article = await article_ops.get_by_slug(created_article.slug)
        
        assert retrieved_article is not None
        assert retrieved_article.slug == created_article.slug
        assert retrieved_article.title == sample_article_data["title"]
    
    @pytest.mark.asyncio
    async def test_update_article(self, article_ops, sample_article_data):
        """Test updating an article."""
        article = Article(**sample_article_data)
        created_article = await article_ops.create(article)
        
        update_data = {"title": "Updated Title", "content": "Updated content"}
        success = await article_ops.update(created_article.id, update_data)
        
        assert success is True
        
        updated_article = await article_ops.get_by_id(created_article.id)
        assert updated_article.title == "Updated Title"
        assert updated_article.content == "Updated content"
    
    @pytest.mark.asyncio
    async def test_delete_article(self, article_ops, sample_article_data):
        """Test deleting an article."""
        article = Article(**sample_article_data)
        created_article = await article_ops.create(article)
        
        success = await article_ops.delete(created_article.id)
        assert success is True
        
        deleted_article = await article_ops.get_by_id(created_article.id)
        assert deleted_article is None
    
    @pytest.mark.asyncio
    async def test_list_articles(self, article_ops, sample_article_data):
        """Test listing articles."""
        # Create multiple articles
        for i in range(3):
            article_data = sample_article_data.copy()
            article_data["title"] = f"Article {i+1}"
            article_data["slug"] = f"article-{i+1}"
            article = Article(**article_data)
            await article_ops.create(article)
        
        articles = await article_ops.list()
        assert len(articles) == 3
    
    @pytest.mark.asyncio
    async def test_search_articles(self, article_ops, sample_article_data):
        """Test searching articles."""
        article = Article(**sample_article_data)
        await article_ops.create(article)
        
        search_results = await article_ops.search("test")
        assert len(search_results) >= 1
        assert any("test" in result.title.lower() for result in search_results)


class TestAuthorOperations:
    """Test author database operations."""
    
    @pytest_asyncio.fixture
    async def author_ops(self, clean_real_db):
        """Create AuthorOperations instance."""
        return AuthorOperations(clean_real_db)
    
    @pytest.mark.asyncio
    async def test_create_author(self, author_ops, sample_author_data):
        """Test creating a new author."""
        author = Author(**sample_author_data)
        created_author = await author_ops.create(author)
        
        assert created_author.id is not None
        assert created_author.name == sample_author_data["name"]
        assert created_author.email == sample_author_data["email"]
        assert created_author.total_articles == 0
    
    @pytest.mark.asyncio
    async def test_get_author_by_email(self, author_ops, sample_author_data):
        """Test retrieving author by email."""
        author = Author(**sample_author_data)
        created_author = await author_ops.create(author)
        
        retrieved_author = await author_ops.get_by_email(created_author.email)
        
        assert retrieved_author is not None
        assert retrieved_author.email == created_author.email
        assert retrieved_author.name == sample_author_data["name"]
    
    @pytest.mark.asyncio
    async def test_get_author_by_name(self, author_ops, sample_author_data):
        """Test retrieving author by name."""
        author = Author(**sample_author_data)
        created_author = await author_ops.create(author)
        
        retrieved_author = await author_ops.get_by_name(created_author.name)
        
        assert retrieved_author is not None
        assert retrieved_author.name == created_author.name
        assert retrieved_author.email == sample_author_data["email"]
    
    @pytest.mark.asyncio
    async def test_update_author(self, author_ops, sample_author_data):
        """Test updating an author."""
        author = Author(**sample_author_data)
        created_author = await author_ops.create(author)
        
        update_data = {"name": "Updated Name", "bio": "Updated bio"}
        success = await author_ops.update(created_author.id, update_data)
        
        assert success is True
        
        updated_author = await author_ops.get_by_id(created_author.id)
        assert updated_author.name == "Updated Name"
        assert updated_author.bio == "Updated bio"
    
    @pytest.mark.asyncio
    async def test_get_authors_by_expertise(self, author_ops, sample_author_data):
        """Test retrieving authors by expertise."""
        author = Author(**sample_author_data)
        await author_ops.create(author)
        
        authors = await author_ops.get_by_expertise("technology")
        assert len(authors) >= 1
        assert any("technology" in author.expertise_areas for author in authors)
    
    @pytest.mark.asyncio
    async def test_update_article_count(self, author_ops, sample_author_data):
        """Test updating author's article count."""
        author = Author(**sample_author_data)
        created_author = await author_ops.create(author)
        
        success = await author_ops.update_article_count(created_author.id, 5)
        assert success is True
        
        updated_author = await author_ops.get_by_id(created_author.id)
        assert updated_author.total_articles == 5


class TestReviewOperations:
    """Test review database operations."""
    
    @pytest_asyncio.fixture
    async def review_ops(self, clean_real_db):
        """Create ReviewOperations instance."""
        return ReviewOperations(clean_real_db)
    
    @pytest.fixture
    def sample_article_id(self):
        """Sample article ID for testing."""
        return ObjectId()
    
    @pytest.mark.asyncio
    async def test_create_review(self, review_ops, sample_review_data, sample_article_id):
        """Test creating a new review."""
        sample_review_data["article_id"] = sample_article_id
        review = Review(**sample_review_data)
        created_review = await review_ops.create(review)
        
        assert created_review.id is not None
        assert created_review.article_id == sample_article_id
        assert created_review.purpose == sample_review_data["purpose"]
        assert created_review.status == sample_review_data["status"]
    
    @pytest.mark.asyncio
    async def test_get_reviews_by_article(self, review_ops, sample_review_data, sample_article_id):
        """Test retrieving reviews by article."""
        # Create multiple reviews for the same article
        for i in range(2):
            review_data = sample_review_data.copy()
            review_data["article_id"] = sample_article_id
            review_data["version"] = i + 1
            review = Review(**review_data)
            await review_ops.create(review)
        
        reviews = await review_ops.get_by_article(sample_article_id)
        assert len(reviews) == 2
    
    @pytest.mark.asyncio
    async def test_update_review_status(self, review_ops, sample_review_data, sample_article_id):
        """Test updating review status."""
        sample_review_data["article_id"] = sample_article_id
        review = Review(**sample_review_data)
        created_review = await review_ops.create(review)
        
        success = await review_ops.update_status(created_review.id, "completed")
        assert success is True
        
        updated_review = await review_ops.get_by_id(created_review.id)
        assert updated_review.status == "completed"
        assert updated_review.completed_at is not None
    
    @pytest.mark.asyncio
    async def test_get_reviews_by_status(self, review_ops, sample_review_data, sample_article_id):
        """Test retrieving reviews by status."""
        # Create reviews with different statuses
        for status in ["pending", "in_progress", "completed"]:
            review_data = sample_review_data.copy()
            review_data["article_id"] = sample_article_id
            review_data["status"] = status
            review = Review(**review_data)
            await review_ops.create(review)
        
        pending_reviews = await review_ops.get_by_status("pending")
        assert len(pending_reviews) >= 1
        
        completed_reviews = await review_ops.get_by_status("completed")
        assert len(completed_reviews) >= 1
