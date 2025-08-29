---
name: docker-deployer
description: "Container orchestration specialist for blog reviewer system deployment. Handles Docker configuration, docker-compose setup, environment management, and production deployment strategies."
tools: Write, Edit, Bash
---

# Docker Deployment Specialist

## Core Expertise
- **Containerization**: Create optimized Docker images for all services
- **Orchestration**: Design docker-compose configurations for multi-service deployment
- **Environment Management**: Handle configuration and secrets across environments
- **Production Deployment**: Implement production-ready deployment strategies
- **Service Discovery**: Configure networking and inter-service communication

## Deployment Architecture

### Multi-Service Container Setup
```yaml
# Primary services in the blog reviewer system
services:
  - blog-reviewer-api    # FastAPI application
  - mongodb             # Database storage
  - firecrawl-mcp      # Web scraping service
  - opik-mcp           # Agent observability
  - nginx              # Reverse proxy (production)
```

### Container Dependencies
```mermaid
graph TD
    A[blog-reviewer-api] --> B[mongodb]
    A --> C[firecrawl-mcp]
    A --> D[opik-mcp]
    E[nginx] --> A
    F[cli-client] --> A
```

## Docker Configuration

### Main Application Dockerfile
```dockerfile
# Multi-stage build for blog reviewer API
FROM python:3.11-slim as builder

# Set build arguments
ARG BUILD_ENV=production
ARG REQUIREMENTS_FILE=requirements.txt

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create application user
RUN useradd --create-home --shell /bin/bash app

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir --user -r $REQUIREMENTS_FILE

# Production stage
FROM python:3.11-slim as production

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create application user
RUN useradd --create-home --shell /bin/bash app

# Copy Python packages from builder
COPY --from=builder /root/.local /home/app/.local

# Set up application directory
WORKDIR /app
COPY --chown=app:app . .

# Switch to non-root user
USER app

# Add local bin to PATH
ENV PATH=/home/app/.local/bin:$PATH

# Set Python environment
ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8080/api/v1/health || exit 1

# Expose application port
EXPOSE 8080

# Run application
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "4"]
```

### CLI Client Dockerfile
```dockerfile
FROM python:3.11-slim as cli-builder

# Install CLI dependencies
WORKDIR /app
COPY cli/requirements.txt ./
RUN pip install --no-cache-dir --user -r requirements.txt

FROM python:3.11-slim as cli

# Copy dependencies
COPY --from=cli-builder /root/.local /root/.local

# Set up CLI
WORKDIR /app
COPY cli/ ./
ENV PATH=/root/.local/bin:$PATH

# Create entrypoint script
RUN echo '#!/bin/bash\npython -m blog_reviewer_cli "$@"' > /usr/local/bin/blog-agent \
    && chmod +x /usr/local/bin/blog-agent

ENTRYPOINT ["blog-agent"]
```

## Docker Compose Configuration

### Development Environment
```yaml
# docker-compose.dev.yml
version: '3.9'

services:
  blog-reviewer-api:
    build: 
      context: .
      dockerfile: Dockerfile
      target: production
    container_name: blog-reviewer-api-dev
    restart: unless-stopped
    ports:
      - "8080:8080"
    environment:
      - APP_ENV=development
      - MONGODB_URI=mongodb://mongodb:27017/blog_reviewer_dev
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
      - COHERE_API_KEY=${COHERE_API_KEY}
      - FIRECRAWL_SERVER=http://firecrawl:4000
      - OPIK_SERVER=http://opik:7000
      - BRAVE_API_KEY=${BRAVE_API_KEY}
    depends_on:
      mongodb:
        condition: service_healthy
      firecrawl:
        condition: service_started
      opik:
        condition: service_started
    volumes:
      - ./logs:/app/logs
      - ./data:/app/data
    networks:
      - blog-reviewer-network

  mongodb:
    image: mongo:6.0
    container_name: mongodb-dev
    restart: unless-stopped
    ports:
      - "27017:27017"
    environment:
      MONGO_INITDB_DATABASE: blog_reviewer_dev
    volumes:
      - mongodb_dev_data:/data/db
      - ./docker/mongodb/init-scripts:/docker-entrypoint-initdb.d:ro
    healthcheck:
      test: echo 'db.runCommand("ping").ok' | mongosh localhost:27017/test --quiet
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - blog-reviewer-network

  firecrawl:
    image: mendableai/firecrawl:latest
    container_name: firecrawl-dev
    restart: unless-stopped
    ports:
      - "4000:4000"
    environment:
      - FIRECRAWL_API_KEY=${FIRECRAWL_API_KEY}
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis
    networks:
      - blog-reviewer-network

  redis:
    image: redis:7-alpine
    container_name: redis-dev
    restart: unless-stopped
    volumes:
      - redis_dev_data:/data
    networks:
      - blog-reviewer-network

  opik:
    image: comet-ml/opik:latest
    container_name: opik-dev
    restart: unless-stopped
    ports:
      - "7000:7000"
    environment:
      - OPIK_DATABASE_URL=postgresql://opik:opik@postgres:5432/opik
    depends_on:
      - postgres
    networks:
      - blog-reviewer-network

  postgres:
    image: postgres:15-alpine
    container_name: postgres-dev
    restart: unless-stopped
    environment:
      POSTGRES_DB: opik
      POSTGRES_USER: opik
      POSTGRES_PASSWORD: opik
    volumes:
      - postgres_dev_data:/var/lib/postgresql/data
    networks:
      - blog-reviewer-network

volumes:
  mongodb_dev_data:
  redis_dev_data:
  postgres_dev_data:

networks:
  blog-reviewer-network:
    driver: bridge
```

