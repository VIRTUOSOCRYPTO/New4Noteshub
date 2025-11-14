#!/bin/bash
# Standard Rollback Script
# Includes database migration rollback

set -e

VERSION_TO_ROLLBACK=$1

if [ -z "$VERSION_TO_ROLLBACK" ]; then
    echo "Usage: ./rollback_standard.sh <version>"
    echo "Example: ./rollback_standard.sh v1.2.2"
    exit 1
fi

echo "🔄 Starting standard rollback to $VERSION_TO_ROLLBACK..."

# 1. Switch traffic to blue environment
echo "Step 1: Switching traffic to blue environment..."
if [ -f "./scripts/switch_traffic.sh" ]; then
    ./scripts/switch_traffic.sh blue
else
    echo "⚠️  switch_traffic.sh not found, manual switch required"
fi

# 2. Rollback database migrations (if needed)
if [ -f "scripts/rollback_migrations.py" ]; then
    echo "Step 2: Rolling back database migrations..."
    python scripts/rollback_migrations.py "$VERSION_TO_ROLLBACK"
else
    echo "Step 2: No migration rollback script found, skipping..."
fi

# 3. Restart services
echo "Step 3: Restarting services..."
if command -v supervisorctl &> /dev/null; then
    sudo supervisorctl restart all
    sleep 5
fi

# 4. Health check
echo "Step 4: Running health checks..."
if [ -f "./scripts/health_check.sh" ]; then
    if ! ./scripts/health_check.sh; then
        echo "❌ Health check failed!"
        exit 1
    fi
else
    echo "⚠️  health_check.sh not found"
    # Basic health check
    if ! curl -f -s http://localhost:8001/health > /dev/null 2>&1; then
        echo "❌ Backend health check failed!"
        exit 1
    fi
fi

# 5. Run smoke tests
echo "Step 5: Running smoke tests..."
if [ -f "./scripts/smoke_tests.sh" ]; then
    if ! ./scripts/smoke_tests.sh; then
        echo "⚠️  Some smoke tests failed, but rollback is complete"
    fi
fi

# 6. Log the rollback
LOG_FILE="/var/log/noteshub/deployments.log"
mkdir -p /var/log/noteshub
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ): STANDARD ROLLBACK to $VERSION_TO_ROLLBACK completed" >> "$LOG_FILE"

echo ""
echo "✅ Rollback to $VERSION_TO_ROLLBACK completed successfully"
echo "Please monitor the application for the next 30 minutes"
