---
name: mongodb-manager
description: "MongoDB database specialist for the blog reviewer system. Handles schema design, data operations, indexing, performance optimization, and integration with blog review workflows. Manages complex document relationships and ensures data consistency."
tools: Bash, Glob, Grep, LS, Read, Edit, Write, WebFetch, WebSearch, BashOutput, KillBash, TodoWrite
---

# MongoDB Database Management Specialist

## Core Expertise
- **Schema Design**: Design and implement complex document structures for blog review system
- **Data Operations**: Handle CRUD operations for articles, authors, reviews, and metadata
- **Performance Optimization**: Implement indexing strategies and query optimization
- **Data Migration**: Manage schema evolution and data migrations
- **Integration Support**: Provide database layer for all system components

## Database Architecture

### Database Structure
```javascript
// Database: blog_reviewer
// Collections:
// - articles: All blog content (drafts, published, reference)
// - authors: Author profiles and metadata
// - reviews: Review reports and analysis results
// - users: User accounts and API keys
// - system_config: Application configuration
```

### Collection Schemas

#### Articles Collection
```javascript
{
  "_id": ObjectId,
  "author_id": ObjectId,              // Reference to authors collection
  "title": String,                    // Article title
  "slug": String,                     // URL-friendly identifier
  "content": String,                  // Full article content in markdown
  "url": String,                      // Original URL (if scraped)
  "article_type": String,             // "draft", "published", "reference", "review_example"
  "review_status": String,            // "pending", "in_progress", "completed", "approved", "released"
  "review_id": ObjectId,              // Reference to reviews collection
  "version": Number,                  // Content version (1, 2, 3...)
  "is_current": Boolean,              // Current version flag
  "purpose": String,                  // Article purpose for review
  "word_count": Number,
  "reading_time_minutes": Number,
  "images": [{
    "filename": String,
    "url": String,
    "alt_text": String,
    "caption": String,
    "stored_locally": Boolean
  }],
  "metadata": {
    "tags": [String],
    "description": String,
    "published_date": Date,
    "canonical_url": String,
    "language": String,
    "seo_keywords": [String]
  },
  "source": String,                   // "scraped", "uploaded", "blog_review", "manual"
  "processing_metadata": {
    "scraped_at": Date,
    "processed_at": Date,
    "processor_version": String,
    "quality_score": Number,
    "content_completeness": Number
  },
  "created_at": Date,
  "updated_at": Date
}
```

#### Authors Collection
```javascript
{
  "_id": ObjectId,
  "name": String,                     // Author display name
  "slug": String,                     // URL-friendly identifier
  "bio": String,                      // Author biography
  "author_type": String,              // "external", "user"
  "contact_info": {
    "email": String,
    "website": String,
    "social_profiles": [{
      "platform": String,            // "twitter", "linkedin", "medium"
      "url": String,
      "username": String
    }]
  },
  "style_profile": {
    "tone": String,                   // "conversational", "formal", "technical"
    "complexity": String,             // "simple", "medium", "complex"
    "writing_style": String,          // "narrative", "analytical", "list-based"
    "avg_sentence_length": Number,
    "vocabulary_complexity": Number,
    "preferred_formats": [String],    // "long-form", "listicles", "tutorials"
    "expertise_areas": [String]
  },
  "content_stats": {
    "total_articles": Number,
    "avg_word_count": Number,
    "content_themes": [String],
    "publication_frequency": String,
    "last_content_date": Date
  },
  "scraping_config": {
    "source_urls": [String],          // URLs to scrape
    "last_scraped": Date,
    "scraping_frequency": String,     // "weekly", "monthly", "manual"
    "max_articles": Number,
    "content_filters": {
      "min_word_count": Number,
      "exclude_patterns": [String],
      "include_only": [String]
    }
  },
  "created_at": Date,
  "updated_at": Date
}
```

