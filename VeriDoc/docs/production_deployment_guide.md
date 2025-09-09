# VeriDoc Production Deployment Guide

## Overview

This guide provides comprehensive instructions for deploying VeriDoc in production environments with enterprise-grade security, monitoring, and compliance features.

## Prerequisites

### System Requirements

#### Minimum Requirements
- **OS**: Windows 10/11, Ubuntu 18.04+, or macOS 10.15+
- **CPU**: 4-core processor (2.5 GHz minimum)
- **RAM**: 8 GB
- **Storage**: 10 GB free space
- **Network**: 10 Mbps stable connection

#### Recommended Production Requirements
- **OS**: Windows Server 2019+, Ubuntu 20.04+, RHEL 8+
- **CPU**: 8-core processor (3.0 GHz+)
- **RAM**: 16 GB+
- **Storage**: 50 GB SSD storage
- **Network**: 100 Mbps+ with redundancy

### Software Dependencies

```bash
# Core Dependencies
pip install PySide6>=6.6.0 numpy>=1.24.0 opencv-python>=4.8.0 Pillow>=10.0.0

# Optional AI/ML Dependencies (for enhanced features)
pip install ultralytics>=8.0.0 mediapipe>=0.10.0 scikit-learn>=1.3.0

# Development/Testing Dependencies
pip install pytest>=7.4.0 black>=23.0.0 flake8>=6.0.0
```

### Security Requirements

- **Secure Boot**: Enabled on UEFI systems
- **TPM**: Available for key storage (recommended)
- **Firewall**: Configured with VeriDoc-specific rules
- **SSL/TLS**: Valid certificates for secure communication

## Installation

### Automated Installation

```bash
# Clone the repository
git clone https://github.com/your-org/veridoc.git
cd veridoc

# Run automated setup
python setup_production.py

# Follow the interactive setup wizard
```

### Manual Installation

```bash
# 1. Create production environment
python -m venv veridoc_prod
source veridoc_prod/bin/activate  # On Windows: veridoc_prod\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp config/production_config.json.example config/production_config.json
# Edit configuration file with production values

# 4. Initialize security
python -m core.security_manager --init

# 5. Run initial tests
python -m tests.production_test_suite --smoke

# 6. Start application
python main.py --production
```

## Configuration

### Production Configuration

Create `config/production_config.json`:

```json
{
  "environment": "production",
  "security": {
    "audit_enabled": true,
    "encryption_at_rest": true,
    "session_timeout_minutes": 15,
    "max_login_attempts": 3,
    "secure_boot_required": true
  },
  "performance": {
    "max_worker_threads": 8,
    "cache_enabled": true,
    "memory_limit_mb": 2048,
    "batch_processing_enabled": true
  },
  "logging": {
    "console_level": "WARNING",
    "file_level": "INFO",
    "audit_level": "DEBUG",
    "log_rotation": true,
    "max_log_size_mb": 100
  },
  "monitoring": {
    "enabled": true,
    "metrics_collection_interval": 60,
    "alerts_enabled": true,
    "health_check_endpoint": "/health"
  }
}
```

### Environment Variables

```bash
# Security
export VERIDOC_ENCRYPTION_KEY="your-256-bit-key"
export VERIDOC_AUDIT_DB_PATH="/secure/audit.db"
export VERIDOC_TLS_CERT_PATH="/ssl/veridoc.crt"
export VERIDOC_TLS_KEY_PATH="/ssl/veridoc.key"

# Performance
export VERIDOC_MAX_WORKERS="8"
export VERIDOC_MEMORY_LIMIT="2048"
export VERIDOC_CACHE_SIZE="512"

# Monitoring
export VERIDOC_METRICS_PORT="9090"
export VERIDOC_HEALTH_PORT="8080"
```

## Security Configuration

### 1. Certificate Management

```bash
# Generate self-signed certificate (for testing only)
openssl req -x509 -newkey rsa:4096 -keyout veridoc.key -out veridoc.crt -days 365 -nodes

# For production, use CA-signed certificates
# Place certificates in /etc/ssl/veridoc/
```

