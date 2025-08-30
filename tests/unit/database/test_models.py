<<<<<<< HEAD
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
=======
"""
Unit tests for database models.
"""

import pytest
from bson import ObjectId
from datetime import datetime

from core.database.models.article import Article, ArticleImage, PyObjectId as ArticlePyObjectId
from core.database.models.author import Author, WritingStyle, SocialLinks
from core.database.models.review import Review, ReviewConfig, ReviewScore, PyObjectId as ReviewPyObjectId


class TestPyObjectId:
    """Test PyObjectId custom field."""
    
    def test_pyobjectid_validation_string(self):
        """Test PyObjectId validation with string input."""
        valid_id = "507f1f77bcf86cd799439011"
        obj_id = ArticlePyObjectId._validate(valid_id, None)
        assert isinstance(obj_id, ObjectId)
        assert str(obj_id) == valid_id
    
    def test_pyobjectid_validation_objectid(self):
        """Test PyObjectId validation with ObjectId input."""
        original_id = ObjectId()
        obj_id = ArticlePyObjectId._validate(original_id, None)
        assert isinstance(obj_id, ObjectId)
        assert obj_id == original_id
    
    def test_pyobjectid_validation_invalid(self):
        """Test PyObjectId validation with invalid input."""
        with pytest.raises(ValueError, match="Invalid ObjectId"):
            ArticlePyObjectId._validate("invalid-id", None)
    
    def test_pyobjectid_validation_invalid_type(self):
        """Test PyObjectId validation with invalid type."""
        from pydantic import BaseModel, ValidationError
        
        class TestModel(BaseModel):
            id: ArticlePyObjectId
        
        with pytest.raises(ValidationError):
            TestModel(id=123)
    
    def test_pyobjectid_validation_with_info(self):
        """Test PyObjectId validation with info parameter."""
        # Test the _validate method directly with info parameter
        valid_id = "507f1f77bcf86cd799439011"
        obj_id = ArticlePyObjectId._validate(valid_id, None)
        assert isinstance(obj_id, ObjectId)
        assert str(obj_id) == valid_id
        
        # Test with ObjectId
        original_id = ObjectId()
        obj_id = ArticlePyObjectId._validate(original_id, None)
        assert obj_id == original_id
        
        # Test with invalid input
        with pytest.raises(ValueError, match="Invalid ObjectId"):
            ArticlePyObjectId._validate("invalid-id", None)
    
    def test_pyobjectid_validation_non_string_non_objectid(self):
        """Test PyObjectId validation with non-string, non-ObjectId types."""
        # Test with integer
        with pytest.raises(ValueError, match="Invalid ObjectId"):
            ArticlePyObjectId._validate(123, None)
        
        # Test with list
        with pytest.raises(ValueError, match="Invalid ObjectId"):
            ArticlePyObjectId._validate([], None)
        
        # Test with dict
        with pytest.raises(ValueError, match="Invalid ObjectId"):
            ArticlePyObjectId._validate({}, None)
        
        # Test with None
        with pytest.raises(ValueError, match="Invalid ObjectId"):
            ArticlePyObjectId._validate(None, None)
    
    def test_pyobjectid_validation_string_that_raises_exception(self):
        """Test PyObjectId validation with string that raises exception during ObjectId conversion."""
        # Test with a string that looks like an ObjectId but is invalid
        invalid_oid_string = "507f1f77bcf86cd79943901"  # Too short
        with pytest.raises(ValueError, match="Invalid ObjectId"):
            ArticlePyObjectId._validate(invalid_oid_string, None)
        
        # Test with a completely invalid string
        invalid_string = "not-an-object-id"
        with pytest.raises(ValueError, match="Invalid ObjectId"):
            ArticlePyObjectId._validate(invalid_string, None)
    
    def test_pyobjectid_serialization_schema(self):
        """Test PyObjectId serialization schema."""
        # Test that the schema is properly configured
        schema = ArticlePyObjectId.__get_pydantic_core_schema__(None, None)
        assert schema is not None
        # The schema structure is different in Pydantic v2, check for the function type
        assert schema.get('type') == 'function-plain'


