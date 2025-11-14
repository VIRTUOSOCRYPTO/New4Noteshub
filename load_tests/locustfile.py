"""
Load Testing with Locust
API load testing scenarios for NotesHub
"""
import os
import random
from locust import HttpUser, task, between, events
import json

# Test data
TEST_DEPARTMENTS = ["Computer Science", "Electronics", "Mechanical", "Civil"]
TEST_SUBJECTS = ["Mathematics", "Physics", "Programming", "Data Structures"]
TEST_YEARS = [1, 2, 3, 4]


class AuthenticatedUser(HttpUser):
    """
    Simulates an authenticated user performing various actions
    """
    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks
    
    def on_start(self):
        """Called when a user starts - performs login"""
        # Register a test user
        usn = f"TEST{random.randint(10000, 99999)}"
        department = random.choice(TEST_DEPARTMENTS)
        year = random.choice(TEST_YEARS)
        
        self.user_data = {
            "usn": usn,
            "email": f"{usn.lower()}@test.com",
            "password": "TestPass123!",
            "confirmPassword": "TestPass123!",
            "department": department,
            "college": "Test College",
            "year": year
        }
        
        # Register
        response = self.client.post("/api/register", json=self.user_data)
        
        if response.status_code == 200 or response.status_code == 409:
            # Login
            login_response = self.client.post("/api/login", json={
                "usn": usn,
                "password": "TestPass123!"
            })
            
            if login_response.status_code == 200:
                data = login_response.json()
                self.access_token = data.get("accessToken")
                self.headers = {"Authorization": f"Bearer {self.access_token}"}
            else:
                self.access_token = None
                self.headers = {}
        else:
            self.access_token = None
            self.headers = {}
    
    @task(3)
    def view_notes(self):
        """View notes list - most common action"""
        params = {
            "department": random.choice(TEST_DEPARTMENTS),
            "year": random.choice(TEST_YEARS)
        }
        
        with self.client.get(
            "/api/notes",
            params=params,
            name="/api/notes [browse]",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Got status code {response.status_code}")
    
    @task(2)
    def search_notes(self):
        """Search for notes"""
        query = random.choice(["algorithm", "data", "structure", "mathematics"])
        
        with self.client.get(
            "/api/search",
            params={"q": query},
            headers=self.headers,
            name="/api/search",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Search failed: {response.status_code}")
    
    @task(1)
    def view_profile(self):
        """View user profile"""
        if not self.access_token:
            return
        
        with self.client.get(
            "/api/user",
            headers=self.headers,
            name="/api/user [profile]",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Profile fetch failed: {response.status_code}")
    
    @task(1)
    def view_stats(self):
        """View user statistics"""
        if not self.access_token:
            return
        
        with self.client.get(
            "/api/user/stats",
            headers=self.headers,
            name="/api/user/stats",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Stats fetch failed: {response.status_code}")


class UnauthenticatedUser(HttpUser):
    """
    Simulates an unauthenticated user browsing the site
    """
    wait_time = between(2, 5)
    
    @task(5)
    def view_homepage(self):
        """View homepage/health check"""
        with self.client.get("/api/health", name="/api/health", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Health check failed: {response.status_code}")
    
    @task(2)
    def view_public_notes(self):
        """Browse public notes without authentication"""
        with self.client.get("/api/notes", name="/api/notes [public]", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Public notes fetch failed: {response.status_code}")


# Event handlers for custom reporting
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    print("\n" + "="*80)
    print("Starting NotesHub Load Test")
    print("="*80)
    print(f"Target URL: {environment.host}")
    print(f"Number of users: {environment.runner.target_user_count if hasattr(environment.runner, 'target_user_count') else 'N/A'}")
    print("="*80 + "\n")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    print("\n" + "="*80)
    print("Load Test Completed")
    print("="*80)
    
    # Get statistics
    stats = environment.stats
    
    print(f"\nTotal requests: {stats.total.num_requests}")
    print(f"Total failures: {stats.total.num_failures}")
    print(f"Average response time: {stats.total.avg_response_time:.2f}ms")
    print(f"Median response time: {stats.total.median_response_time:.2f}ms")
    print(f"95th percentile: {stats.total.get_response_time_percentile(0.95):.2f}ms")
    print(f"99th percentile: {stats.total.get_response_time_percentile(0.99):.2f}ms")
    print(f"Requests per second: {stats.total.total_rps:.2f}")
    print(f"Failure rate: {(stats.total.num_failures / stats.total.num_requests * 100):.2f}%" if stats.total.num_requests > 0 else "0.00%")
    print("="*80 + "\n")