#### Reviews Collection
```javascript
{
  "_id": ObjectId,
  "article_id": ObjectId,             // Reference to articles collection
  "version": Number,                  // Article version being reviewed
  "review_config": {
    "authors_used": [ObjectId],       // Author references for style comparison
    "purpose": String,                // Review purpose
    "analysis_depth": String,         // "basic", "standard", "comprehensive"
    "requested_by": ObjectId          // User who requested review
  },
  "workflow_status": {
    "current_phase": String,          // "setup", "analyzing", "compiling", "completed"
    "setup": {
      "complete": Boolean,
      "started_at": Date,
      "completed_at": Date,
      "writers_validated": Boolean,
      "questions_generated": [String],
      "errors": [String]
    },
    "purpose_analysis": {
      "complete": Boolean,
      "started_at": Date,
      "completed_at": Date,
      "questions": [String],
      "scores": [{
        "question": String,
        "score": Number,              // 1-10 scale
        "reasoning": String,
        "evidence": [String]
      }],
      "overall_score": Number,
      "processing_time_seconds": Number
    },
    "style_review": {
      "complete": Boolean,
      "started_at": Date,
      "completed_at": Date,
      "personas_used": [String],
      "reviews": [{
        "author_id": ObjectId,
        "author_name": String,
        "rating": Number,             // 1-10 scale
        "feedback": {
          "strengths": [String],
          "improvement_areas": [String],
          "specific_suggestions": [String],
          "tone_alignment": Number,
          "style_consistency": Number
        },
        "processing_time_seconds": Number
      }],
      "aggregate_score": Number
    },
    "grammar_review": {
      "complete": Boolean,
      "started_at": Date,
      "completed_at": Date,
      "issues_found": [{
        "type": String,               // "grammar", "clarity", "style", "spelling"
        "severity": String,           // "low", "medium", "high"
        "text": String,               // Problematic text
        "line_number": Number,
        "suggestion": String,
        "explanation": String
      }],
      "summary": {
        "total_issues": Number,
        "grammar_score": Number,      // 1-10 scale
        "clarity_score": Number,
        "readability_score": Number
      },
      "processing_time_seconds": Number
    }
  },
  "final_assessment": {
    "overall_score": Number,          // Weighted average of all scores
    "score_breakdown": {
      "purpose_weight": Number,
      "style_weight": Number,
      "grammar_weight": Number
    },
    "key_strengths": [String],
    "priority_improvements": [String],
    "actionable_recommendations": [String],
    "estimated_revision_time": String
  },
  "review_metadata": {
    "total_processing_time": Number,
    "api_calls_made": Number,
    "tokens_consumed": Number,
    "estimated_cost": Number,
    "system_version": String
  },
  "approval_status": {
    "status": String,                 // "pending", "approved", "rejected", "needs_revision"
    "approved_by": ObjectId,
    "approved_at": Date,
    "user_comments": String,
    "follow_up_actions": [String]
  },
  "created_at": Date,
  "updated_at": Date
}
```

#### Users Collection
```javascript
{
  "_id": ObjectId,
  "username": String,
  "email": String,
  "full_name": String,
  "user_type": String,                // "admin", "user", "api_only"
  "authentication": {
    "password_hash": String,          // bcrypt hash
    "api_keys": [{
      "key_hash": String,
      "name": String,                 // Key description
      "permissions": [String],
      "created_at": Date,
      "expires_at": Date,
      "last_used": Date,
      "is_active": Boolean
    }],
    "last_login": Date
  },
  "preferences": {
    "default_review_purpose": String,
    "preferred_authors": [ObjectId],
    "notification_settings": {
      "email_enabled": Boolean,
      "review_completion": Boolean,
      "system_updates": Boolean
    },
    "ui_preferences": {
      "theme": String,
      "language": String,
      "timezone": String
    }
  },
  "usage_stats": {
    "total_reviews": Number,
    "total_articles_uploaded": Number,
    "api_calls_this_month": Number,
    "storage_used_mb": Number
  },
  "created_at": Date,
  "updated_at": Date
}
```

## Database Operations

### Core CRUD Operations