class TestReviewPyObjectId:
    """Test Review module's PyObjectId custom field."""
    
    def test_review_pyobjectid_validation_string(self):
        """Test Review PyObjectId validation with string input."""
        valid_id = "507f1f77bcf86cd799439011"
        obj_id = ReviewPyObjectId._validate(valid_id, None)
        assert isinstance(obj_id, ObjectId)
        assert str(obj_id) == valid_id
    
    def test_review_pyobjectid_validation_objectid(self):
        """Test Review PyObjectId validation with ObjectId input."""
        original_id = ObjectId()
        obj_id = ReviewPyObjectId._validate(original_id, None)
        assert isinstance(obj_id, ObjectId)
        assert obj_id == original_id
    
    def test_review_pyobjectid_validation_invalid(self):
        """Test Review PyObjectId validation with invalid input."""
        with pytest.raises(ValueError, match="Invalid ObjectId"):
            ReviewPyObjectId._validate("invalid-id", None)
    
    def test_review_pyobjectid_validation_non_string_non_objectid(self):
        """Test Review PyObjectId validation with non-string, non-ObjectId types."""
        # Test with integer
        with pytest.raises(ValueError, match="Invalid ObjectId"):
            ReviewPyObjectId._validate(123, None)
        
        # Test with list
        with pytest.raises(ValueError, match="Invalid ObjectId"):
            ReviewPyObjectId._validate([], None)
        
        # Test with dict
        with pytest.raises(ValueError, match="Invalid ObjectId"):
            ReviewPyObjectId._validate({}, None)
        
        # Test with None
        with pytest.raises(ValueError, match="Invalid ObjectId"):
            ReviewPyObjectId._validate(None, None)
    
    def test_review_pyobjectid_validation_string_that_raises_exception(self):
        """Test Review PyObjectId validation with string that raises exception during ObjectId conversion."""
        # Test with a string that looks like an ObjectId but is invalid
        invalid_oid_string = "507f1f77bcf86cd79943901"  # Too short
        with pytest.raises(ValueError, match="Invalid ObjectId"):
            ReviewPyObjectId._validate(invalid_oid_string, None)
        
        # Test with a completely invalid string
        invalid_string = "not-an-object-id"
        with pytest.raises(ValueError, match="Invalid ObjectId"):
            ReviewPyObjectId._validate(invalid_string, None)
    
    def test_review_pyobjectid_serialization_schema(self):
        """Test Review PyObjectId serialization schema."""
        # Test that the schema is properly configured
        schema = ReviewPyObjectId.__get_pydantic_core_schema__(None, None)
        assert schema is not None
        # The schema structure is different in Pydantic v2, check for the function type
        assert schema.get('type') == 'function-plain'


class TestArticleModel:
    """Test Article model."""
    
    def test_create_article(self, sample_article_data):
        """Test creating an article."""
        article = Article(**sample_article_data)
        
        assert article.title == sample_article_data["title"]
>>>>>>> 378fefe (Updated to include the scope of PR-01. All tests passed for PR-01 and PR-02. All mocking removed with a instantiated MongoDb instance)
        assert article.content == sample_article_data["content"]
        assert article.article_type == sample_article_data["article_type"]
        assert article.review_status == sample_article_data["review_status"]
        assert article.purpose == sample_article_data["purpose"]