### 2. User Authentication Setup

```bash
# Initialize user database
python -c "from core.security_manager import ProductionSecurityManager; sm = ProductionSecurityManager(); sm.initialize_user_db()"

# Create admin user
python -c "
from core.security_manager import ProductionSecurityManager
sm = ProductionSecurityManager()
sm.create_user('admin', 'secure_password', roles=['admin', 'security'])
"
```

### 3. Security Policy Configuration

```json
{
  "password_policy": {
    "min_length": 12,
    "require_uppercase": true,
    "require_lowercase": true,
    "require_numbers": true,
    "require_special_chars": true,
    "max_age_days": 90
  },
  "session_policy": {
    "max_concurrent_sessions": 3,
    "idle_timeout_minutes": 30,
    "absolute_timeout_hours": 8,
    "require_mfa": true
  }
}
```

## Deployment Options

### 1. Standalone Deployment

```bash
# Build standalone executable
python deploy/build_standalone.py

# Deploy
./dist/VeriDoc --config config/production_config.json
```

### 2. Docker Deployment

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . /app

RUN pip install -r requirements.txt
RUN python setup_production.py

EXPOSE 8080 9090
CMD ["python", "main.py", "--production"]
```

```bash
# Build and run
docker build -t veridoc .
docker run -p 8080:8080 -p 9090:9090 veridoc
```

### 3. Kubernetes Deployment

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: veridoc
spec:
  replicas: 3
  selector:
    matchLabels:
      app: veridoc
  template:
    metadata:
      labels:
        app: veridoc
    spec:
      containers:
      - name: veridoc
        image: veridoc:latest
        ports:
        - containerPort: 8080
        env:
        - name: VERIDOC_ENV
          value: "production"
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
```

### 4. Cloud Deployment (AWS/Azure/GCP)

```bash
# AWS EC2 example
aws ec2 run-instances \
  --image-id ami-12345678 \
  --instance-type t3.medium \
  --security-group-ids sg-12345678 \
  --user-data file://deploy/aws_userdata.sh
```

## Monitoring and Observability

### 1. Application Metrics

```python
# Enable metrics collection
from core.performance_monitor import PerformanceMonitor

monitor = PerformanceMonitor()
monitor.start_collection()

# Metrics available at /metrics endpoint
# - Request latency
# - Error rates
# - Resource usage
# - Processing throughput
```

### 2. Health Checks

```bash
# Health check endpoint
curl http://localhost:8080/health

# Response:
{
  "status": "healthy",
  "version": "1.0.0",
  "uptime": "2d 4h 32m",
  "services": {
    "database": "healthy",
    "cache": "healthy",
    "security": "healthy"
  }
}
```

### 3. Log Aggregation

```bash
# Configure log shipping to ELK stack
# File: /etc/rsyslog.d/veridoc.conf
if $programname == 'veridoc' then @logstash:514

# Or use fluentd
<match veridoc.**>
  @type elasticsearch
  host elasticsearch
  port 9200
  logstash_format true
</match>
```

## Backup and Recovery

### 1. Automated Backups

```bash
# Configure automated backups
0 2 * * * /path/to/veridoc/deploy/backup.sh

# Backup script content:
#!/bin/bash
BACKUP_DIR="/backups/veridoc/$(date +%Y%m%d)"
mkdir -p $BACKUP_DIR

# Backup application data
cp -r /app/data $BACKUP_DIR/
cp -r /app/config $BACKUP_DIR/

# Backup database
pg_dump veridoc > $BACKUP_DIR/database.sql

# Compress and encrypt
tar -czf $BACKUP_DIR.tar.gz $BACKUP_DIR
openssl enc -aes-256-cbc -salt -in $BACKUP_DIR.tar.gz -out $BACKUP_DIR.enc
```

### 2. Disaster Recovery

