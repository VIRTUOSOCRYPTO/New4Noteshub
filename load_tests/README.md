# Load Testing with Locust

This directory contains load testing scripts for the NotesHub API using Locust.

## Prerequisites

```bash
pip install locust
```

## Running Load Tests

### Basic Usage

Start the backend server first:
```bash
cd /app/backend
python -m uvicorn server:app --host 0.0.0.0 --port 8001
```

Then run the load test:
```bash
cd /app/load_tests
locust -f locustfile.py --host=http://localhost:8001
```

Open http://localhost:8089 in your browser to access the Locust web UI.

### Command Line Mode (Headless)

Run without the web UI:
```bash
locust -f locustfile.py \
  --host=http://localhost:8001 \
  --users 100 \
  --spawn-rate 10 \
  --run-time 5m \
  --headless
```

Parameters:
- `--users`: Total number of concurrent users to simulate
- `--spawn-rate`: How many users to spawn per second
- `--run-time`: Test duration (e.g., 5m, 1h)
- `--headless`: Run without web UI

### Distributed Load Testing

For high load testing, run Locust in distributed mode:

**Master node:**
```bash
locust -f locustfile.py --master --host=http://localhost:8001
```

**Worker nodes:**
```bash
locust -f locustfile.py --worker --master-host=<master-ip>
```

## Test Scenarios

### 1. AuthenticatedUser
Simulates logged-in users performing:
- Browsing notes (30% of requests)
- Searching notes (20% of requests)
- Viewing profile (10% of requests)
- Viewing stats (10% of requests)

### 2. UnauthenticatedUser
Simulates anonymous users:
- Viewing homepage/health check (50% of requests)
- Browsing public notes (20% of requests)

## Interpreting Results

### Key Metrics

1. **Response Time**
   - Median: 50% of requests complete within this time
   - 95th percentile: 95% of requests complete within this time
   - 99th percentile: 99% of requests complete within this time

2. **Requests per Second (RPS)**
   - Total throughput of the system
   - Higher is better

3. **Failure Rate**
   - Percentage of failed requests
   - Should be < 1% for production systems

### Performance Benchmarks

**Acceptable Performance:**
- Median response time: < 200ms
- 95th percentile: < 1000ms
- 99th percentile: < 2000ms
- Failure rate: < 1%
- RPS: > 100 (for small deployments)

**Good Performance:**
- Median response time: < 100ms
- 95th percentile: < 500ms
- 99th percentile: < 1000ms
- Failure rate: < 0.1%
- RPS: > 500

## Exporting Results

### HTML Report
```bash
locust -f locustfile.py \
  --host=http://localhost:8001 \
  --users 100 \
  --spawn-rate 10 \
  --run-time 5m \
  --headless \
  --html=report.html
```

### CSV Report
```bash
locust -f locustfile.py \
  --host=http://localhost:8001 \
  --users 100 \
  --spawn-rate 10 \
  --run-time 5m \
  --headless \
  --csv=results
```

This creates:
- `results_stats.csv`: Request statistics
- `results_stats_history.csv`: Time-series data
- `results_failures.csv`: Failed requests

## CI/CD Integration

Add to your CI/CD pipeline:

```yaml
# .github/workflows/load-test.yml
name: Load Test

on:
  schedule:
    - cron: '0 2 * * *'  # Run daily at 2 AM

jobs:
  load-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Start backend
        run: |
          cd backend
          pip install -r requirements.txt
          uvicorn server:app --host 0.0.0.0 --port 8001 &
          sleep 10
      
      - name: Install Locust
        run: pip install locust
      
      - name: Run load test
        run: |
          cd load_tests
          locust -f locustfile.py \
            --host=http://localhost:8001 \
            --users 50 \
            --spawn-rate 5 \
            --run-time 2m \
            --headless \
            --html=report.html
      
      - name: Upload results
        uses: actions/upload-artifact@v2
        with:
          name: load-test-results
          path: load_tests/report.html
```

## Customization

Edit `locustfile.py` to:
- Add new user behaviors
- Adjust task weights
- Add custom test data
- Implement more complex scenarios

## Troubleshooting

### Connection Refused
- Ensure backend is running
- Check host URL is correct
- Verify firewall settings

### High Failure Rate
- Check backend logs for errors
- Reduce spawn rate
- Check database connection
- Monitor server resources

### Slow Response Times
- Enable database indexes
- Check for N+1 queries
- Monitor server CPU/memory
- Consider caching strategies