<<<<<<< HEAD
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
=======
        assert article.source == sample_article_data["source"]
        assert article.slug == "test-article-title"
        assert article.word_count == 15
    
    def test_article_with_images(self, sample_article_data):
        """Test article with images."""
        sample_article_data["images"] = [
            {
                "url": "https://example.com/image1.jpg",
                "alt_text": "Test image 1",
                "caption": "A test image"
            }
        ]
        
        article = Article(**sample_article_data)
        
        assert len(article.images) == 1
        assert article.images[0].url == "https://example.com/image1.jpg"
        assert article.images[0].alt_text == "Test image 1"
        assert article.images[0].caption == "A test image"
    
    def test_article_validation(self):
        """Test article validation."""
        # Test invalid article type
        with pytest.raises(ValueError):
            Article(
                title="Test",
                content="Test content",
                article_type="invalid",
                review_status="pending",
                purpose="test",
                source="manual"
            )
        
        # Test invalid review status
        with pytest.raises(ValueError):
            Article(
                title="Test",
                content="Test content",
                article_type="draft",
                review_status="invalid",
                purpose="test",
                source="manual"
            )
    
    def test_article_serialization(self, sample_article_data):
        """Test article serialization."""
        article = Article(**sample_article_data)
        data = article.model_dump()
        
        assert "_id" not in data  # Should not be in dump if id is None
        assert data["title"] == sample_article_data["title"]
        assert data["content"] == sample_article_data["content"]
    
    def test_article_serialization_with_id(self, sample_article_data):
        """Test article serialization with ID."""
        article = Article(**sample_article_data)
        article.id = ObjectId()
        data = article.model_dump()
        
        assert "_id" in data
        assert data["_id"] == article.id
    
    def test_article_title_validation_empty(self):
        """Test article title validation with empty title."""
        with pytest.raises(ValueError, match="Title cannot be empty"):
            Article(
                title="   ",
                content="Test content",
                article_type="draft",
                review_status="pending",
                purpose="test",
                source="manual"
            )
    
    def test_article_content_validation_empty(self):
        """Test article content validation with empty content."""
        with pytest.raises(ValueError, match="Content cannot be empty"):
            Article(
                title="Test Title",
                content="   ",
                article_type="draft",
                review_status="pending",
                purpose="test",
                source="manual"
            )
    
    def test_article_slug_generation_complex(self):
        """Test article slug generation with complex title."""
        article_data = {
            "title": "Complex Title with Special Characters! @#$%",
            "content": "Test content",
            "article_type": "draft",
            "review_status": "pending",
            "purpose": "test",
            "source": "manual"
        }
        article = Article(**article_data)
        assert article.slug == "complex-title-with-special-characters"
    
    def test_article_word_count_calculation(self):
        """Test article word count calculation."""
        article_data = {
            "title": "Test Title",
            "content": "This is a test article with multiple words for counting purposes.",
            "article_type": "draft",
            "review_status": "pending",
            "purpose": "test",
            "source": "manual"
        }
        article = Article(**article_data)
        assert article.word_count == 11
    
    def test_article_with_existing_slug_and_word_count(self):
        """Test article with pre-existing slug and word count."""
        article_data = {
            "title": "Test Title",
            "content": "Test content",
            "article_type": "draft",
            "review_status": "pending",
            "purpose": "test",
            "source": "manual",
            "slug": "custom-slug",
            "word_count": 999
        }
        article = Article(**article_data)
        assert article.slug == "custom-slug"
        assert article.word_count == 999


class TestAuthorModel:
    """Test Author model."""
    
    def test_create_author(self, sample_author_data):
        """Test creating an author."""
>>>>>>> 378fefe (Updated to include the scope of PR-01. All tests passed for PR-01 and PR-02. All mocking removed with a instantiated MongoDb instance)
        author = Author(**sample_author_data)
        
        assert author.name == sample_author_data["name"]
        assert author.email == sample_author_data["email"]
        assert author.bio == sample_author_data["bio"]
        assert author.expertise_areas == sample_author_data["expertise_areas"]
<<<<<<< HEAD
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
=======
        assert author.total_articles == 0
    
    def test_author_writing_style(self, sample_author_data):
        """Test author writing style."""
        author = Author(**sample_author_data)
        
        assert author.writing_style.tone == "professional"
        assert author.writing_style.voice == "active"
        assert author.writing_style.sentence_structure == "varied"
    
    def test_author_social_links(self, sample_author_data):
        """Test author social links."""
        author = Author(**sample_author_data)
        
        assert author.social_links.twitter == "https://twitter.com/testauthor"
        assert author.social_links.linkedin == "https://linkedin.com/in/testauthor"
    
    def test_author_validation(self):
        """Test author validation."""
        # Test invalid email
        with pytest.raises(ValueError):
            Author(
                name="Test Author",
                email="invalid-email",
                bio="Test bio",
                expertise_areas=["technology"],
                writing_style={
                    "tone": "professional",
                    "voice": "active",
                    "sentence_structure": "varied"
                }
            )
        
        # Test empty expertise areas
        with pytest.raises(ValueError):
            Author(
                name="Test Author",
                email="test@example.com",
                bio="Test bio",
                expertise_areas=[],
                writing_style={
                    "tone": "professional",
                    "voice": "active",
                    "sentence_structure": "varied"
                }
            )
    
    def test_author_serialization(self, sample_author_data):
        """Test author serialization."""
        author = Author(**sample_author_data)
        data = author.model_dump()
        
        assert "_id" not in data  # Should not be in dump if id is None
        assert data["name"] == sample_author_data["name"]
        assert data["email"] == sample_author_data["email"]
    
    def test_author_serialization_with_id(self, sample_author_data):
        """Test author serialization with ID."""
        author = Author(**sample_author_data)
        author.id = ObjectId()
        data = author.model_dump()
        
        assert "_id" in data
        assert data["_id"] == author.id
    
    def test_author_name_validation_empty(self):
        """Test author name validation with empty name."""
        with pytest.raises(ValueError, match="Name cannot be empty"):
            Author(
                name="   ",
                email="test@example.com",
                bio="Test bio",
                expertise_areas=["technology"],
                writing_style={
                    "tone": "professional",
                    "voice": "active",
                    "sentence_structure": "varied"
                }
            )
    
    def test_author_bio_validation_empty(self):
        """Test author bio validation with empty bio."""
        with pytest.raises(ValueError, match="Bio cannot be empty"):
            Author(
                name="Test Author",
                email="test@example.com",
                bio="   ",
                expertise_areas=["technology"],
                writing_style={
                    "tone": "professional",
                    "voice": "active",
                    "sentence_structure": "varied"
                }
            )
    
    def test_author_expertise_areas_validation_empty_items(self):
        """Test author expertise areas validation with empty items."""
        with pytest.raises(ValueError, match="At least one expertise area is required"):
            Author(
                name="Test Author",
                email="test@example.com",
                bio="Test bio",
                expertise_areas=["", "   ", ""],
                writing_style={
                    "tone": "professional",
                    "voice": "active",
                    "sentence_structure": "varied"
                }
            )
    
    def test_author_expertise_areas_validation_stripped(self):
        """Test author expertise areas validation with whitespace stripping."""
        author_data = {
            "name": "Test Author",
            "email": "test@example.com",
            "bio": "Test bio",
            "expertise_areas": ["  technology  ", "  programming  "],
            "writing_style": {
                "tone": "professional",
                "voice": "active",
                "sentence_structure": "varied"
            }
        }
        author = Author(**author_data)
        assert author.expertise_areas == ["technology", "programming"]