```bash
# Recovery procedure
# 1. Restore from backup
openssl enc -d -aes-256-cbc -in backup.enc -out backup.tar.gz
tar -xzf backup.tar.gz

# 2. Restore application files
cp -r backup/data /app/
cp -r backup/config /app/

# 3. Restore database
psql -d veridoc < backup/database.sql

# 4. Verify integrity
python -m tests.production_test_suite --smoke
```

## Performance Tuning

### 1. Memory Optimization

```python
# Configure memory limits
config = get_config()
config.processing.memory_limit_mb = 2048
config.performance.cache_max_size_mb = 512

# Enable garbage collection tuning
import gc
gc.set_threshold(1000, 10, 10)
```

### 2. CPU Optimization

```python
# Configure thread pools
config.performance.max_worker_threads = 8
config.performance.thread_pool_size = 16

# Enable CPU affinity for critical threads
import os
os.sched_setaffinity(0, {0, 1, 2, 3})  # Pin to first 4 CPUs
```

### 3. I/O Optimization

```python
# Configure I/O settings
config.performance.batch_write_size = 100
config.performance.file_buffer_size_kb = 256

# Enable async I/O
import asyncio
asyncio.get_event_loop().set_default_executor(
    concurrent.futures.ThreadPoolExecutor(max_workers=8)
)
```

## Troubleshooting

### Common Issues

#### 1. Application Won't Start

```bash
# Check logs
tail -f logs/veridoc.log

# Verify configuration
python -c "from config.production_config import get_config; print(get_config())"

# Check dependencies
python -c "import PySide6, cv2, numpy; print('Dependencies OK')"
```

#### 2. Performance Issues

```bash
# Monitor resource usage
top -p $(pgrep -f veridoc)

# Check memory usage
python -c "import psutil; print(psutil.virtual_memory())"

# Profile application
python -m cProfile -o profile.out main.py
```

#### 3. Security Alerts

```bash
# Check security status
python -c "from core.security_manager import ProductionSecurityManager; sm = ProductionSecurityManager(); print(sm.get_security_status())"

# Review audit logs
python -c "from core.audit_logger import AuditLogger; logger = AuditLogger(); logger.generate_report()"
```

## Compliance and Auditing

### 1. GDPR Compliance

- **Data Minimization**: Only collect necessary data
- **Consent Management**: Implement user consent flows
- **Right to Deletion**: Provide data deletion mechanisms
- **Data Portability**: Enable data export features

### 2. ICAO Compliance

- **Document Standards**: Adhere to Doc 9303 specifications
- **Quality Assurance**: Implement automated compliance checks
- **Audit Trails**: Maintain comprehensive processing logs
- **Security Controls**: Implement access controls and encryption

### 3. Audit Procedures

```bash
# Generate compliance report
python deploy/compliance_report.py --period 30d --format pdf

# Review access logs
python -c "
from core.audit_logger import AuditLogger
logger = AuditLogger()
logger.generate_access_report(start_date='2024-01-01', end_date='2024-01-31')
"
```

## Support and Maintenance

### 1. Regular Maintenance Tasks

```bash
# Daily tasks
0 6 * * * /path/to/veridoc/deploy/daily_maintenance.sh

# Weekly tasks
0 7 * * 1 /path/to/veridoc/deploy/weekly_maintenance.sh

# Monthly tasks
0 8 1 * * /path/to/veridoc/deploy/monthly_maintenance.sh
```

### 2. Update Procedures

```bash
# 1. Backup current installation
python deploy/production_deployer.py --backup

# 2. Download and test updates
python deploy/update_system.py --test

# 3. Deploy updates
python deploy/production_deployer.py --update

# 4. Verify deployment
python -m tests.production_test_suite --smoke
```

### 3. Support Contacts

- **Technical Support**: support@veridoc.com
- **Security Issues**: security@veridoc.com
- **Documentation**: docs.veridoc.com
- **Emergency Hotline**: +1-800-VERIDOC

## Appendices

### A. Configuration Reference

Complete configuration schema and examples.

### B. API Documentation

REST API endpoints and usage examples.

### C. Integration Guides

Third-party system integration procedures.

### D. Security Checklist

Comprehensive security hardening checklist.