# Database Schema: AI Blog Reviewer

## Overview

This document defines the complete database schema for the Blog Accelerator Agent, including all collections, indexes, and relationships.

## Database: `blog_reviewer`

### Collections Overview

| Collection | Purpose | Primary Key |
|------------|---------|-------------|
| `articles` | Store all articles (blogs, drafts, reference articles) | `_id` |
| `authors` | Store author profiles | `_id` |
| `reviews` | Store review reports and scores | `article_id` |

## Collection Schemas

### Articles Collection

**Purpose**: Store all articles (blogs, reference articles, drafts, published content)

```javascript
{
  "_id": ObjectId,
  "author_id": ObjectId,         // Reference to authors collection
  "title": String,               // Article title
  "slug": String,                // URL-friendly title (optional)
  "content": String,             // Article content
  "url": String,                 // Original URL (optional)
  "article_type": String,        // "draft", "published", "reference", "review_example"
  "review_status": String,       // "pending", "in_progress", "completed", "approved", "released"
  "review_id": ObjectId,         // Reference to reviews collection (if reviewed)
  "version": Number,             // Version number (1, 2, 3...)
  "is_current": Boolean,         // Is this the current version
  "purpose": String,             // Article purpose (for review requests)
  "word_count": Number,
  "images": [{
    "filename": String,          // Image filename
    "url": String,              // Image URL
    "alt_text": String,         // Alt text for accessibility
    "caption": String           // Image caption
  }],
  "source": String,              // "scraped", "uploaded", "blog_review", "manual"
  "created_at": Date,
  "updated_at": Date
}
```

**Indexes**:
```javascript
{ "_id": 1 }
{ "author_id": 1 }
{ "article_type": 1 }
{ "review_status": 1 }
{ "review_id": 1 }
{ "is_current": 1 }
{ "slug": 1 }
{ "created_at": -1 }
```

### Authors Collection

**Purpose**: Store author profiles

```javascript
{
  "_id": ObjectId,
  "name": String,                // Author name
  "bio": String,                 // Author biography
  "author_type": String,         // "external" (scraped) or "user" (you)
  "style_profile": {
    "tone": String,              // conversational, formal, technical
    "complexity": String,        // simple, medium, complex
    "writing_style": String      // narrative, analytical, list-based
  },
  "total_articles": Number,      // Number of articles (calculated)
  "created_at": Date,
  "updated_at": Date
}
```

**Indexes**:
```javascript
{ "_id": 1 }
{ "name": 1 }
{ "style_profile.tone": 1 }
```



### Reviews Collection

**Purpose**: Store review reports and scores

```javascript
{
  "_id": ObjectId,
  "article_id": ObjectId,        // Reference to articles collection
  "version": Number,             // Article version being reviewed
  "authors_used": [ObjectId],    // References to authors collection
  "purpose_analysis": {
    "questions": [String],       // Generated questions
    "scores": [Number],          // Scores for each question (1-10)
    "overall_score": Number      // Average score
  },
  "style_review": {
    "personas": [String],        // Personas used (Packy, Tufte, etc.)
    "feedback": [{
      "persona": String,
      "rating": Number,          // 1-10 rating
      "comments": String
    }]
  },
  "grammar_review": {
    "issues_found": Number,
    "suggestions": [String]
  },
  "overall_score": Number,       // Combined score
  "status": String,              // pending, completed, approved
  "created_at": Date,
  "completed_at": Date
}
```

**Indexes**:
```javascript
{ "_id": 1 }
{ "article_id": 1 }
{ "status": 1 }
{ "created_at": -1 }
```

## Data Relationships

### One-to-Many Relationships

1. **Articles → Reviews**
   - One article can have multiple reviews (different versions)
   - Foreign key: `reviews.article_id` → `articles._id`

2. **Authors → Articles**
   - One author can have many articles
   - Foreign key: `articles.author_id` → `authors._id`

3. **Authors → Reviews**
   - Multiple authors can be used in one review
   - Foreign key: `reviews.authors_used` → `authors._id`

### Author Content Workflow

#### How Authors Connect to Reviews

1. **External Authors** (for style comparison):
   ```javascript
   // Example: Packy McCormick author record
   {
     "_id": ObjectId("author123"),
     "name": "Packy McCormick",
     "author_type": "external"
   }
   
   // Packy's articles in articles collection
   {
     "author_id": ObjectId("author123"),
     "title": "The Great Online Game",
     "url": "https://notboring.co/p/the-great-online-game",
     "content": "Full article content...",
     "article_type": "reference",
     "source": "scraped"
   }
   ```