class TestReviewModel:
    """Test Review model."""
    
    def test_create_review(self, sample_review_data, mock_object_id):
        """Test creating a review."""
        sample_review_data["article_id"] = ObjectId(mock_object_id)
        
        review = Review(**sample_review_data)
        
        assert review.article_id == ObjectId(mock_object_id)
        assert review.version == sample_review_data["version"]
        assert review.purpose == sample_review_data["purpose"]
        assert review.target_audience == sample_review_data["target_audience"]
        assert review.status == sample_review_data["status"]
    
    def test_review_config(self, sample_review_data, mock_object_id):
        """Test review configuration."""
        sample_review_data["article_id"] = ObjectId(mock_object_id)
        
        review = Review(**sample_review_data)
        
        assert review.review_config.check_grammar is True
        assert review.review_config.check_style is True
        assert review.review_config.check_technical_accuracy is True
        assert review.review_config.max_score == 100
    
    def test_review_with_scores(self, sample_review_data, mock_object_id):
        """Test review with scores."""
        sample_review_data["article_id"] = ObjectId(mock_object_id)
        sample_review_data["scores"] = {
            "overall_score": 85.5,
            "grammar_score": 90.0,
            "style_score": 80.0,
            "technical_score": 85.0,
            "readability_score": 87.0,
            "feedback": ["Good content", "Minor grammar issues"],
            "suggestions": ["Consider shorter sentences", "Add more examples"]
        }
        
        review = Review(**sample_review_data)
        
        assert review.scores.overall_score == 85.5
        assert review.scores.grammar_score == 90.0
        assert len(review.scores.feedback) == 2
        assert len(review.scores.suggestions) == 2
    
    def test_review_validation(self, mock_object_id):
        """Test review validation."""
        # Test invalid purpose
        with pytest.raises(ValueError):
            Review(
                article_id=ObjectId(mock_object_id),
                purpose="invalid_purpose",
                target_audience="developers",
                review_config={
                    "check_grammar": True,
                    "check_style": True,
                    "check_technical_accuracy": True,
                    "max_score": 100
                },
                status="pending"
            )
        
        # Test invalid target audience
        with pytest.raises(ValueError):
            Review(
                article_id=ObjectId(mock_object_id),
                purpose="quality_assessment",
                target_audience="invalid_audience",
                review_config={
                    "check_grammar": True,
                    "check_style": True,
                    "check_technical_accuracy": True,
                    "max_score": 100
                },
                status="pending"
            )
    
    def test_review_serialization(self, sample_review_data, mock_object_id):
        """Test review serialization."""
        sample_review_data["article_id"] = ObjectId(mock_object_id)
        review = Review(**sample_review_data)
        data = review.model_dump()
        
        assert "_id" not in data  # Should not be in dump if id is None
        assert data["purpose"] == sample_review_data["purpose"]
        assert data["target_audience"] == sample_review_data["target_audience"]
    
    def test_review_serialization_with_id(self, sample_review_data, mock_object_id):
        """Test review serialization with ID."""
        sample_review_data["article_id"] = ObjectId(mock_object_id)
        review = Review(**sample_review_data)
        review.id = ObjectId()
        data = review.model_dump()
        
        assert "_id" in data
        assert data["_id"] == review.id
    
    def test_review_model_dump_for_db(self, sample_review_data, mock_object_id):
        """Test review model_dump_for_db method."""
        sample_review_data["article_id"] = ObjectId(mock_object_id)
        review = Review(**sample_review_data)
        review.id = ObjectId()
        
        # Test model_dump_for_db
        db_data = review.model_dump_for_db()
        assert db_data["_id"] == review.id
        assert db_data["article_id"] == review.article_id
    
    def test_review_model_dump_for_db_with_string_ids(self, sample_review_data, mock_object_id):
        """Test review model_dump_for_db with string ObjectIds."""
        review_data = {
            **sample_review_data,
            "id": str(ObjectId(mock_object_id)),
            "article_id": str(ObjectId(mock_object_id)),
            "version": 1
        }
        review = Review(**review_data)
        
        # Test model_dump_for_db converts string IDs to ObjectIds
        db_data = review.model_dump_for_db()
        assert isinstance(db_data["_id"], ObjectId)
        assert isinstance(db_data["article_id"], ObjectId)
    
    def test_review_model_dump_for_db_with_string_article_id_only(self, sample_review_data, mock_object_id):
        """Test review model_dump_for_db with only article_id as string."""
        review_data = {
            **sample_review_data,
            "article_id": str(ObjectId(mock_object_id)),
            "version": 1
        }
        review = Review(**review_data)
        
        # Test model_dump_for_db converts string article_id to ObjectId
        db_data = review.model_dump_for_db()
        assert isinstance(db_data["article_id"], ObjectId)
        assert db_data["article_id"] == ObjectId(mock_object_id)
    
    def test_review_model_dump_for_db_with_string_id_only(self, sample_review_data, mock_object_id):
        """Test review model_dump_for_db with only id as string."""
        review_data = {
            **sample_review_data,
            "id": str(ObjectId(mock_object_id)),
            "article_id": ObjectId(mock_object_id),
            "version": 1
        }
        review = Review(**review_data)
        
        # Test model_dump_for_db converts string id to ObjectId
        db_data = review.model_dump_for_db()
        assert isinstance(db_data["_id"], ObjectId)
        assert db_data["_id"] == ObjectId(mock_object_id)
    
    def test_review_model_dump_for_db_with_no_string_ids(self, sample_review_data, mock_object_id):
        """Test review model_dump_for_db with no string IDs (ObjectIds already)."""
        review_data = {
            **sample_review_data,
            "id": ObjectId(mock_object_id),
            "article_id": ObjectId(mock_object_id),
            "version": 1
        }
        review = Review(**review_data)
        
        # Test model_dump_for_db preserves ObjectIds
        db_data = review.model_dump_for_db()
        assert isinstance(db_data["_id"], ObjectId)
        assert isinstance(db_data["article_id"], ObjectId)
        assert db_data["_id"] == ObjectId(mock_object_id)
        assert db_data["article_id"] == ObjectId(mock_object_id)
    
    def test_review_model_dump_for_db_with_string_article_id_in_data(self, sample_review_data, mock_object_id, monkeypatch):
        """Test review model_dump_for_db when article_id becomes string in model_dump."""
        # Create a review with ObjectId
        review_data = {
            **sample_review_data,
            "article_id": ObjectId(mock_object_id),
            "version": 1
        }
        review = Review(**review_data)
        
        # Create modified data with string article_id
        original_data = review.model_dump()
        modified_data = original_data.copy()
        modified_data['article_id'] = str(modified_data['article_id'])
        
        # Use object.__setattr__ to bypass Pydantic's validation
        def mock_model_dump(**kwargs):
            return modified_data
        
        object.__setattr__(review, 'model_dump', mock_model_dump)
        
        # Test model_dump_for_db converts string back to ObjectId
        db_data = review.model_dump_for_db()
        assert isinstance(db_data["article_id"], ObjectId)
        assert db_data["article_id"] == ObjectId(mock_object_id)
    
    def test_review_model_dump_for_db_with_string_id_in_data(self, sample_review_data, mock_object_id, monkeypatch):
        """Test review model_dump_for_db when _id becomes string in model_dump."""
        # Create a review with ObjectId
        review_data = {
            **sample_review_data,
            "id": ObjectId(mock_object_id),
            "article_id": ObjectId(mock_object_id),
            "version": 1
        }
        review = Review(**review_data)
        
        # Create modified data with string _id
        original_data = review.model_dump()
        modified_data = original_data.copy()
        modified_data['_id'] = str(modified_data['_id'])
        
        # Use object.__setattr__ to bypass Pydantic's validation
        def mock_model_dump(**kwargs):
            return modified_data
        
        object.__setattr__(review, 'model_dump', mock_model_dump)
        
        # Test model_dump_for_db converts string back to ObjectId
        db_data = review.model_dump_for_db()
        assert isinstance(db_data["_id"], ObjectId)
        assert db_data["_id"] == ObjectId(mock_object_id)
    
    def test_review_purpose_validation_all_valid(self, mock_object_id):
        """Test review purpose validation with all valid purposes."""
        valid_purposes = ["quality_assessment", "content_improvement", "fact_checking", "style_review"]
        
        for purpose in valid_purposes:
            review = Review(
                article_id=ObjectId(mock_object_id),
                version=1,
                purpose=purpose,
                target_audience="developers",
                review_config={
                    "check_grammar": True,
                    "check_style": True,
                    "check_technical_accuracy": True,
                    "max_score": 100
                },
                status="pending"
            )
            assert review.purpose == purpose
    
    def test_review_target_audience_validation_all_valid(self, mock_object_id):
        """Test review target audience validation with all valid audiences."""
        valid_audiences = ["general", "developers", "managers", "students", "professionals"]
        
        for audience in valid_audiences:
            review = Review(
                article_id=ObjectId(mock_object_id),
                version=1,
                purpose="quality_assessment",
                target_audience=audience,
                review_config={
                    "check_grammar": True,
                    "check_style": True,
                    "check_technical_accuracy": True,
                    "max_score": 100
                },
                status="pending"
            )
            assert review.target_audience == audience


