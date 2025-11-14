#!/bin/bash
# Health Check Script
# Verifies all services are operational

set -e

BACKEND_URL="http://localhost:8001"
FRONTEND_URL="http://localhost:3000"

echo "🏥 Running health checks..."
echo ""

# Function to check URL
check_url() {
    local name=$1
    local url=$2
    
    if curl -f -s --max-time 5 "$url" > /dev/null 2>&1; then
        echo "✅ $name is healthy"
        return 0
    else
        echo "❌ $name health check failed"
        return 1
    fi
}

# Track failures
FAILURES=0

# Check backend health endpoint
echo "Checking backend..."
if ! check_url "Backend" "${BACKEND_URL}/health"; then
    FAILURES=$((FAILURES + 1))
fi

# Check frontend
echo "Checking frontend..."
if ! check_url "Frontend" "$FRONTEND_URL"; then
    FAILURES=$((FAILURES + 1))
fi

# Check database (if mongosh is available)
if command -v mongosh &> /dev/null; then
    echo "Checking database..."
    if mongosh --eval "db.adminCommand('ping')" --quiet > /dev/null 2>&1; then
        echo "✅ Database is healthy"
    else
        echo "❌ Database health check failed"
        FAILURES=$((FAILURES + 1))
    fi
else
    echo "⚠️  mongosh not found, skipping database check"
fi

# Check supervisor services
if command -v supervisorctl &> /dev/null; then
    echo "Checking supervisor services..."
    if supervisorctl status | grep -q "RUNNING"; then
        echo "✅ Supervisor services are running"
    else
        echo "❌ Some supervisor services are not running"
        supervisorctl status
        FAILURES=$((FAILURES + 1))
    fi
fi

echo ""
if [ $FAILURES -eq 0 ]; then
    echo "✅ All health checks passed"
    exit 0
else
    echo "❌ $FAILURES health check(s) failed"
    exit 1
fi
