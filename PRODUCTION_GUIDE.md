# 🚀 Production Deployment Guide - PolyMind MCP Server v1.0.0

## 📋 **Production Checklist**

### ✅ **Pre-Deployment**
- [ ] Code reviewed and tested
- [ ] All MCP tools validated (30/30 ✅)
- [ ] Docker images built and tested
- [ ] Environment variables configured
- [ ] Backup strategy implemented
- [ ] Monitoring setup complete

### ✅ **Infrastructure Requirements**

#### 🖥️ **Minimum System Requirements**
- **CPU**: 4 cores (8 recommended)
- **RAM**: 8GB (16GB recommended)
- **Storage**: 50GB SSD (100GB recommended)
- **Network**: 1Gbps connection
- **OS**: Ubuntu 20.04+ / CentOS 8+ / Windows Server 2019+

#### 🐳 **Docker Requirements**
- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **Available Ports**: 3000, 5432, 8000, 11434

## 🏗️ **Deployment Options**

### 🔥 **Option 1: Docker Compose (Recommended)**

#### 📁 **Production Setup**
```bash
# Clone repository
git clone https://github.com/maithanhduyan/polymind.git
cd polymind/mcp-server

# Create production environment file
cp .env.example .env.production

# Edit production configuration
nano .env.production
```

#### 🔧 **Environment Configuration**
```bash
# .env.production
NODE_ENV=production
MCP_PORT=3000

# PostgreSQL Configuration
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=polymind_prod
POSTGRES_USER=polymind_user
POSTGRES_PASSWORD=your_secure_password_here

# ChromaDB Configuration
CHROMADB_HOST=chromadb
CHROMADB_PORT=8000

# Ollama Configuration
OLLAMA_HOST=ollama
OLLAMA_PORT=11434
OLLAMA_MODEL=nomic-embed-text

# Logging
LOG_LEVEL=info
LOG_FILE=/var/log/polymind/app.log
```

#### 🚀 **Production Deployment**
```bash
# Build production images
docker-compose -f docker-compose.yml -f docker-compose.prod.yml build

# Start production services
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Verify deployment
docker-compose ps
docker-compose logs --tail=100
```

### 🎯 **Option 2: Kubernetes Deployment**

#### 📄 **Kubernetes Manifests**
```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: polymind-prod

---
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: polymind-mcp-server
  namespace: polymind-prod
spec:
  replicas: 3
  selector:
    matchLabels:
      app: polymind-mcp-server
  template:
    metadata:
      labels:
        app: polymind-mcp-server
    spec:
      containers:
      - name: mcp-server
        image: polymind/mcp-server:v1.0.0
        ports:
        - containerPort: 3000
        env:
        - name: NODE_ENV
          value: production
        - name: POSTGRES_HOST
          value: postgres-service
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
```

#### 🎛️ **Deploy to Kubernetes**
```bash
# Apply Kubernetes manifests
kubectl apply -f k8s/

# Check deployment
kubectl get pods -n polymind-prod
kubectl logs -f deployment/polymind-mcp-server -n polymind-prod
```

## 🔒 **Security Configuration**

### 🛡️ **Network Security**
```bash
# Firewall rules (Ubuntu/CentOS)
# Allow only necessary ports
ufw allow 3000/tcp  # MCP Server
ufw allow 22/tcp    # SSH
ufw deny 5432/tcp   # PostgreSQL (internal only)
ufw deny 8000/tcp   # ChromaDB (internal only)
ufw deny 11434/tcp  # Ollama (internal only)
```

### 🔐 **SSL/TLS Configuration**
```nginx
# nginx.conf
server {
    listen 443 ssl http2;
    server_name mcp.yourdomain.com;
    
    ssl_certificate /etc/ssl/certs/mcp.crt;
    ssl_certificate_key /etc/ssl/private/mcp.key;
    
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 🔑 **Environment Security**
```bash
# Secure environment variables
export POSTGRES_PASSWORD=$(openssl rand -base64 32)
export JWT_SECRET=$(openssl rand -base64 64)
export API_KEY=$(openssl rand -base64 32)

