# API Specification: AI Blog Reviewer

## Overview

This document provides the API specification for the AI Blog Reviewer MVP, including all endpoints, request/response formats, and authentication methods.

## Base URL

```
http://localhost:8080/api/v1
```

## Authentication

### API Key Authentication
All API requests require an API key to be included in the request header:

```
Authorization: Bearer <api_key>
```

### API Key Management
- API keys are generated during system setup
- Keys are stored securely in the database
- Basic rate limiting is applied per API key

## Common Response Format

### Success Response
```json
{
  "success": true,
  "data": {},
  "message": "Operation completed successfully",
  "timestamp": "2024-01-01T00:00:00Z",
  "request_id": "req_123456789"
}
```

### Error Response
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input parameters",
    "details": {
      "field": "blog_file",
      "issue": "File not found"
    }
  },
  "timestamp": "2024-01-01T00:00:00Z",
  "request_id": "req_123456789"
}
```

## Error Codes

| Code | Description | HTTP Status |
|------|-------------|-------------|
| `VALIDATION_ERROR` | Invalid input parameters | 400 |
| `NOT_FOUND` | Resource not found | 404 |
| `UNAUTHORIZED` | Invalid or missing API key | 401 |
| `FORBIDDEN` | Insufficient permissions | 403 |
| `RATE_LIMITED` | Rate limit exceeded | 429 |
| `INTERNAL_ERROR` | Server error | 500 |
| `SERVICE_UNAVAILABLE` | External service unavailable | 503 |

## Endpoints

### Reviews

#### Start Review
```http
POST /reviews
```

**Request Body:**
```json
{
  "article_file": "path/to/article.md",
  "authors": ["author1", "author2"],
  "purpose": "educational"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "review_id": "rev_123456789",
    "article_id": "art_123456789",
    "status": "pending",
    "estimated_completion": "2024-01-01T01:00:00Z",
    "progress": {
      "setup": false,
      "purpose_analysis": false,
      "style_review": false,
      "grammar_review": false,
      "complete_report": false
    }
  },
  "message": "Review started successfully"
}
```

#### Get Review Status
```http
GET /reviews/{review_id}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "review_id": "rev_123456789",
    "title": "Example Blog Post",
    "status": "in_progress",
    "progress": {
      "setup": true,
      "purpose_analysis": true,
      "style_review": false,
      "grammar_review": false,
      "complete_report": false
    },
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:30:00Z",
    "estimated_completion": "2024-01-01T01:00:00Z"
  }
}
```

#### List Reviews
```http
GET /reviews?status=completed&limit=10&offset=0
```

**Query Parameters:**
- `status`: Filter by status (pending, in_progress, completed, approved, failed)
- `limit`: Number of reviews to return (default: 20, max: 50)
- `offset`: Number of reviews to skip (default: 0)

**Response:**
```json
{
  "success": true,
  "data": {
    "reviews": [
      {
        "review_id": "rev_123456789",
        "title": "Example Blog Post",
        "status": "completed",
        "created_at": "2024-01-01T00:00:00Z",
        "completed_at": "2024-01-01T01:00:00Z"
      }
    ],
    "pagination": {
      "total": 50,
      "limit": 10,
      "offset": 0,
      "has_more": true
    }
  }
}
```

#### Get Review Report
```http
GET /reviews/{review_id}/report
```

**Response:**
```json
{
  "success": true,
  "data": {
    "review_id": "rev_123456789",
    "title": "Example Blog Post",
    "purpose_analysis": {
      "questions": [
        "Does the article clearly explain the main concept?",
        "Are practical examples provided?"
      ],
      "scores": [8.5, 7.2],
      "overall_score": 7.85
    },
    "style_review": {
      "personas": ["Packy Mckormic", "Edward Tufte"],
      "feedback": [
        {
          "persona": "Packy Mckormic",
          "rating": 7.5,
          "comments": "Good storytelling but could use more concrete examples"
        }
      ]
    },
    "grammar_review": {
      "issues_found": 5,
      "suggestions": [
        "Consider using active voice in paragraph 3",
        "Fix subject-verb agreement in sentence 12"
      ]
    },
    "recommendations": [
      "Add more specific examples to support main arguments",
      "Consider restructuring the conclusion for better flow"
    ]
  }
}
```

#### Approve Review
```http
PUT /reviews/{review_id}/approve
```

**Request Body:**
```json
{
  "approved": true,
  "comments": "Great feedback, will implement suggestions"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "review_id": "rev_123456789",
    "status": "approved",
    "approved_at": "2024-01-01T01:30:00Z",
    "approved_by": "user@example.com"
  },
  "message": "Review approved successfully"
}
```

#### Cancel Review
```http
DELETE /reviews/{review_id}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "review_id": "rev_123456789",
    "status": "cancelled",
    "cancelled_at": "2024-01-01T00:45:00Z"
  },
  "message": "Review cancelled successfully"
}
```

### Authors

#### List Authors
```http
GET /authors?limit=20&offset=0
```

**Query Parameters:**
- `limit`: Number of authors to return (default: 20, max: 50)
- `offset`: Number of authors to skip (default: 0)
- `search`: Search by author name

**Response:**
```json
{
  "success": true,
  "data": {
    "authors": [
      {
        "author_id": "auth_123456789",
        "name": "Packy McCormick",
        "author_type": "external",
        "total_articles": 15,
        "created_at": "2024-01-01T00:00:00Z",
        "style_profile": {
          "tone": "conversational",
          "complexity": "medium"
        }
      }
    ],
    "pagination": {
      "total": 25,
      "limit": 20,
      "offset": 0,
      "has_more": true
    }
  }
}
```

#### Get Author Details
```http
GET /authors/{author_id}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "author_id": "auth_123456789",
    "name": "Packy McCormick",
    "author_type": "external",
    "bio": "Author bio",
    "total_articles": 15,
    "created_at": "2024-01-01T00:00:00Z",
    "style_profile": {
      "tone": "conversational",
      "complexity": "medium",
      "writing_style": "narrative"
    }
  }
}
```

#### Add Author
```http
POST /authors
```

**Request Body:**
```json
{
  "name": "New Author",
  "author_type": "external",
  "urls": [
    "https://example.com/author1",
    "https://example.com/author2"
  ],
  "max_articles": 20
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "author_id": "auth_987654321",
    "name": "New Author",
    "status": "scraping",
    "articles_scraped": 0,
    "estimated_completion": "2024-01-01T00:05:00Z"
  },
  "message": "Author added and scraping started"
}
```

#### Update Author
```http
PUT /authors/{author_id}
```

**Request Body:**
```json
{
  "urls": [
    "https://example.com/author1",
    "https://example.com/author2",
    "https://example.com/author3"
  ],
  "rescraper": true
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "author_id": "auth_123456789",
    "status": "updating",
    "articles_scraped": 0,
    "estimated_completion": "2024-01-01T00:05:00Z"
  },
  "message": "Author update started"
}
```

#### Delete Author
```http
DELETE /authors/{author_id}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "author_id": "auth_123456789",
    "deleted_at": "2024-01-01T00:00:00Z"
  },
  "message": "Author deleted successfully"
}
```

### System

#### Health Check
```http
GET /health
```

**Response:**
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "timestamp": "2024-01-01T00:00:00Z",
    "version": "1.0.0",
    "services": {
      "database": "healthy",
      "openrouter": "healthy",
      "cohere": "healthy",
      "firecrawl": "healthy"
    }
  }
}
```

