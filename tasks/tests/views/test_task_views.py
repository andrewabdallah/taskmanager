from datetime import date, timedelta

from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from core.factories import UserFactory
from tasks.factories import TaskFactory
from tasks.models import Task
from tasks.views import TaskViewSet


class TestTaskViewSet(TestCase):
    # ---------------- LIST ----------------
    def test_tasks_list(self):
        user = UserFactory()
        TaskFactory(owner=user)
        TaskFactory(owner=user)

        request = APIRequestFactory().get("/tasks/")
        force_authenticate(request, user=user)

        response = TaskViewSet.as_view({"get": "list"})(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

    # ---------------- RETRIEVE ----------------
    def test_task_retrieve(self):
        user = UserFactory()
        task = TaskFactory(owner=user)

        request = APIRequestFactory().get(f"/tasks/{task.id}/")
        force_authenticate(request, user=user)

        response = TaskViewSet.as_view({"get": "retrieve"})(request, pk=task.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], str(task.id))

    # ---------------- CREATE ----------------
    def test_task_create(self):
        user = UserFactory()

        payload = {
            "title": "New Task",
            "description": "",
            "priority": 3,
            "status": "pending",
            "due_date": str(date.today() + timedelta(days=1)),
        }

        request = APIRequestFactory().post("/tasks/", payload, format="json")
        force_authenticate(request, user=user)

        response = TaskViewSet.as_view({"post": "create"})(request)
        self.assertEqual(response.status_code, 201)

        task = Task.objects.first()
        self.assertEqual(task.owner, user)
        self.assertEqual(task.title, "New Task")

    # ---------------- UPDATE ----------------
    def test_task_update(self):
        user = UserFactory()
        task = TaskFactory(owner=user, title="Old")

        payload = {"title": "Updated"}

        request = APIRequestFactory().patch(f"/tasks/{task.id}/", payload, format="json")
        force_authenticate(request, user=user)

        response = TaskViewSet.as_view({"patch": "partial_update"})(request, pk=task.id)
        self.assertEqual(response.status_code, 200)

        task.refresh_from_db()
        self.assertEqual(task.title, "Updated")

    # ---------------- DELETE ----------------
    def test_task_delete(self):
        """
        Delete a task and ensure it is soft deleted.
        Verify that the task is no longer in the active queryset.
        """
        user = UserFactory()
        task = TaskFactory(owner=user)

        request = APIRequestFactory().delete(f"/tasks/{task.id}/")
        force_authenticate(request, user=user)

        response = TaskViewSet.as_view({"delete": "destroy"})(request, pk=task.id)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Task.objects.active().count(), 0)
        self.assertEqual(Task.objects.count(), 1)  # still exists in DB

    def test_tasks_list_filter_priority(self):
        user = UserFactory()
        TaskFactory(owner=user, priority=1)
        TaskFactory(owner=user, priority=5)

        request = APIRequestFactory().get("/tasks/?min_priority=3")
        force_authenticate(request, user=user)

        response = TaskViewSet.as_view({"get": "list"})(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["items"]), 1)
        self.assertEqual(response.data["items"][0]["priority"], 5)

    def test_tasks_list_csv_renderer(self):
        user = UserFactory()
        TaskFactory(owner=user)

        request = APIRequestFactory().get("/tasks/?format=csv", HTTP_ACCEPT="text/csv")
        force_authenticate(request, user=user)

        response = TaskViewSet.as_view({"get": "list"})(request)
        self.assertEqual(response.status_code, 200)
        self.assertIn("attachment; filename=", response["Content-Disposition"])
