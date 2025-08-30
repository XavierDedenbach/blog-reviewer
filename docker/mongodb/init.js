// MongoDB initialization script for Blog Reviewer
// This script runs when the MongoDB container starts for the first time

// Switch to the blog_reviewer database
db = db.getSiblingDB('blog_reviewer');

// Create collections with proper validation
db.createCollection('articles', {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["title", "content", "article_type", "review_status", "purpose", "word_count", "slug", "source"],
            properties: {
                title: {
                    bsonType: "string",
                    description: "must be a string and is required"
                },
                content: {
                    bsonType: "string",
                    description: "must be a string and is required"
                },
                article_type: {
                    enum: ["draft", "published", "archived"],
                    description: "must be one of the enum values and is required"
                },
                review_status: {
                    enum: ["pending", "in_progress", "completed", "failed"],
                    description: "must be one of the enum values and is required"
                }
            }
        }
    }
});

db.createCollection('authors', {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["name", "email", "bio", "expertise_areas", "writing_style"],
            properties: {
                email: {
                    bsonType: "string",
                    pattern: "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$",
                    description: "must be a valid email address and is required"
                },
                name: {
                    bsonType: "string",
                    description: "must be a string and is required"
                }
            }
        }
    }
});

db.createCollection('reviews', {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["article_id", "version", "purpose", "target_audience", "review_config", "status"],
            properties: {
                article_id: {
                    bsonType: "objectId",
                    description: "must be an ObjectId and is required"
                },
                status: {
                    enum: ["pending", "in_progress", "completed", "failed"],
                    description: "must be one of the enum values and is required"
                }
            }
        }
    }
});

// Create indexes for better performance
db.articles.createIndex({ "slug": 1 }, { unique: true });
db.articles.createIndex({ "author_id": 1 });
db.articles.createIndex({ "article_type": 1 });
db.articles.createIndex({ "review_status": 1 });
db.articles.createIndex({ "created_at": -1 });
db.articles.createIndex({ "title": "text", "content": "text" });

db.authors.createIndex({ "email": 1 }, { unique: true });
db.authors.createIndex({ "name": 1 });
db.authors.createIndex({ "expertise_areas": 1 });

db.reviews.createIndex({ "article_id": 1 });
db.reviews.createIndex({ "status": 1 });
db.reviews.createIndex({ "created_at": -1 });
db.reviews.createIndex({ "article_id": 1, "version": 1 }, { unique: true });

// Create a test user for development
db.authors.insertOne({
    _id: ObjectId(),
    name: "Test Author",
    email: "test@example.com",
    bio: "A test author for development purposes",
    expertise_areas: ["technology", "programming"],
    writing_style: {
        tone: "professional",
        voice: "active",
        sentence_structure: "varied"
    },
    social_links: {
        twitter: "https://twitter.com/testauthor",
        linkedin: "https://linkedin.com/in/testauthor"
    },
    total_articles: 0,
    created_at: new Date(),
    updated_at: new Date()
});

print("MongoDB initialization completed successfully!");
print("Database: blog_reviewer");
print("Collections created: articles, authors, reviews");
print("Indexes created for optimal performance");
print("Test author created for development");