#### Article Management
```javascript
// Create new article
async function createArticle(articleData) {
  const article = {
    ...articleData,
    _id: new ObjectId(),
    slug: generateSlug(articleData.title),
    word_count: countWords(articleData.content),
    reading_time_minutes: calculateReadingTime(articleData.content),
    is_current: true,
    version: 1,
    created_at: new Date(),
    updated_at: new Date()
  };
  
  return await db.articles.insertOne(article);
}

// Update article version
async function createNewVersion(articleId, updatedContent) {
  // Mark current version as not current
  await db.articles.updateMany(
    { "article_id": articleId, "is_current": true },
    { $set: { "is_current": false } }
  );
  
  // Get latest version number
  const latestVersion = await db.articles.findOne(
    { "article_id": articleId },
    { sort: { version: -1 } }
  );
  
  // Create new version
  const newVersion = {
    ...updatedContent,
    article_id: articleId,
    version: (latestVersion?.version || 0) + 1,
    is_current: true,
    created_at: new Date(),
    updated_at: new Date()
  };
  
  return await db.articles.insertOne(newVersion);
}

// Get current article version
async function getCurrentArticleVersion(articleId) {
  return await db.articles.findOne({
    article_id: articleId,
    is_current: true
  });
}
```

#### Review Management
```javascript
// Create review record
async function createReview(reviewData) {
  const review = {
    _id: new ObjectId(),
    article_id: reviewData.article_id,
    version: reviewData.version,
    review_config: reviewData.config,
    workflow_status: {
      current_phase: "setup",
      setup: { complete: false, started_at: new Date() },
      purpose_analysis: { complete: false },
      style_review: { complete: false },
      grammar_review: { complete: false }
    },
    created_at: new Date(),
    updated_at: new Date()
  };
  
  return await db.reviews.insertOne(review);
}

// Update review phase
async function updateReviewPhase(reviewId, phase, data) {
  const updatePath = `workflow_status.${phase}`;
  const update = {
    $set: {
      [`${updatePath}.complete`]: true,
      [`${updatePath}.completed_at`]: new Date(),
      "updated_at": new Date(),
      ...Object.fromEntries(
        Object.entries(data).map(([key, value]) => 
          [`${updatePath}.${key}`, value]
        )
      )
    }
  };
  
  return await db.reviews.updateOne({ _id: reviewId }, update);
}

// Get active reviews
async function getActiveReviews(limit = 10) {
  return await db.reviews.find({
    "workflow_status.current_phase": { 
      $in: ["setup", "analyzing", "compiling"] 
    }
  })
  .sort({ created_at: -1 })
  .limit(limit)
  .toArray();
}
```

#### Author Operations
```javascript
// Create author with style profiling
async function createAuthor(authorData) {
  const author = {
    _id: new ObjectId(),
    name: authorData.name,
    slug: generateSlug(authorData.name),
    author_type: authorData.author_type || "external",
    style_profile: await generateInitialStyleProfile(authorData),
    content_stats: {
      total_articles: 0,
      avg_word_count: 0,
      content_themes: [],
      last_content_date: null
    },
    created_at: new Date(),
    updated_at: new Date()
  };
  
  return await db.authors.insertOne(author);
}

// Update author style profile
async function updateAuthorStyleProfile(authorId, articles) {
  const styleAnalysis = await analyzeAuthorStyle(articles);
  
  return await db.authors.updateOne(
    { _id: authorId },
    {
      $set: {
        style_profile: styleAnalysis.style_profile,
        content_stats: styleAnalysis.content_stats,
        updated_at: new Date()
      }
    }
  );
}

// Get authors with article count
async function getAuthorsWithStats() {
  return await db.authors.aggregate([
    {
      $lookup: {
        from: "articles",
        localField: "_id",
        foreignField: "author_id",
        as: "articles"
      }
    },
    {
      $addFields: {
        "content_stats.total_articles": { $size: "$articles" },
        "content_stats.avg_word_count": { 
          $avg: "$articles.word_count" 
        }
      }
    },
    {
      $project: { articles: 0 }  // Remove articles from output
    }
  ]).toArray();
}
```

## Indexing Strategy