2. **User Authors** (your own writing):
   ```javascript
   // Example: Your author record
   {
     "_id": ObjectId("user456"),
     "name": "Your Name",
     "author_type": "user"
   }
   
   // Your articles in articles collection
   {
     "author_id": ObjectId("user456"),
     "title": "My Previous Blog Post",
     "content": "Your writing content...",
     "article_type": "user_blog",
     "source": "uploaded"
   }
   ```

#### How Reviews Use Author Content

When reviewing a blog, the system:

1. **Identifies which authors to use** (from review request)
2. **Queries articles collection** for all articles by those authors
3. **Uses the content to prime the LLM** for style analysis
4. **Stores the review results** in the reviews collection

**Example Query:**
```javascript
// Get all articles for an author to prime the LLM
db.articles.find({ 
  author_id: ObjectId("user456"),
  article_type: { $in: ["user_blog", "approved_blog"] }
})
```

#### Adding Your Writing to the System

You can add your own articles in several ways:

1. **Manual upload**: Upload your previous blog posts
2. **From reviews**: When you approve a blog, it gets added to your reference articles
3. **URL scraping**: Provide URLs to your published articles

This creates a feedback loop where your writing style improves the review quality over time.

## Practical Example

### Scenario: Reviewing Your New Blog Post

1. **You upload a new blog post**:
   ```javascript
   // articles collection
   {
     "author_id": ObjectId("user456"),
     "title": "Why Microgrids Will Replace Utilities",
     "content": "Your blog content...",
     "article_type": "draft",
     "review_status": "pending",
     "version": 1,
     "is_current": true,
     "purpose": "educational",
     "images": [...]
   }
   ```

2. **You request a review using your own writing style**:
   ```bash
   ./agent start-review --blog-file new-post.md --writers "Your Name" --purpose "educational"
   ```

3. **System retrieves your articles**:
   ```javascript
   // Query articles collection for your writing
   db.articles.find({ 
     author_id: ObjectId("user456"),
     article_type: { $in: ["user_blog", "approved_blog"] }
   })
   
   // Returns your articles:
   {
     "author_id": ObjectId("user456"),
     "title": "My Previous Post",
     "content": "Your writing style...",
     "article_type": "user_blog",
     "source": "uploaded"
   }
   ```

4. **System creates review using your style**:
   ```javascript
   // reviews collection
   {
     "article_id": ObjectId("..."),
     "authors_used": [ObjectId("your_author_id")],
     "style_review": {
       "personas": ["Your Name"],
       "feedback": [{
         "persona": "Your Name",
         "rating": 8.5,
         "comments": "This matches your typical style well..."
       }]
     }
   }
   ```

5. **After approval, your article gets updated**:
   ```javascript
   // Original article record gets updated
   {
     "review_status": "released",
     "article_type": "published",
     "review_id": ObjectId("review123")
   }
   
   // And gets added as reference material for future reviews
   {
     "author_id": ObjectId("user456"),
     "title": "Why Microgrids Will Replace Utilities",
     "content": "Your approved blog content...",
     "article_type": "reference",
     "source": "blog_review",
     "version": 1,
     "is_current": true
   }
   ```

This way, the system learns your writing style over time and provides more personalized feedback.

## Article Types and Review Status

### Article Types
- **`draft`**: New article uploaded for review
- **`published`**: Article that has been reviewed and approved
- **`reference`**: Articles used to prime the review agent (your previous work, external authors)
- **`review_example`**: Articles specifically uploaded as examples for review

### Review Status
- **`pending`**: Article uploaded but review not started
- **`in_progress`**: Review is currently running
- **`completed`**: Review finished, waiting for user approval
- **`approved`**: User approved the review
- **`released`**: Article is published and available

### Versioning
- Each article can have multiple versions (draft → revised → final)
- `is_current` flag indicates the active version
- Previous versions are kept for history but marked as `is_current: false`

## Storage Strategy

### MongoDB Collections
- **Articles**: Store all content (blogs, drafts, reference articles, published work)
- **Authors**: Store author profiles
- **Reviews**: Store review reports and scores

### Local File Storage
- **Images**: Store blog images in local filesystem
- **Backups**: Store database backups locally

### Why MongoDB?
- **Flexible schema**: Easy to add new fields
- **Document storage**: Natural fit for article content
- **Versioning**: Easy to handle article versions
- **Query flexibility**: Easy to find articles by type, status, author
