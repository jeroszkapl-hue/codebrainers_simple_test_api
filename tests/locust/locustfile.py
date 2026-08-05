"""Simple Locust load test for the Employee Manager API.

Not part of the pytest suite (no `test_*.py` naming, not collected by
`pytest`) — this is exercised with the `locust` CLI directly, against a
running instance of the app.

Run with the interactive web UI:

    python run.py                                    # in one terminal
    locust -f tests/locust/locustfile.py --host http://127.0.0.1:8000

Then open http://localhost:8089 to pick a user count / spawn rate and
watch live charts.

Or headless, e.g. for a quick 10-user/1-minute smoke run:

    locust -f tests/locust/locustfile.py --host http://127.0.0.1:8000 \
        --headless --users 10 --spawn-rate 2 --run-time 1m

Notes:
- `/api/login` issues a bearer token valid for 10 minutes (see
  `TOKEN_TTL_MINUTES` in main.py). Each simulated user re-logs in
  automatically on a 401 instead of assuming the token outlives the run,
  so --run-time can safely exceed 10 minutes.
- The app keeps employees in a single in-memory list shared by every
  simulated user (see main.py) — nothing here calls
  `POST /api/employees/reset`, so employee IDs keep climbing across a run.
  Reset manually between runs if you want a clean slate.
- Each user only updates/deletes employees it created itself, so there's
  no cross-user 404 noise from one user deleting another's employee.
"""

import random

from locust import HttpUser, between, task

POSITIONS = ["Junior QA", "Mid QA", "Senior QA", "QA Lead"]


class EmployeeManagerUser(HttpUser):
    """Simulates one logged-in user browsing and editing the employee list."""

    wait_time = between(1, 3)

    def on_start(self):
        self.created_ids: list[int] = []
        self.login()

    def login(self):
        response = self.client.post(
            "/api/login",
            json={"username": "admin", "password": "admin"},
            name="/api/login",
        )
        self.token = response.json()["access_token"]

    def auth_headers(self):
        return {"Authorization": f"Bearer {self.token}"}

    def api_request(self, method, url, **kwargs):
        """Send an authenticated request, re-logging in once on a 401.

        Covers the token expiring mid-run (10-minute TTL) without every
        task having to handle that itself.
        """
        response = self.client.request(
            method, url, headers=self.auth_headers(), **kwargs
        )

        if response.status_code == 401:
            self.login()
            response = self.client.request(
                method, url, headers=self.auth_headers(), **kwargs
            )

        return response

    def random_employee_payload(self):
        return {
            "name": f"Load Test {random.randint(1, 1_000_000)}",
            "salary": random.randint(1, 200_000),
            "age": random.randint(18, 65),
            "position": random.choice(POSITIONS),
            "on_leave": random.choice([True, False]),
        }

    @task(5)
    def list_employees(self):
        self.api_request("GET", "/api/employees", name="/api/employees [GET]")

    @task(3)
    def create_employee(self):
        response = self.api_request(
            "POST",
            "/api/employees",
            json=self.random_employee_payload(),
            name="/api/employees [POST]",
        )
        if response.status_code == 200:
            self.created_ids.append(response.json()["id"])

    @task(2)
    def update_employee(self):
        if not self.created_ids:
            return

        emp_id = random.choice(self.created_ids)
        self.api_request(
            "PUT",
            f"/api/employees/{emp_id}",
            json=self.random_employee_payload(),
            name="/api/employees/{id} [PUT]",
        )

    @task(1)
    def delete_employee(self):
        if not self.created_ids:
            return

        emp_id = self.created_ids.pop()
        self.api_request(
            "DELETE",
            f"/api/employees/{emp_id}",
            name="/api/employees/{id} [DELETE]",
        )

    @task(1)
    def health_check(self):
        # Unauthenticated baseline — useful to compare latency against the
        # authenticated CRUD endpoints above.
        self.client.get("/health", name="/health")