### Performance-Critical Indexes
```javascript
// Articles collection indexes
db.articles.createIndex({ "author_id": 1 });
db.articles.createIndex({ "article_type": 1, "review_status": 1 });
db.articles.createIndex({ "is_current": 1, "created_at": -1 });
db.articles.createIndex({ "slug": 1 }, { unique: true, sparse: true });
db.articles.createIndex({ "review_id": 1 });
db.articles.createIndex({ "url": 1 }, { sparse: true });

// Text search index for content
db.articles.createIndex({ 
  "title": "text", 
  "content": "text", 
  "metadata.description": "text" 
});

// Reviews collection indexes
db.reviews.createIndex({ "article_id": 1, "version": 1 });
db.reviews.createIndex({ "workflow_status.current_phase": 1 });
db.reviews.createIndex({ "created_at": -1 });
db.reviews.createIndex({ "approval_status.status": 1 });
db.reviews.createIndex({ "review_config.requested_by": 1 });

// Authors collection indexes
db.authors.createIndex({ "name": 1 });
db.authors.createIndex({ "slug": 1 }, { unique: true });
db.authors.createIndex({ "author_type": 1 });
db.authors.createIndex({ "scraping_config.last_scraped": 1 });

// Users collection indexes
db.users.createIndex({ "email": 1 }, { unique: true });
db.users.createIndex({ "username": 1 }, { unique: true });
db.users.createIndex({ "authentication.api_keys.key_hash": 1 }, { sparse: true });
```

## Data Migration Scripts

### Schema Evolution Support
```javascript
// Migration: Add new fields to existing documents
async function migration_001_add_processing_metadata() {
  const result = await db.articles.updateMany(
    { processing_metadata: { $exists: false } },
    {
      $set: {
        processing_metadata: {
          processed_at: new Date(),
          processor_version: "1.0.0",
          quality_score: null,
          content_completeness: null
        }
      }
    }
  );
  
  console.log(`Updated ${result.modifiedCount} articles with processing metadata`);
}

// Migration: Normalize author style profiles
async function migration_002_normalize_style_profiles() {
  const authors = await db.authors.find({
    "style_profile.tone": { $type: "string" }
  }).toArray();
  
  for (const author of authors) {
    const normalizedProfile = normalizeStyleProfile(author.style_profile);
    
    await db.authors.updateOne(
      { _id: author._id },
      { $set: { style_profile: normalizedProfile } }
    );
  }
  
  console.log(`Normalized ${authors.length} author style profiles`);
}

// Migration runner
async function runMigrations() {
  const migrations = [
    { version: 1, name: "add_processing_metadata", fn: migration_001_add_processing_metadata },
    { version: 2, name: "normalize_style_profiles", fn: migration_002_normalize_style_profiles }
  ];
  
  for (const migration of migrations) {
    const exists = await db.system_config.findOne({ 
      type: "migration", 
      version: migration.version 
    });
    
    if (!exists) {
      console.log(`Running migration ${migration.version}: ${migration.name}`);
      await migration.fn();
      
      await db.system_config.insertOne({
        type: "migration",
        version: migration.version,
        name: migration.name,
        executed_at: new Date()
      });
    }
  }
}
```

## Performance Optimization

### Query Optimization
```javascript
// Optimized queries for common operations

// Get review dashboard data
async function getReviewDashboard(userId, limit = 20) {
  return await db.reviews.aggregate([
    {
      $match: { 
        "review_config.requested_by": userId 
      }
    },
    {
      $lookup: {
        from: "articles",
        localField: "article_id",
        foreignField: "_id",
        as: "article"
      }
    },
    {
      $unwind: "$article"
    },
    {
      $project: {
        _id: 1,
        "article.title": 1,
        "workflow_status.current_phase": 1,
        "final_assessment.overall_score": 1,
        created_at: 1,
        "workflow_status.grammar_review.complete": 1
      }
    },
    {
      $sort: { created_at: -1 }
    },
    {
      $limit: limit
    }
  ]).toArray();
}

// Get author articles for style analysis
async function getAuthorStyleSample(authorId, limit = 10) {
  return await db.articles.aggregate([
    {
      $match: {
        author_id: authorId,
        article_type: { $in: ["reference", "published"] },
        word_count: { $gte: 500 }  // Minimum length for style analysis
      }
    },
    {
      $sample: { size: limit }
    },
    {
      $project: {
        title: 1,
        content: 1,
        word_count: 1,
        "metadata.published_date": 1
      }
    }
  ]).toArray();
}
```

### Connection Management
```javascript
// MongoDB connection with optimal settings
const mongoOptions = {
  maxPoolSize: 50,          // Maximum connections
  minPoolSize: 5,           // Minimum connections  
  maxIdleTimeMS: 30000,     // Close connections after 30s idle
  serverSelectionTimeoutMS: 5000,  // 5s timeout for server selection
  socketTimeoutMS: 45000,   // 45s socket timeout
  bufferMaxEntries: 0,      // Disable mongoose buffering
  bufferCommands: false,    // Disable mongoose buffering
  compressors: ['zlib'],    // Enable compression
  retryWrites: true,        // Enable retry writes
  writeConcern: { w: 'majority', j: true }  // Ensure write durability
};
```