class TestNestedModels:
    """Test nested models."""
    
    def test_article_image_model(self):
        """Test ArticleImage model."""
        image_data = {
            "url": "https://example.com/image.jpg",
            "alt_text": "Test image",
            "caption": "A test image"
        }
        image = ArticleImage(**image_data)
        
        assert image.url == image_data["url"]
        assert image.alt_text == image_data["alt_text"]
        assert image.caption == image_data["caption"]
    
    def test_writing_style_model(self):
        """Test WritingStyle model."""
        style_data = {
            "tone": "casual",
            "voice": "passive",
            "sentence_structure": "simple"
        }
        style = WritingStyle(**style_data)
        
        assert style.tone == style_data["tone"]
        assert style.voice == style_data["voice"]
        assert style.sentence_structure == style_data["sentence_structure"]
    
    def test_social_links_model(self):
        """Test SocialLinks model."""
        social_data = {
            "twitter": "https://twitter.com/user",
            "linkedin": "https://linkedin.com/in/user",
            "github": "https://github.com/user",
            "website": "https://user.com"
        }
        social = SocialLinks(**social_data)
        
        assert social.twitter == social_data["twitter"]
        assert social.linkedin == social_data["linkedin"]
        assert social.github == social_data["github"]
        assert social.website == social_data["website"]
    
    def test_review_config_model(self):
        """Test ReviewConfig model."""
        config_data = {
            "check_grammar": False,
            "check_style": True,
            "check_technical_accuracy": False,
            "check_readability": True,
            "max_score": 50
        }
        config = ReviewConfig(**config_data)
        
        assert config.check_grammar is False
        assert config.check_style is True
        assert config.check_technical_accuracy is False
        assert config.check_readability is True
        assert config.max_score == 50
    
    def test_review_score_model(self):
        """Test ReviewScore model."""
        score_data = {
            "overall_score": 75.5,
            "grammar_score": 80.0,
            "style_score": 70.0,
            "technical_score": 85.0,
            "readability_score": 72.0,
            "feedback": ["Good overall", "Needs improvement"],
            "suggestions": ["Add more examples", "Simplify language"]
        }
        score = ReviewScore(**score_data)
        
        assert score.overall_score == 75.5
        assert score.grammar_score == 80.0
        assert score.style_score == 70.0
        assert score.technical_score == 85.0
        assert score.readability_score == 72.0
        assert len(score.feedback) == 2
        assert len(score.suggestions) == 2
>>>>>>> 378fefe (Updated to include the scope of PR-01. All tests passed for PR-01 and PR-02. All mocking removed with a instantiated MongoDb instance)
