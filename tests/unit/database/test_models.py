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