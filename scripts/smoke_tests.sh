#!/bin/bash
# Smoke Tests
# Quick tests to verify critical functionality

set -e

BACKEND_URL="http://localhost:8001"

echo "🔥 Running smoke tests..."
echo ""

FAILURES=0

# Test 1: Health endpoint
echo "Test 1: Health endpoint"
if curl -f -s "${BACKEND_URL}/health" | jq -e '.status == "healthy"' > /dev/null 2>&1; then
    echo "✅ Health endpoint working"
else
    echo "❌ Health endpoint failed"
    FAILURES=$((FAILURES + 1))
fi

# Test 2: API root
echo "Test 2: API root endpoint"
if curl -f -s "${BACKEND_URL}/api" > /dev/null 2>&1; then
    echo "✅ API root accessible"
else
    echo "❌ API root failed"
    FAILURES=$((FAILURES + 1))
fi

# Test 3: Notes endpoint (should require auth but not error)
echo "Test 3: Notes endpoint (unauthenticated)"
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "${BACKEND_URL}/api/notes")
if [ "$STATUS" -eq 200 ] || [ "$STATUS" -eq 401 ]; then
    echo "✅ Notes endpoint responding correctly"
else
    echo "❌ Notes endpoint returned unexpected status: $STATUS"
    FAILURES=$((FAILURES + 1))
fi

# Test 4: Static file serving (if applicable)
echo "Test 4: Static files"
if [ -d "/app/frontend/build" ] || [ -d "/app/frontend/dist" ]; then
    if curl -f -s http://localhost:3000 > /dev/null 2>&1; then
        echo "✅ Static files serving correctly"
    else
        echo "❌ Static files not accessible"
        FAILURES=$((FAILURES + 1))
    fi
else
    echo "⚠️  Frontend build directory not found, skipping"
fi

echo ""
if [ $FAILURES -eq 0 ]; then
    echo "✅ All smoke tests passed"
    exit 0
else
    echo "❌ $FAILURES smoke test(s) failed"
    exit 1
fi
