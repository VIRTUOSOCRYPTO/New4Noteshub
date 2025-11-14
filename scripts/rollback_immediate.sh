#!/bin/bash
# Immediate Rollback Script
# Routes traffic back to previous version (blue environment)

set -e

echo "🔄 Starting immediate rollback..."

# Get previous version from environment
PREVIOUS_VERSION=${PREVIOUS_VERSION:-"unknown"}
echo "Rolling back to version: $PREVIOUS_VERSION"

# 1. Switch NGINX to route to blue environment
echo "Switching traffic to blue environment..."
if [ -f /etc/nginx/sites-available/noteshub ]; then
    # Backup current config
    cp /etc/nginx/sites-available/noteshub /etc/nginx/sites-available/noteshub.backup
    
    # Switch upstream to blue
    sed -i 's/server green:8001/server blue:8001/g' /etc/nginx/sites-available/noteshub
    
    # Test and reload
    nginx -t && systemctl reload nginx
    echo "✅ Traffic switched to blue environment"
else
    echo "⚠️  NGINX config not found, skipping..."
fi

# 2. Verify blue environment health
echo "Checking blue environment health..."
for i in {1..5}; do
    if curl -f -s http://localhost:8001/health > /dev/null 2>&1; then
        echo "✅ Blue environment is healthy"
        break
    fi
    echo "Attempt $i/5: Blue environment not ready, waiting..."
    sleep 2
done

# 3. Log the rollback
LOG_FILE="/var/log/noteshub/deployments.log"
mkdir -p /var/log/noteshub
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ): ROLLBACK to v${PREVIOUS_VERSION}" >> "$LOG_FILE"

# 4. Send notification (if notification script exists)
if [ -f "./scripts/notify_team.sh" ]; then
    ./scripts/notify_team.sh "🔴 ROLLBACK: Reverted to v${PREVIOUS_VERSION}"
fi

echo ""
echo "✅ Immediate rollback completed successfully"
echo "Current version: $PREVIOUS_VERSION"
echo "Please investigate the issue in green environment"
