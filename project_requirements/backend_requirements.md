# Backend Requirements: AI Blog Reviewer

## Overview

This document outlines the backend requirements for the AI Blog Reviewer MVP, including API design, database schema, and system architecture.

## System Architecture

### Core Components
- **FastAPI Application**: Main API server
- **MongoDB Database**: Data persistence and storage
- **External APIs**: OpenRouter, Cohere (embeddings), Firecrawl (web scraping)
- **Docker Services**: Containerized deployment
- **CLI Interface**: Command-line tool for users

### Service Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   CLI Client    │    │   FastAPI App   │    │   MongoDB       │
│                 │◄──►│                 │◄──►│                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │  External APIs  │
                       │  - OpenRouter   │
                       │  - Cohere       │
                       │  - Firecrawl    │
                       └─────────────────┘
```

## API Design

### Core Endpoints

#### Review Management
```python
# Start new review
POST /api/v1/reviews
{
    "article_file": "path/to/article.md",
    "authors": ["author1", "author2"],
    "purpose": "educational"
}

# Get review status
GET /api/v1/reviews/{review_id}

# Approve review
PUT /api/v1/reviews/{review_id}/approve

# Get review report
GET /api/v1/reviews/{review_id}/report
```

#### Author Management
```python
# List available authors
GET /api/v1/authors

# Get author details
GET /api/v1/authors/{author_id}

# Add new author
POST /api/v1/authors
{
    "name": "author_name",
    "urls": ["url1", "url2"]
}

# Update author
PUT /api/v1/authors/{author_id}
```

#### System Management
```python
# Health check
GET /api/v1/health

# System status
GET /api/v1/status

# Configuration
GET /api/v1/config
```

### Response Formats

#### Standard Response
```python
{
    "success": bool,
    "data": object,
    "message": string,
    "timestamp": string,
    "request_id": string
}
```

#### Error Response
```python
{
    "success": false,
    "error": {
        "code": string,
        "message": string,
        "details": object
    },
    "timestamp": string,
    "request_id": string
}
```

## Database Schema

### Collections

#### Articles Collection
```python
{
    "_id": ObjectId,
    "author_id": ObjectId,
    "title": str,
    "slug": str,
    "content": str,
    "url": str,
    "article_type": str,        # "draft", "published", "reference", "review_example"
    "review_status": str,       # "pending", "in_progress", "completed", "approved", "released"
    "review_id": ObjectId,
    "version": int,
    "is_current": bool,
    "purpose": str,
    "word_count": int,
    "images": List[dict],
    "source": str,              # "scraped", "uploaded", "blog_review", "manual"
    "created_at": datetime,
    "updated_at": datetime
}
```

#### Authors Collection
```python
{
    "_id": ObjectId,
    "name": str,
    "bio": str,
    "author_type": str,         # "external" or "user"
    "style_profile": {
        "tone": str,
        "complexity": str,
        "writing_style": str
    },
    "total_articles": int,
    "created_at": datetime,
    "updated_at": datetime
}
```

#### Reviews Collection
```python
{
    "_id": ObjectId,
    "article_id": ObjectId,
    "version": int,
    "authors_used": List[ObjectId],
    "purpose_analysis": {
        "questions": List[str],
        "scores": List[float],
        "overall_score": float
    },
    "style_review": {
        "personas": List[str],
        "feedback": List[dict]
    },
    "grammar_review": {
        "issues_found": int,
        "suggestions": List[str]
    },
    "overall_score": float,
    "status": str,              # "pending", "completed", "approved"
    "created_at": datetime,
    "completed_at": datetime
}
```

## Core Services

### Review Service
```python
class ReviewService:
    async def start_review(self, article_file: str, authors: List[str], purpose: str) -> Review
    async def get_review_status(self, review_id: str) -> ReviewStatus
    async def approve_review(self, review_id: str) -> bool
    async def get_report(self, review_id: str) -> Report
```

### Author Service
```python
class AuthorService:
    async def validate_authors(self, authors: List[str]) -> List[Author]
    async def scrape_author_articles(self, author_name: str) -> List[Article]
    async def create_author_profile(self, author_name: str, articles: List[Article]) -> Author
    async def get_author_style(self, author_id: str) -> StyleProfile
```

### Analysis Service
```python
class AnalysisService:
    # Purpose Analysis (Step B)
    async def analyze_purpose(self, content: str, purpose: str, questions: List[str]) -> PurposeAnalysis
    
    # Style Review (Step C) - can run multiple authors in parallel
    async def review_style_single_author(self, content: str, author: Author) -> StyleReview
    async def review_style_parallel(self, content: str, authors: List[Author]) -> List[StyleReview]
    
    # Grammar Review (Step D)
    async def check_grammar(self, content: str) -> GrammarReview
    
    # Parallel execution orchestrator
    async def run_parallel_analysis(self, content: str, purpose_questions: List[str], authors: List[Author]) -> AnalysisResults
```

## Parallel Execution Strategy

### Independent Analysis Stages

The system supports running each analysis stage independently and in parallel:

#### 1. Purpose Analysis (Step B)
```python
# Runs independently after Step A completes
purpose_analysis = await analysis_service.analyze_purpose(
    content=article_content,
    purpose=article_purpose,
    questions=generated_questions
)
```

#### 2. Style Review (Step C) - Parallel Author Reviews
```python
# Can run multiple authors in parallel
style_reviews = await analysis_service.review_style_parallel(
    content=article_content,
    authors=selected_authors  # List of Author objects
)

# Or run individual authors independently
for author in authors:
    style_review = await analysis_service.review_style_single_author(
        content=article_content,
        author=author
    )