#### System Status
```http
GET /status
```

**Response:**
```json
{
  "success": true,
  "data": {
    "system": {
      "uptime": "24h 30m 15s",
      "version": "1.0.0",
      "environment": "production"
    },
    "performance": {
      "active_reviews": 5,
      "completed_today": 12,
      "avg_response_time": "500ms",
      "error_rate": "1%"
    },
    "resources": {
      "cpu_usage": "45%",
      "memory_usage": "60%",
      "disk_usage": "30%"
    }
  }
}
```

#### Configuration
```http
GET /config
```

**Response:**
```json
{
  "success": true,
  "data": {
    "api": {
      "openrouter_enabled": true,
      "cohere_enabled": true,
      "firecrawl_enabled": true
    },
    "limits": {
      "max_concurrent_reviews": 10,
      "max_authors_per_review": 5,
      "max_articles_per_author": 20
    },
    "defaults": {
      "default_purpose": "educational",
      "default_authors": ["author1", "author2"]
    }
  }
}
```

## Rate Limiting

### Limits
- **Standard**: 50 requests per minute
- **Burst**: 100 requests per minute
- **Review Creation**: 5 reviews per hour
- **Author Scraping**: 3 authors per hour

### Headers
```
X-RateLimit-Limit: 50
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1640995200
```

## Webhooks

### Review Status Updates
```http
POST /webhooks/review-update
```

**Headers:**
```
X-Webhook-Signature: sha256=...
```

**Request Body:**
```json
{
  "event": "review.completed",
  "review_id": "rev_123456789",
  "status": "completed",
  "timestamp": "2024-01-01T01:00:00Z",
  "data": {
    "title": "Example Blog Post",
    "overall_score": 7.85
  }
}
```

### Webhook Events
- `review.started`: Review process started
- `review.setup_completed`: Article setup completed
- `review.analysis_completed`: Analysis phase completed
- `review.completed`: Review fully completed
- `review.failed`: Review failed
- `author.scraping_completed`: Author article scraping completed

## File Upload

### Upload Article File
```http
POST /uploads/article
Content-Type: multipart/form-data
```

**Form Data:**
- `file`: Article file (markdown, txt, docx)
- `title`: Article title (optional)
- `version`: Version number (optional)

**Response:**
```json
{
  "success": true,
  "data": {
    "file_id": "file_123456789",
    "filename": "article-post.md",
    "size": 15420,
    "uploaded_at": "2024-01-01T00:00:00Z",
    "content_preview": "This is the beginning of the article..."
  }
}
```

## Streaming Responses

### Review Progress Stream
```http
GET /reviews/{review_id}/stream
```

**Response (Server-Sent Events):**
```
event: progress
data: {"phase": "purpose_analysis", "progress": 75}

event: status
data: {"status": "in_progress", "phase": "style_review"}

event: complete
data: {"status": "completed", "overall_score": 7.85}
```

## SDK Examples

### Python SDK
```python
from blog_reviewer import BlogReviewer

client = BlogReviewer(api_key="your_api_key")

# Start a review
review = client.start_review(
    article_file="path/to/article.md",
    authors=["author1", "author2"],
    purpose="educational"
)

# Check status
status = client.get_review_status(review.id)

# Get report
report = client.get_report(review.id)
```

### JavaScript SDK
```javascript
import { BlogReviewer } from '@blog-reviewer/sdk';

const client = new BlogReviewer({ apiKey: 'your_api_key' });

// Start a review
const review = await client.startReview({
  articleFile: 'path/to/article.md',
  authors: ['author1', 'author2'],
  purpose: 'educational'
});

// Check status
const status = await client.getReviewStatus(review.id);

// Get report
const report = await client.getReport(review.id);
```