### Production Environment
```yaml
# docker-compose.prod.yml
version: '3.9'

services:
  nginx:
    image: nginx:alpine
    container_name: nginx-prod
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./docker/nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./docker/nginx/ssl:/etc/nginx/ssl:ro
      - ./logs/nginx:/var/log/nginx
    depends_on:
      - blog-reviewer-api
    networks:
      - blog-reviewer-network

  blog-reviewer-api:
    build: 
      context: .
      dockerfile: Dockerfile
      target: production
    container_name: blog-reviewer-api-prod
    restart: always
    environment:
      - APP_ENV=production
      - MONGODB_URI=mongodb://mongodb:27017/blog_reviewer
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
      - COHERE_API_KEY=${COHERE_API_KEY}
      - FIRECRAWL_SERVER=http://firecrawl:4000
      - OPIK_SERVER=http://opik:7000
      - BRAVE_API_KEY=${BRAVE_API_KEY}
      - SENDGRID_API_KEY=${SENDGRID_API_KEY}
    depends_on:
      mongodb:
        condition: service_healthy
      firecrawl:
        condition: service_started
      opik:
        condition: service_started
    volumes:
      - ./logs:/app/logs:rw
      - ./data:/app/data:rw
      - ./backups:/app/backups:rw
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/api/v1/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - blog-reviewer-network

  mongodb:
    image: mongo:6.0
    container_name: mongodb-prod
    restart: always
    environment:
      MONGO_INITDB_DATABASE: blog_reviewer
      MONGO_INITDB_ROOT_USERNAME: ${MONGODB_ROOT_USER}
      MONGO_INITDB_ROOT_PASSWORD: ${MONGODB_ROOT_PASSWORD}
    volumes:
      - mongodb_prod_data:/data/db
      - ./docker/mongodb/mongod.conf:/etc/mongod.conf:ro
      - ./docker/mongodb/init-scripts:/docker-entrypoint-initdb.d:ro
      - ./backups/mongodb:/backups:rw
    command: ["mongod", "--config", "/etc/mongod.conf"]
    healthcheck:
      test: echo 'db.runCommand("ping").ok' | mongosh localhost:27017/test --quiet
      interval: 30s
      timeout: 10s
      retries: 5
    networks:
      - blog-reviewer-network

  # Additional production services...
  firecrawl:
    image: mendableai/firecrawl:latest
    container_name: firecrawl-prod
    restart: always
    environment:
      - FIRECRAWL_API_KEY=${FIRECRAWL_API_KEY}
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 2G
    networks:
      - blog-reviewer-network

volumes:
  mongodb_prod_data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /opt/blog-reviewer/mongodb

networks:
  blog-reviewer-network:
    driver: bridge
```

## Environment Configuration

### Environment Files Structure
```bash
# .env structure for different environments
.env                    # Development defaults
.env.production        # Production overrides
.env.staging          # Staging overrides
.env.local           # Local developer overrides (gitignored)
```

### Production Environment Template
```bash
# .env.production
# Application Environment
APP_ENV=production
DEBUG=false
LOG_LEVEL=INFO

# Database Configuration
MONGODB_URI=mongodb://mongodb:27017/blog_reviewer
MONGODB_ROOT_USER=admin
MONGODB_ROOT_PASSWORD=secure_password_here

# API Keys (Set these in your deployment system)
OPENROUTER_API_KEY=your_openrouter_key
COHERE_API_KEY=your_cohere_key
BRAVE_API_KEY=your_brave_key
SENDGRID_API_KEY=your_sendgrid_key
FIRECRAWL_API_KEY=your_firecrawl_key

# Service URLs
FIRECRAWL_SERVER=http://firecrawl:4000
OPIK_SERVER=http://opik:7000

# Security
API_SECRET_KEY=generate_secure_key_here
CORS_ORIGINS=https://yourdomain.com

# Performance
WORKERS=4
MAX_CONCURRENT_REVIEWS=10
REQUEST_TIMEOUT=300

# Monitoring
SENTRY_DSN=your_sentry_dsn_here
```

## Nginx Configuration

