# Deployment Guide: AI Blog Reviewer

## Overview

This guide provides instructions for deploying the Blog Reviewer MVP, focusing on getting the system running quickly for development and basic production use.

## Prerequisites

### System Requirements

#### Minimum Requirements (MVP)
- **CPU**: 1 core
- **RAM**: 2GB
- **Storage**: 10GB available space
- **OS**: Ubuntu 20.04+ or macOS 10.15+

#### Recommended Requirements
- **CPU**: 2+ cores
- **RAM**: 4GB+
- **Storage**: 20GB+ SSD
- **OS**: Ubuntu 22.04 LTS

### Software Dependencies

#### Required Software
- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **Git**: 2.30+

#### Optional Software
- **Make**: For simplified commands
- **jq**: For JSON processing
- **curl**: For API testing

### API Keys Required

#### Essential APIs (MVP)
- **OpenRouter API**: For LLM capabilities
- **Brave Search API**: For web search and writer discovery

#### Optional APIs
- **Firecrawl API**: For web scraping
- **SendGrid**: For email notifications
- **Opik**: For observability and debugging

## Local Development Setup

### Quick Start

#### 1. Clone Repository
```bash
git clone https://github.com/your-org/blog-reviewer.git
cd blog-reviewer
```

#### 2. Create Environment File
```bash
cp .env.example .env
```

Edit `.env` with your API keys:
```bash
# Required APIs
OPENROUTER_API_KEY=your_openrouter_key
BRAVE_API_KEY=your_brave_key

# Optional APIs
FIRECRAWL_API_KEY=your_firecrawl_key
SENDGRID_API_KEY=your_sendgrid_key
OPIK_API_KEY=your_opik_key

# Database
MONGODB_URI=mongodb://localhost:27017/blog_agent

# Application
APP_ENV=development
LOG_LEVEL=DEBUG
```

#### 3. Start Services
```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

#### 4. Verify Installation
```bash
# Health check
curl http://localhost:8080/api/v1/health

# Expected response
{
  "success": true,
  "data": {
    "status": "healthy",
    "services": {
      "database": "healthy",
      "openrouter": "healthy",
      "brave_search": "healthy"
    }
  }
}
```

### Development Workflow

#### Running Tests
```bash
# Run all tests
docker-compose exec blog-agent python -m pytest 

# Run specific test
docker-compose exec blog-agent python -m pytest tests/test_reviews.py

# Run with coverage
docker-compose exec blog-agent python -m pytest --cov=app
```

#### Code Quality
```bash
# Lint code
docker-compose exec blog-agent flake8 app/

# Format code
docker-compose exec blog-agent black app/

# Type checking
docker-compose exec blog-agent mypy app/
```

#### Database Management
```bash
# Access MongoDB shell
docker-compose exec mongo mongosh

# Backup database
docker-compose exec mongo mongodump --out /backup

# Restore database
docker-compose exec mongo mongorestore /backup
```

## Basic Production Deployment

### Simple Server Setup
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Add user to docker group
sudo usermod -aG docker $USER
```

### Production Configuration

#### Environment Variables
Create `.env` for production:
```bash
# Production settings
APP_ENV=production
LOG_LEVEL=INFO

# Database
MONGODB_URI=mongodb://mongo:27017/blog_agent

# API Keys
OPENROUTER_API_KEY=your_production_key
BRAVE_API_KEY=your_production_key

# Basic security
SECRET_KEY=your_secret_key_here
```

#### Docker Compose Production
Use the same `docker-compose.yml` as development, just with production environment variables.

### Deployment Commands

#### Initial Deployment
```bash
# Build and start services
docker-compose up -d --build

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

#### Health Check
```bash
# API health
curl http://localhost:8080/api/v1/health

# Database health
docker-compose exec mongo mongosh --eval "db.runCommand('ping')"
```

## Basic Monitoring

### Logs
```bash
# View application logs
docker-compose logs -f blog-agent

# View database logs
docker-compose logs -f mongo
```

### Health Checks
```bash
# Check container status
docker-compose ps

# Check resource usage
docker stats

# Test API endpoint
curl http://localhost:8080/api/v1/health
```

### Simple Backup
```bash
# Manual database backup
docker-compose exec mongo mongodump --out /backup

# Restore database
docker-compose exec mongo mongorestore /backup
```

## Troubleshooting

### Common Issues

#### Container Won't Start
```bash
# Check container logs
docker-compose logs blog-agent

# Restart containers
docker-compose restart
```

#### Database Connection Issues
```bash
# Check MongoDB status
docker-compose exec mongo mongosh --eval "db.runCommand('ping')"

# Restart MongoDB
docker-compose restart mongo
```

#### API Key Issues
```bash
# Check environment variables
docker-compose exec blog-agent env | grep API
```

### Basic Recovery
```bash
# Restart all services
docker-compose down
docker-compose up -d

# Rebuild if needed
docker-compose up -d --build
```

## Security Notes

### Basic Security
- Keep API keys secure
- Use HTTPS in production
- Regular system updates
- Monitor logs for issues