# Store in secure location
echo "POSTGRES_PASSWORD=$POSTGRES_PASSWORD" >> /etc/polymind/secrets.env
chmod 600 /etc/polymind/secrets.env
```

## 📊 **Monitoring & Logging**

### 📈 **Health Checks**
```bash
# Built-in health endpoints
curl http://localhost:3000/health
curl http://localhost:8000/api/v1/heartbeat  # ChromaDB
curl http://localhost:11434/api/version      # Ollama

# Database health
docker exec polymind_postgres psql -U postgres -c "SELECT version();"
```

### 📋 **Logging Configuration**
```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  mcp-server:
    logging:
      driver: "json-file"
      options:
        max-size: "100m"
        max-file: "5"
    volumes:
      - ./logs:/var/log/polymind
```

### 🔍 **Monitoring Stack**
```yaml
# monitoring/docker-compose.yml
version: '3.8'
services:
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
  
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=your_grafana_password
```

## 🚨 **Backup Strategy**

### 💾 **Database Backup**
```bash
#!/bin/bash
# backup-script.sh

# PostgreSQL backup
docker exec polymind_postgres pg_dump -U postgres polymind_prod > backup_$(date +%Y%m%d_%H%M%S).sql

# ChromaDB backup
docker cp polymind_chromadb:/chroma/chroma_data ./backup/chromadb_$(date +%Y%m%d_%H%M%S)

# Ollama models backup
docker cp polymind_ollama:/root/.ollama ./backup/ollama_$(date +%Y%m%d_%H%M%S)
```

### ⏰ **Automated Backups**
```bash
# Add to crontab
crontab -e

# Daily backup at 2 AM
0 2 * * * /opt/polymind/backup-script.sh

# Weekly full backup
0 3 * * 0 /opt/polymind/full-backup-script.sh
```

## 🔄 **CI/CD Pipeline**

### 🏃 **GitHub Actions**
```yaml
# .github/workflows/production.yml
name: Production Deployment

on:
  push:
    tags:
      - 'v*'

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Build Docker images
      run: |
        docker build -t polymind/mcp-server:${{ github.ref_name }} .
    
    - name: Push to registry
      run: |
        docker push polymind/mcp-server:${{ github.ref_name }}
    
    - name: Deploy to production
      run: |
        # Your deployment script here
        ./deploy-production.sh
```

## 🆘 **Troubleshooting**

### 🔧 **Common Issues**

#### ❌ **Service Won't Start**
```bash
# Check logs
docker-compose logs mcp-server

# Check resource usage
docker stats

# Restart services
docker-compose restart
```

#### ❌ **Database Connection Issues**
```bash
# Test PostgreSQL connection
docker exec -it polymind_postgres psql -U postgres

# Check network connectivity
docker network ls
docker network inspect polymind_default
```

#### ❌ **Memory Issues**
```bash
# Check memory usage
free -h
docker stats --no-stream

# Adjust memory limits in docker-compose.yml
services:
  mcp-server:
    deploy:
      resources:
        limits:
          memory: 2G
```

### 📞 **Support Contacts**
- **Technical Issues**: Create GitHub issue
- **Deployment Help**: Check documentation
- **Emergency**: Follow incident response plan

## 📈 **Performance Tuning**

### ⚡ **Optimization Tips**
```bash
# PostgreSQL tuning
# Edit postgresql.conf
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB

# ChromaDB optimization
# Increase batch size for bulk operations
CHROMADB_BATCH_SIZE=1000

# Ollama optimization
# Use GPU acceleration if available
OLLAMA_GPU_LAYERS=32
```

### 📊 **Performance Metrics**
- **Response Time**: < 200ms for simple queries
- **Throughput**: 1000+ requests/minute
- **Memory Usage**: < 2GB under normal load
- **CPU Usage**: < 50% under normal load

---

## ✅ **Post-Deployment Verification**

### 🧪 **Production Testing**
```bash
# Test all MCP tools
npm run test:production

# Load testing
npm run test:load

# Security scanning
npm run test:security
```

### 📋 **Go-Live Checklist**
- [ ] All services running and healthy
- [ ] Database connections working
- [ ] MCP tools responding correctly
- [ ] SSL certificates valid
- [ ] Monitoring alerts configured
- [ ] Backup system tested
- [ ] Performance within acceptable limits
- [ ] Security scans passed

---

**🎉 Your PolyMind MCP Server v1.0.0 is now production ready!**