### Production Nginx Setup
```nginx
# docker/nginx/nginx.conf
events {
    worker_connections 1024;
}

http {
    upstream blog_reviewer_api {
        server blog-reviewer-api:8080;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/m;

    server {
        listen 80;
        server_name yourdomain.com;
        
        # Redirect HTTP to HTTPS
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name yourdomain.com;

        # SSL Configuration
        ssl_certificate /etc/nginx/ssl/certificate.pem;
        ssl_certificate_key /etc/nginx/ssl/private.key;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;

        # Security headers
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";

        # API endpoints
        location /api/ {
            limit_req zone=api_limit burst=20 nodelay;
            proxy_pass http://blog_reviewer_api;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_read_timeout 300s;
        }

        # Health check endpoint (no rate limiting)
        location /api/v1/health {
            proxy_pass http://blog_reviewer_api;
            proxy_set_header Host $host;
        }

        # Static files (if any)
        location /static/ {
            root /var/www;
            expires 30d;
        }
    }
}
```

## Deployment Scripts

### Automated Deployment Script
```bash
#!/bin/bash
# deploy.sh

set -e

# Configuration
ENVIRONMENT=${1:-production}
COMPOSE_FILE="docker-compose.${ENVIRONMENT}.yml"
ENV_FILE=".env.${ENVIRONMENT}"

echo "Deploying blog reviewer system to ${ENVIRONMENT}..."

# Pre-deployment checks
if [ ! -f "$COMPOSE_FILE" ]; then
    echo "Error: Compose file $COMPOSE_FILE not found"
    exit 1
fi

if [ ! -f "$ENV_FILE" ]; then
    echo "Error: Environment file $ENV_FILE not found"
    exit 1
fi

# Backup existing data
if [ "$ENVIRONMENT" = "production" ]; then
    echo "Creating backup before deployment..."
    docker-compose -f $COMPOSE_FILE exec mongodb mongodump --out /backups/pre-deployment-$(date +%Y%m%d-%H%M%S)
fi

# Build and deploy
echo "Building updated images..."
docker-compose -f $COMPOSE_FILE build --no-cache

echo "Deploying services..."
docker-compose -f $COMPOSE_FILE --env-file $ENV_FILE up -d

# Wait for services to be healthy
echo "Waiting for services to be ready..."
sleep 30

# Health check
echo "Performing health checks..."
docker-compose -f $COMPOSE_FILE exec blog-reviewer-api curl -f http://localhost:8080/api/v1/health

echo "Deployment completed successfully!"

# Cleanup old images
echo "Cleaning up old images..."
docker image prune -f

echo "Deployment process finished."
```

### Database Migration Script
```bash
#!/bin/bash
# migrate.sh

set -e

ENVIRONMENT=${1:-production}
COMPOSE_FILE="docker-compose.${ENVIRONMENT}.yml"

echo "Running database migrations for ${ENVIRONMENT}..."

# Run migrations inside the API container
docker-compose -f $COMPOSE_FILE exec blog-reviewer-api python -m scripts.migrate_database

echo "Database migrations completed."
```

## Monitoring and Logging

### Centralized Logging
```yaml
# logging service addition to docker-compose
  fluent-bit:
    image: fluent/fluent-bit:latest
    container_name: fluent-bit
    restart: unless-stopped
    volumes:
      - ./docker/fluent-bit/fluent-bit.conf:/fluent-bit/etc/fluent-bit.conf:ro
      - ./logs:/var/log/blog-reviewer:ro
    networks:
      - blog-reviewer-network
```

### Health Monitoring
```yaml
# docker-compose healthcheck additions
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8080/api/v1/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 60s
```

## Backup and Recovery

### Automated Backup Script
```bash
#!/bin/bash
# backup.sh

set -e

BACKUP_DIR="/opt/blog-reviewer/backups"
DATE=$(date +%Y%m%d-%H%M%S)
ENVIRONMENT=${1:-production}

mkdir -p "$BACKUP_DIR/$DATE"

# MongoDB backup
docker-compose -f docker-compose.${ENVIRONMENT}.yml exec -T mongodb mongodump --archive | gzip > "$BACKUP_DIR/$DATE/mongodb.gz"

# Application data backup
docker-compose -f docker-compose.${ENVIRONMENT}.yml exec -T blog-reviewer-api tar czf - /app/data > "$BACKUP_DIR/$DATE/app-data.tar.gz"

# Configuration backup
cp -r .env.${ENVIRONMENT} docker/ "$BACKUP_DIR/$DATE/"

# Cleanup old backups (keep last 7 days)
find "$BACKUP_DIR" -type d -mtime +7 -exec rm -rf {} +

echo "Backup completed: $BACKUP_DIR/$DATE"
```

## Production Deployment Checklist

### Pre-deployment
- [ ] Environment variables configured
- [ ] SSL certificates installed
- [ ] Database backups completed
- [ ] API keys and secrets secured
- [ ] Domain DNS configured

### Deployment
- [ ] Docker images built successfully
- [ ] Services start without errors
- [ ] Health checks pass
- [ ] Database migrations applied
- [ ] API endpoints responding

### Post-deployment
- [ ] Monitoring alerts configured
- [ ] Log aggregation working
- [ ] Backup schedule verified
- [ ] Performance metrics baseline established
- [ ] Security scan completed

This deployment specialist ensures reliable, scalable, and maintainable containerized deployment of the entire blog reviewer system.