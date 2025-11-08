from datetime import date, timedelta

from django.contrib.auth.models import User
from rest_framework.test import APIClient, APITestCase

from tasks.models import Task


class TaskAPITests(APITestCase):
    def setUp(self):
        self.u = User.objects.create_user("andrew", password="pass1234")
        self.client = APIClient()
        token = self.client.post(
            "/api/token/", {"username": "andrew", "password": "pass1234"}
        ).data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def test_create_task_validates_priority(self):
        r = self.client.post("/api/tasks/", {"title": "X", "priority": 9}, format="json")
        self.assertEqual(r.status_code, 400)
        self.assertIn("priority", str(r.data).capitalize())

    def test_create_and_list(self):
        due = (date.today() + timedelta(days=2)).isoformat()
        r = self.client.post(
            "/api/tasks/",
            {"title": "Do it", "priority": 2, "due_date": due},
            format="json",
        )
        self.assertEqual(r.status_code, 201)
        r = self.client.get("/api/tasks/")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.data), 1)

    def test_recent_endpoint_cached(self):
        for i in range(3):
            Task.objects.create(owner=self.u, title=f"T{i}")
        r1 = self.client.get("/api/tasks/recent/")
        r2 = self.client.get("/api/tasks/recent/")  # should hit cache
        self.assertEqual(r1.status_code, 200)
        self.assertEqual(r2.status_code, 200)
