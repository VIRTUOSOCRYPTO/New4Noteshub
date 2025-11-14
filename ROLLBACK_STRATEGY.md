# Rollback Strategy

## Overview

This document outlines the rollback strategy for NotesHub to ensure safe deployments and quick recovery from issues.

## Table of Contents

- [Deployment Strategy](#deployment-strategy)
- [Version Management](#version-management)
- [Rollback Procedures](#rollback-procedures)
- [Database Migration Rollback](#database-migration-rollback)
- [Health Checks](#health-checks)
- [Monitoring & Alerts](#monitoring--alerts)
- [Communication Protocol](#communication-protocol)

## Deployment Strategy

### Blue-Green Deployment

We use blue-green deployment to enable zero-downtime deployments and quick rollbacks.

```
┌──────────────────────────────────────────────────────┐
│             Load Balancer / NGINX                    │
└────────────┬─────────────────────────────────────────┘
             │
        ┌────┴────┐
        │ Switch  │ (Can route to Blue or Green)
        └────┬────┘
             │
     ┌───────┴───────┐
     │               │
┌────▼────┐    ┌────▼────┐
│  BLUE   │    │  GREEN  │
│  v1.0.0 │    │  v1.0.1 │
│ (Live)  │    │ (Staged)│
└─────────┘    └─────────┘
```

### Deployment Flow

1. **Prepare Green Environment**
   - Deploy new version to green environment
   - Run database migrations (if any)
   - Warm up caches

2. **Health Checks**
   - Run automated health checks
   - Verify all services are running
   - Check database connectivity

3. **Smoke Tests**
   - Run critical path tests
   - Verify key functionality
   - Check API endpoints

4. **Switch Traffic**
   - Gradually route traffic to green (10%, 25%, 50%, 100%)
   - Monitor metrics and errors
   - Keep blue environment running

5. **Monitor**
   - Watch for 15-30 minutes
   - Check error rates, response times
   - Review logs for issues

6. **Commit or Rollback**
   - If successful: Decommission blue
   - If issues: Rollback to blue

## Version Management

### Version Tagging

```bash
# Tag format: v{major}.{minor}.{patch}
git tag -a v1.2.3 -m "Release version 1.2.3"
git push origin v1.2.3
```

### Version History

Keep the last 3 production versions deployed and ready:

```
v1.2.3 (current)
v1.2.2 (previous - ready for rollback)
v1.2.1 (archived - available if needed)
```

### Environment Configuration

```bash
# .env.production
APP_VERSION=1.2.3
DEPLOYMENT_ENV=blue
PREVIOUS_VERSION=1.2.2
```

## Rollback Procedures

### Immediate Rollback (< 5 minutes)

Use when critical issues are detected immediately after deployment.

```bash
#!/bin/bash
# scripts/rollback_immediate.sh

# 1. Switch load balancer back to blue environment
sudo nginx -t && sudo systemctl reload nginx

# 2. Verify blue is healthy
curl -f http://localhost:8001/health || exit 1

# 3. Log the rollback
echo "$(date): Rolled back to v${PREVIOUS_VERSION}" >> /var/log/deployments.log

# 4. Notify team
./scripts/notify_team.sh "🔴 ROLLBACK: Reverted to v${PREVIOUS_VERSION}"
```

**Steps:**

1. Switch load balancer to route all traffic to blue (previous version)
2. Verify blue environment is healthy
3. Stop green environment
4. Investigate issue in green environment
5. Document root cause

**Execution:**

```bash
cd /app
./scripts/rollback_immediate.sh
```

### Standard Rollback (< 30 minutes)

Use when issues are discovered within the monitoring period.

```bash
#!/bin/bash
# scripts/rollback_standard.sh

VERSION_TO_ROLLBACK=$1

if [ -z "$VERSION_TO_ROLLBACK" ]; then
    echo "Usage: ./rollback_standard.sh <version>"
    exit 1
fi

echo "Starting rollback to version $VERSION_TO_ROLLBACK..."

# 1. Switch traffic to previous version
./scripts/switch_traffic.sh blue

# 2. Rollback database migrations (if needed)
if [ -f "migrations/rollback_${VERSION_TO_ROLLBACK}.sql" ]; then
    echo "Rolling back database migrations..."
    python scripts/rollback_migrations.py $VERSION_TO_ROLLBACK
fi

# 3. Restart services
sudo supervisorctl restart all

# 4. Health check
./scripts/health_check.sh || exit 1

# 5. Verify
./scripts/smoke_tests.sh || exit 1

echo "✅ Rollback to $VERSION_TO_ROLLBACK completed successfully"
```

**Steps:**

1. Switch traffic to blue environment
2. Rollback database migrations (if required)
3. Restart services
4. Run health checks
5. Run smoke tests
6. Monitor for 15 minutes
7. Document and communicate

**Execution:**

```bash
cd /app
./scripts/rollback_standard.sh v1.2.2
```

### Emergency Rollback (Production Down)

Use when production is completely down.

**Steps:**

1. **Immediate Actions** (< 2 minutes)
   ```bash
   # Switch to last known good version
   ./scripts/emergency_rollback.sh
   
   # This script:
   # - Routes all traffic to blue
   # - Restarts all services
   # - Clears caches
   # - Restores from last backup if needed
   ```

2. **Verify** (< 3 minutes)
   ```bash
   # Check all services
   sudo supervisorctl status
   
   # Test critical endpoints
   curl -f http://localhost:8001/health
   curl -f http://localhost:8001/api/notes
   ```

3. **Communicate** (< 5 minutes)
   - Notify team via Slack/Email
   - Update status page
   - Log incident

4. **Monitor** (30 minutes)
   - Watch error rates
   - Check response times
   - Review logs

## Database Migration Rollback

### Migration Strategy

Every migration must have a rollback script:

```
migrations/
├── 001_add_email_verification.up.sql
├── 001_add_email_verification.down.sql
├── 002_add_indexes.up.sql
└── 002_add_indexes.down.sql
```

### Migration Template

**Up Migration:**
```sql
-- migrations/002_add_indexes.up.sql
CREATE INDEX idx_notes_department ON notes(department);
CREATE INDEX idx_notes_year ON notes(year);
CREATE INDEX idx_notes_uploaded_at ON notes(uploaded_at);
```

**Down Migration:**
```sql
-- migrations/002_add_indexes.down.sql
DROP INDEX IF EXISTS idx_notes_department;
DROP INDEX IF EXISTS idx_notes_year;
DROP INDEX IF EXISTS idx_notes_uploaded_at;
```

### Rollback Database

```bash
#!/bin/bash
# scripts/rollback_migrations.py

import sys
import pymongo
from pathlib import Path

def rollback_migration(version):
    # Load rollback script
    rollback_file = Path(f"migrations/{version}.down.sql")
    
    if not rollback_file.exists():
        print(f"No rollback script found for {version}")
        return False
    
    # Execute rollback
    with open(rollback_file) as f:
        rollback_sql = f.read()
    
    # Apply rollback
    # ... execute SQL
    
    print(f"✅ Rolled back migration {version}")
    return True

if __name__ == "__main__":
    version = sys.argv[1]
    rollback_migration(version)
```

### Backward-Compatible Migrations

Always write backward-compatible migrations when possible:

**❌ Breaking Change:**
```sql
-- Removes column - breaks old code
ALTER TABLE users DROP COLUMN old_field;
```

**✅ Backward Compatible:**
```sql
-- Step 1: Add new field
ALTER TABLE users ADD COLUMN new_field VARCHAR(255);

-- Step 2: Copy data
UPDATE users SET new_field = old_field;

-- Step 3: Deploy new code

-- Step 4 (next release): Remove old field
-- ALTER TABLE users DROP COLUMN old_field;
```

## Health Checks

### Health Check Endpoint

```python
# backend/routers/health.py

@router.get("/health")
async def health_check(database=Depends(get_database)):
    """
    Comprehensive health check
    Returns 200 if all systems operational
    """
    health_status = {
        "status": "healthy",
        "version": os.getenv("APP_VERSION", "unknown"),
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {}
    }
    
    # Check database
    try:
        await database.command("ping")
        health_status["checks"]["database"] = "ok"
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["checks"]["database"] = f"error: {str(e)}"
    
    # Check file storage
    if os.path.exists("uploads/notes"):
        health_status["checks"]["storage"] = "ok"
    else:
        health_status["status"] = "degraded"
        health_status["checks"]["storage"] = "error: directory not found"
    
    # Return appropriate status code
    status_code = 200 if health_status["status"] == "healthy" else 503
    return JSONResponse(content=health_status, status_code=status_code)
```

### Health Check Script

```bash
#!/bin/bash
# scripts/health_check.sh

BACKEND_URL="http://localhost:8001"

echo "Running health checks..."

# Check backend health
if ! curl -f -s "${BACKEND_URL}/health" > /dev/null; then
    echo "❌ Backend health check failed"
    exit 1
fi

echo "✅ Backend health check passed"

# Check frontend
if ! curl -f -s "http://localhost:3000" > /dev/null; then
    echo "❌ Frontend health check failed"
    exit 1
fi

echo "✅ Frontend health check passed"

# Check database
if ! mongosh --eval "db.adminCommand('ping')" > /dev/null 2>&1; then
    echo "❌ Database health check failed"
    exit 1
fi

echo "✅ Database health check passed"

echo "✅ All health checks passed"
exit 0
```

## Monitoring & Alerts

### Key Metrics to Monitor

1. **Error Rate**
   - Alert if > 1% (Warning)
   - Alert if > 5% (Critical)

2. **Response Time**
   - Alert if p95 > 1000ms (Warning)
   - Alert if p95 > 3000ms (Critical)

3. **Database Performance**
   - Alert if query time > 100ms average (Warning)
   - Alert if query time > 500ms average (Critical)

4. **System Resources**
   - CPU > 80% (Warning)
   - Memory > 90% (Critical)
   - Disk > 85% (Warning)

### Rollback Triggers

Automatically trigger rollback if:

1. Error rate > 10% for 5 minutes
2. Response time p95 > 5000ms for 5 minutes
3. Health check fails 3 times in a row
4. Database connection fails

## Communication Protocol

### During Rollback

1. **Immediate Notification** (< 1 minute)
   - Post in #incidents Slack channel
   - Update status page to "Investigating"

2. **Status Updates** (Every 5 minutes)
   - Progress on rollback
   - Current status
   - ETA for resolution

3. **Resolution** (When complete)
   - Confirm rollback successful
   - Update status page to "Operational"
   - Schedule post-mortem

### Template Messages

**Rollback Initiated:**
```
🔴 ROLLBACK IN PROGRESS
Version: v1.2.3 → v1.2.2
Reason: High error rate detected
Status: Switching traffic to previous version
ETA: 5 minutes
```

**Rollback Complete:**
```
✅ ROLLBACK COMPLETED
Version: Now running v1.2.2
Status: All systems operational
Impact: ~10 minutes of degraded performance
Next Steps: Post-mortem scheduled for tomorrow
```

## Post-Rollback Procedures

### Immediate (< 1 hour)

1. ✅ Verify all systems operational
2. ✅ Review logs for root cause
3. ✅ Document timeline of events
4. ✅ Update stakeholders

### Short-term (< 24 hours)

1. ✅ Conduct post-mortem meeting
2. ✅ Document root cause
3. ✅ Create action items
4. ✅ Update rollback procedures if needed

### Long-term (< 1 week)

1. ✅ Implement fixes
2. ✅ Add tests to prevent recurrence
3. ✅ Update monitoring/alerts
4. ✅ Share learnings with team

## Testing Rollback Procedures

### Monthly Rollback Drill

```bash
# Test rollback on staging environment
./scripts/rollback_drill.sh

# This script:
# 1. Deploys a test version
# 2. Simulates an issue
# 3. Executes rollback
# 4. Verifies system health
# 5. Reports results
```

### Checklist

- [ ] Rollback scripts are tested and work
- [ ] Team knows how to execute rollback
- [ ] Health checks are reliable
- [ ] Monitoring alerts are configured
- [ ] Communication channels are set up
- [ ] Database rollback scripts exist
- [ ] Backups are recent and verified

## Best Practices

1. **Always Have a Rollback Plan**
   - Never deploy without knowing how to rollback
   - Document rollback steps before deployment

2. **Keep Previous Version Running**
   - Don't tear down old environment immediately
   - Wait 24-48 hours before decommissioning

3. **Test Rollback Procedures**
   - Run monthly drills
   - Keep procedures up-to-date

4. **Automate Where Possible**
   - Use scripts for rollbacks
   - Minimize manual steps

5. **Monitor Closely After Deployment**
   - Watch for 30 minutes minimum
   - Have team available

6. **Document Everything**
   - Log all rollbacks
   - Document lessons learned

7. **Backward Compatible Changes**
   - Prefer additive changes
   - Deprecate before removing

## Quick Reference

### Rollback Commands

```bash
# Immediate rollback (traffic switch only)
./scripts/rollback_immediate.sh

# Standard rollback (with migrations)
./scripts/rollback_standard.sh v1.2.2

# Emergency rollback (production down)
./scripts/emergency_rollback.sh

# Health check
./scripts/health_check.sh

# View current version
curl http://localhost:8001/health | jq .version
```

### Support Contacts

- **On-Call Engineer**: [phone/slack]
- **DevOps Team**: #devops-alerts
- **Incident Channel**: #incidents

---

**Last Updated**: January 2025  
**Version**: 1.0.0  
**Next Review**: February 2025
