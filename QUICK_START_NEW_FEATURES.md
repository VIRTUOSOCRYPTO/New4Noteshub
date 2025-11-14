# Quick Start Guide - New Features

## \ud83d\ude80 Getting Started with New Features

### 1. Backup System

**Create a Manual Backup:**
```bash
# Via Python script (recommended)
cd /app/backend
python3 -c "from services.backup_service import backup_service; print(backup_service.create_backup())"

# Or via API (requires admin token)
curl -X POST http://localhost:8001/api/admin/backup/create \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

**List Available Backups:**
```bash
python3 /app/scripts/restore_backup.py list
```

**Restore from Backup:**
```bash
python3 /app/scripts/restore_backup.py restore --backup <backup_name>
```

---

### 2. Feature Flags

**Enable a Feature for 50% of Users:**
```python
# In your code
from services.feature_flags import feature_flags

# Check if feature is enabled for current user
if await feature_flags.is_enabled("new_ui", user_id=user_id):
    # Show new UI
    return render_new_ui()
else:
    # Show old UI
    return render_old_ui()
```

**Manage via Admin API:**
```bash
# Create a feature flag
curl -X POST http://localhost:8001/api/admin/feature-flags \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "new_ui",
    "description": "New user interface",
    "status": "rollout",
    "rollout_percentage": 50
  }'

# Update to 100% (full rollout)
curl -X PATCH http://localhost:8001/api/admin/feature-flags/new_ui \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "enabled", "rollout_percentage": 100}'
```

---

### 3. A/B Testing

**Run a Button Color Test:**
```python
# In your code
from services.ab_testing import ab_testing

# Get variant for user
variant = await ab_testing.get_variant("button_color_test", user_id)

# Track when user clicks
if button_clicked:
    await ab_testing.track_metric(
        experiment_name="button_color_test",
        user_id=user_id,
        metric_name="click_through_rate",
        value=1.0
    )
```

**Create Experiment via API:**
```bash
curl -X POST http://localhost:8001/api/admin/experiments \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "button_color_test",
    "description": "Test blue vs green button",
    "variants": [
      {"name": "control", "traffic_percentage": 50},
      {"name": "green", "traffic_percentage": 50}
    ],
    "metrics": ["click_through_rate", "conversion_rate"]
  }'

# Start the experiment
curl -X PATCH http://localhost:8001/api/admin/experiments/button_color_test/status \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "running"}'

# Get results
curl http://localhost:8001/api/admin/experiments/button_color_test/results \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

---

### 4. Load Testing

**Quick Load Test:**
```bash
cd /app/load_tests

# Install locust if not already installed
pip install locust

# Run test with 50 users for 2 minutes
locust -f locustfile.py \
  --host=http://localhost:8001 \
  --users 50 \
  --spawn-rate 5 \
  --run-time 2m \
  --headless \
  --html=report.html
```

**Web UI Mode:**
```bash
locust -f locustfile.py --host=http://localhost:8001

# Open browser to http://localhost:8089
```

---

### 5. Log Search

**Search Error Logs:**
```bash
curl "http://localhost:8001/api/admin/logs/search?log_file=error.log&level=ERROR&limit=20" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

**Get Recent Errors:**
```bash
curl "http://localhost:8001/api/admin/logs/errors?count=10" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

---

### 6. Performance Monitoring

**View Endpoint Performance:**
```bash
# Get last 60 minutes of endpoint metrics
curl "http://localhost:8001/api/admin/performance/endpoints?minutes=60" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"

# Get database query performance
curl "http://localhost:8001/api/admin/performance/queries?minutes=60" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"

# Check for alerts
curl "http://localhost:8001/api/admin/performance/alerts" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

---

### 7. System Health Check

**Quick Health Check:**
```bash
curl http://localhost:8001/api/admin/system/health \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

This returns:
- Overall health score (0-100)
- Active alerts
- Log statistics
- System status

---

### 8. Virus Scanning

**Check Quarantine:**
```bash
curl http://localhost:8001/api/admin/security/quarantine \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

Virus scanning is automatic on all file uploads. Infected files are quarantined.

---

## Environment Setup

Copy and configure:
```bash
cp /app/.env.example /app/backend/.env
```

Edit `/app/backend/.env` with your settings.

---

## Admin Access

To use admin endpoints, you need an admin user. Set admin user IDs in environment:

```bash
# In .env file
ADMIN_USER_IDS=507f1f77bcf86cd799439011,507f191e810c19729de860ea
```

Or check admin status:
```bash
curl http://localhost:8001/api/admin/check \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Testing Everything

**Run this test script:**
```bash
#!/bin/bash

# Get admin token (replace with actual login)
TOKEN="your_admin_token_here"

echo "1. Testing Health..."
curl -s http://localhost:8001/api/health

echo -e "\n\n2. Creating Backup..."
curl -s -X POST http://localhost:8001/api/admin/backup/create \
  -H "Authorization: Bearer $TOKEN"

echo -e "\n\n3. Listing Backups..."
curl -s http://localhost:8001/api/admin/backup/list \
  -H "Authorization: Bearer $TOKEN"

echo -e "\n\n4. Creating Feature Flag..."
curl -s -X POST http://localhost:8001/api/admin/feature-flags \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"test_feature","description":"Test","status":"enabled"}'

echo -e "\n\n5. System Health..."
curl -s http://localhost:8001/api/admin/system/health \
  -H "Authorization: Bearer $TOKEN"

echo -e "\n\nAll tests complete!"
```

---

## Documentation

- **Full Implementation Details**: `/app/IMPLEMENTATION_COMPLETE.md`
- **CDN Setup**: `/app/CDN_SETUP_GUIDE.md`
- **Load Testing**: `/app/load_tests/README.md`
- **Environment Config**: `/app/.env.example`

---

## Support

**Check Logs:**
```bash
# Application logs
tail -f /app/logs/app.log

# Error logs
tail -f /app/logs/error.log

# Backend service logs
sudo supervisorctl tail -f backend
```

**Restart Services:**
```bash
sudo supervisorctl restart all
```

---

## What's Next?

See `/app/IMPLEMENTATION_COMPLETE.md` for:
- Detailed feature documentation
- API endpoint reference
- Configuration options
- Advanced usage examples
- Remaining improvements (low priority)

---

## Summary

\u2705 8/8 High + Medium priority features implemented and ready to use!

Happy coding! \ud83d\ude80
