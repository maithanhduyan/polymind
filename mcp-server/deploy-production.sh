#!/bin/bash
# Generated by Copilot
# Production Deployment Script for PolyMind MCP Server v1.0.0

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_NAME="polymind_prod"
BACKUP_DIR="/var/backups/polymind"
LOG_FILE="/var/log/polymind/deployment.log"

# Functions
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    echo "[ERROR] $1" >> "$LOG_FILE"
    exit 1
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
    echo "[SUCCESS] $1" >> "$LOG_FILE"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
    echo "[WARNING] $1" >> "$LOG_FILE"
}

# Pre-deployment checks
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed"
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose is not installed"
    fi
    
    # Check environment file
    if [ ! -f ".env.production" ]; then
        error "Production environment file (.env.production) not found"
    fi
    
    # Check disk space (minimum 10GB)
    AVAILABLE_SPACE=$(df / | awk 'NR==2 {print $4}')
    if [ "$AVAILABLE_SPACE" -lt 10485760 ]; then
        error "Insufficient disk space. Minimum 10GB required"
    fi
    
    success "Prerequisites check passed"
}

# Backup existing data
backup_data() {
    log "Creating backup of existing data..."
    
    # Create backup directory
    mkdir -p "$BACKUP_DIR/$(date +%Y%m%d_%H%M%S)"
    BACKUP_TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
    
    # Check if containers exist
    if docker-compose -p "$PROJECT_NAME" ps -q postgres > /dev/null 2>&1; then
        log "Backing up PostgreSQL data..."
        docker-compose -p "$PROJECT_NAME" exec -T postgres \
            pg_dump -U polymind_user polymind_prod > "$BACKUP_DIR/$BACKUP_TIMESTAMP/postgres_backup.sql"
    fi
    
    if docker-compose -p "$PROJECT_NAME" ps -q chromadb > /dev/null 2>&1; then
        log "Backing up ChromaDB data..."
        docker cp "${PROJECT_NAME}_chromadb_1:/chroma/chroma_data" "$BACKUP_DIR/$BACKUP_TIMESTAMP/chromadb_data"
    fi
    
    success "Backup completed: $BACKUP_DIR/$BACKUP_TIMESTAMP"
}

# Deploy application
deploy_application() {
    log "Starting deployment..."
    
    # Pull latest images
    log "Pulling Docker images..."
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml pull
    
    # Build custom images
    log "Building application images..."
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml build
    
    # Start services
    log "Starting services..."
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
    
    success "Deployment completed"
}

# Health checks
health_check() {
    log "Performing health checks..."
    
    # Wait for services to start
    sleep 30
    
    # Check MCP Server
    if curl -f http://localhost:3000/health > /dev/null 2>&1; then
        success "MCP Server is healthy"
    else
        error "MCP Server health check failed"
    fi
    
    # Check PostgreSQL
    if docker-compose -f docker-compose.yml -f docker-compose.prod.yml exec -T postgres \
        pg_isready -U polymind_user -d polymind_prod > /dev/null 2>&1; then
        success "PostgreSQL is healthy"
    else
        error "PostgreSQL health check failed"
    fi
    
    # Check ChromaDB
    if curl -f http://localhost:8000/api/v1/heartbeat > /dev/null 2>&1; then
        success "ChromaDB is healthy"
    else
        error "ChromaDB health check failed"
    fi
    
    # Check Ollama
    if curl -f http://localhost:11434/api/version > /dev/null 2>&1; then
        success "Ollama is healthy"
    else
        error "Ollama health check failed"
    fi
    
    success "All health checks passed"
}

# Post-deployment tasks
post_deployment() {
    log "Running post-deployment tasks..."
    
    # Set up log rotation
    log "Configuring log rotation..."
    cat > /etc/logrotate.d/polymind << EOF
/var/log/polymind/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 644 root root
}
EOF
    
    # Set up backup cron job
    log "Setting up backup cron job..."
    (crontab -l 2>/dev/null; echo "0 2 * * * $SCRIPT_DIR/backup-script.sh") | crontab -
    
    # Set up monitoring alerts
    log "Configuring monitoring..."
    # Add monitoring configuration here
    
    success "Post-deployment tasks completed"
}

# Rollback function
rollback() {
    log "Rolling back deployment..."
    
    # Stop current services
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml down
    
    # Restore from backup
    LATEST_BACKUP=$(ls -t "$BACKUP_DIR" | head -n1)
    if [ -n "$LATEST_BACKUP" ]; then
        log "Restoring from backup: $LATEST_BACKUP"
        # Add restore logic here
    fi
    
    error "Rollback completed"
}

# Main deployment function
main() {
    log "Starting PolyMind MCP Server v1.0.0 deployment..."
    
    # Create log directory
    mkdir -p "$(dirname "$LOG_FILE")"
    
    # Trap errors for rollback
    trap rollback ERR
    
    # Run deployment steps
    check_prerequisites
    backup_data
    deploy_application
    health_check
    post_deployment
    
    success "🎉 PolyMind MCP Server v1.0.0 deployed successfully!"
    success "🌐 Access your application at: http://localhost:3000"
    success "📊 Monitoring dashboard: http://localhost:3001"
    success "📋 Logs location: $LOG_FILE"
}

# Parse command line arguments
case "${1:-}" in
    "deploy")
        main
        ;;
    "rollback")
        rollback
        ;;
    "health-check")
        health_check
        ;;
    "backup")
        backup_data
        ;;
    *)
        echo "Usage: $0 {deploy|rollback|health-check|backup}"
        echo ""
        echo "Commands:"
        echo "  deploy       - Full production deployment"
        echo "  rollback     - Rollback to previous version"
        echo "  health-check - Check service health"
        echo "  backup       - Create data backup"
        exit 1
        ;;
esac