```

#### 3. Grammar Review (Step D)
```python
# Runs independently
grammar_review = await analysis_service.check_grammar(
    content=article_content
)
```

### Parallel Execution Orchestrator
```python
# Run all analysis stages in parallel after Step A
analysis_results = await analysis_service.run_parallel_analysis(
    content=article_content,
    purpose_questions=generated_questions,
    authors=selected_authors
)
```

### Benefits
- **Scalability**: Handle 1+ authors efficiently
- **Fault Tolerance**: If one author review fails, others continue
- **Performance**: Parallel execution reduces total review time
- **Flexibility**: Can add/remove authors without restarting entire process

### Review Workflow with Parallel Execution

```python
# Step A: Upload & Setup (sequential)
article = await article_service.upload_article(article_file, authors, purpose)
questions = await purpose_service.generate_questions(purpose)

# Step B, C, D: Parallel Analysis (all run simultaneously)
async with asyncio.TaskGroup() as tg:
    # Purpose Analysis (Step B)
    purpose_task = tg.create_task(
        analysis_service.analyze_purpose(content, purpose, questions)
    )
    
    # Style Review (Step C) - Multiple authors in parallel
    style_tasks = [
        tg.create_task(
            analysis_service.review_style_single_author(content, author)
        )
        for author in authors
    ]
    
    # Grammar Review (Step D)
    grammar_task = tg.create_task(
        analysis_service.check_grammar(content)
    )

# Compile results
purpose_analysis = purpose_task.result()
style_reviews = [task.result() for task in style_tasks]
grammar_review = grammar_task.result()

# Generate final report
report = await report_service.compile_report(
    purpose_analysis, style_reviews, grammar_review
)
```

### Managing Multiple Authors (1+ Authors)

For cases with many authors, the system can:

```python
# Option 1: Run all authors in parallel (if API limits allow)
style_reviews = await analysis_service.review_style_parallel(
    content=article_content,
    authors=all_authors  # Could be 6+ authors
)

# Option 2: Batch authors to respect API rate limits
async def review_style_batched(authors: List[Author], batch_size: int = 3):
    results = []
    for i in range(0, len(authors), batch_size):
        batch = authors[i:i + batch_size]
        batch_results = await analysis_service.review_style_parallel(
            content=article_content,
            authors=batch
        )
        results.extend(batch_results)
    return results

# Option 3: Individual author reviews with progress tracking
async def review_style_with_progress(authors: List[Author]):
    results = []
    for i, author in enumerate(authors):
        review = await analysis_service.review_style_single_author(
            content=article_content,
            author=author
        )
        results.append(review)
        # Update progress: (i + 1) / len(authors) * 100
    return results
```

## External API Integration

### OpenRouter API
```python
class OpenRouterClient:
    async def generate_questions(self, purpose: str) -> List[str]
    async def score_content(self, content: str, question: str) -> float
    async def analyze_style(self, content: str, author_style: str) -> StyleAnalysis
```

### Cohere API
```python
class CohereClient:
    async def generate_embeddings(self, text: str) -> List[float]
    async def compare_embeddings(self, text1: str, text2: str) -> float
```

### Firecrawl API
```python
class FirecrawlClient:
    async def scrape_article(self, url: str) -> Article
    async def extract_content(self, html: str) -> str
```

## Performance Requirements

### Response Times
- **API Endpoints**: < 500ms for simple operations
- **Review Processing**: < 15 minutes for complete review
- **Author Scraping**: < 10 minutes per author
- **Report Generation**: < 2 minutes

### Scalability
- **Concurrent Reviews**: Support 10+ simultaneous reviews
- **Database**: Handle 1,000+ reviews and 100+ authors
- **API Rate Limits**: Respect external API limits with basic queuing

### Reliability
- **Uptime**: 95% availability
- **Error Handling**: Graceful degradation for external API failures
- **Data Backup**: Weekly automated backups
- **Monitoring**: Basic logging and error tracking

## Security Requirements

### Authentication & Authorization
- **API Keys**: Secure API key management
- **Rate Limiting**: Basic rate limiting to prevent abuse
- **Input Validation**: Sanitize all user inputs
- **CORS**: Basic CORS configuration

### Data Protection
- **Encryption**: Basic encryption for sensitive data
- **Access Control**: Simple access control for system resources
- **Audit Logging**: Basic logging of system access
- **Compliance**: Basic data privacy practices

## Monitoring & Logging

### Application Monitoring
```python
# Basic logging configuration
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        },
    },
    "handlers": {
        "default": {
            "level": "INFO",
            "formatter": "standard",
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "": {
            "handlers": ["default"],
            "level": "INFO",
            "propagate": False
        }
    }
}
```

### Metrics Collection
- **Request Count**: Basic API endpoint usage
- **Response Times**: Simple performance tracking
- **Error Rates**: Basic error monitoring
- **Resource Usage**: Simple CPU and memory tracking

## Deployment

### Docker Configuration
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

### Environment Variables
```bash
# Database
MONGODB_URI=mongodb://localhost:27017

# API Keys
OPENROUTER_API_KEY=your_key
COHERE_API_KEY=your_key

# External Services
FIRECRAWL_SERVER=http://localhost:4000

# Application
APP_ENV=development
LOG_LEVEL=INFO
```

## Testing Strategy

### Unit Tests
- **Service Layer**: Test core business logic
- **API Endpoints**: Test basic request/response handling
- **Database Operations**: Test essential data persistence

### Integration Tests
- **External APIs**: Mock external service responses
- **End-to-End**: Basic review workflow testing
- **Performance**: Simple load testing

### Test Coverage
- **Target**: > 70% code coverage
- **Critical Paths**: 100% coverage for core functionality
- **Error Handling**: Basic error scenario testing
