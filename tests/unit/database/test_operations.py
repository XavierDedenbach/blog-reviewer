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