## Data Validation and Integrity

### Schema Validation
```javascript
// Collection validation rules
db.createCollection("articles", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["title", "content", "author_id", "article_type"],
      properties: {
        title: {
          bsonType: "string",
          minLength: 1,
          maxLength: 500
        },
        content: {
          bsonType: "string",
          minLength: 100
        },
        author_id: {
          bsonType: "objectId"
        },
        article_type: {
          enum: ["draft", "published", "reference", "review_example"]
        },
        word_count: {
          bsonType: "int",
          minimum: 0
        }
      }
    }
  }
});

// Data integrity checks
async function validateDataIntegrity() {
  const issues = [];
  
  // Check for orphaned reviews
  const orphanedReviews = await db.reviews.find({
    article_id: { $nin: await db.articles.distinct("_id") }
  }).count();
  
  if (orphanedReviews > 0) {
    issues.push(`Found ${orphanedReviews} orphaned reviews`);
  }
  
  // Check for articles without authors
  const articlesWithoutAuthors = await db.articles.find({
    author_id: { $nin: await db.authors.distinct("_id") }
  }).count();
  
  if (articlesWithoutAuthors > 0) {
    issues.push(`Found ${articlesWithoutAuthors} articles without valid authors`);
  }
  
  return issues;
}
```

## Backup and Recovery

### Automated Backup Strategy
```javascript
// Backup configuration
const backupConfig = {
  schedule: "0 2 * * *",  // Daily at 2 AM
  retention: {
    daily: 7,    // Keep 7 daily backups
    weekly: 4,   // Keep 4 weekly backups  
    monthly: 12  // Keep 12 monthly backups
  },
  destinations: [
    "local",     // Local filesystem
    "s3",        // AWS S3 bucket
    "azure"      // Azure Blob Storage
  ]
};

// Backup execution
async function performBackup(type = "daily") {
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  const backupName = `blog-reviewer-${type}-${timestamp}`;
  
  // Create MongoDB dump
  const dumpCommand = `mongodump --uri="${process.env.MONGODB_URI}" --out=/backups/${backupName}`;
  await execAsync(dumpCommand);
  
  // Compress backup
  const compressCommand = `tar -czf /backups/${backupName}.tar.gz /backups/${backupName}`;
  await execAsync(compressCommand);
  
  // Upload to cloud storage
  await uploadToCloudStorage(`/backups/${backupName}.tar.gz`);
  
  // Cleanup old backups
  await cleanupOldBackups(type);
  
  console.log(`Backup completed: ${backupName}`);
}
```

## Integration with System Components

### Agent Integration Points
```javascript
// Content Analyzer integration
async function storeContentAnalysis(articleId, analysis) {
  return await db.articles.updateOne(
    { _id: articleId },
    {
      $set: {
        "processing_metadata.content_analysis": analysis,
        "processing_metadata.analyzed_at": new Date()
      }
    }
  );
}

// Review Orchestrator integration  
async function updateReviewProgress(reviewId, phase, progressData) {
  const updatePath = `workflow_status.${phase}`;
  
  return await db.reviews.updateOne(
    { _id: reviewId },
    {
      $set: {
        [`${updatePath}`]: progressData,
        "workflow_status.current_phase": phase,
        "updated_at": new Date()
      }
    }
  );
}

// External Scraper integration
async function storeScrapedArticles(authorId, articles) {
  const operations = articles.map(article => ({
    updateOne: {
      filter: { url: article.url },
      update: {
        $setOnInsert: {
          ...article,
          author_id: authorId,
          article_type: "reference",
          source: "scraped",
          created_at: new Date()
        },
        $set: {
          updated_at: new Date()
        }
      },
      upsert: true
    }
  }));
  
  return await db.articles.bulkWrite(operations);
}
```

This MongoDB specialist ensures efficient, reliable, and scalable data management for the entire blog reviewer system, providing the foundation for all other components to build upon.