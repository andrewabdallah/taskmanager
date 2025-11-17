from datetime import date, timedelta

from django.test import TestCase

from tasks.factories import TaskFactory
from tasks.serializers.task_serializer import TaskCSVSerializer, TaskSerializer


class TestTaskSerializer(TestCase):
    def test_task_serializer_valid(self):
        task = TaskFactory()
        serializer = TaskSerializer(task)

        self.assertIsNotNone(serializer.data["id"])
        self.assertEqual(serializer.data["owner"], task.owner.username)

    def test_task_serializer_invalid_priority(self):
        payload = {
            "title": "Test",
            "description": "",
            "priority": 8,  # invalid
            "due_date": str(date.today() + timedelta(days=1)),
            "status": "pending",
        }

        serializer = TaskSerializer(data=payload, context={"request": None})
        self.assertFalse(serializer.is_valid())
        self.assertIn("priority", serializer.errors)

    def test_task_serializer_invalid_due_date(self):
        payload = {
            "title": "Test",
            "priority": 3,
            "due_date": str(date.today() - timedelta(days=1)),  # invalid past date
            "status": "pending",
        }

        serializer = TaskSerializer(data=payload)
        self.assertFalse(serializer.is_valid())
        self.assertIn("due_date", serializer.errors)

    def test_task_serializer_valid_data(self):
        payload = {
            "title": "Test Task",
            "description": "This is a test task.",
            "priority": 2,
            "due_date": str(date.today() + timedelta(days=5)),
            "status": "in_progress",
        }

        serializer = TaskSerializer(data=payload)
        self.assertTrue(serializer.is_valid())

    def test_task_serializer_edge_case_due_date_today(self):
        payload = {
            "title": "Today Due Task",
            "priority": 3,
            "due_date": str(date.today()),
            "status": "pending",
        }
        serializer = TaskSerializer(data=payload)
        self.assertTrue(serializer.is_valid())

    def test_task_serializer_boundary_due_date(self):
        payload = {
            "title": "Boundary Due Date Task",
            "priority": 3,
            "due_date": str(date.today() + timedelta(days=0)),  # today
            "status": "pending",
        }
        serializer = TaskSerializer(data=payload)
        self.assertTrue(serializer.is_valid())

    def test_task_serializer_maximum_fields(self):
        payload = {
            "title": "Max Fields Task",
            "description": "D" * 1000,  # long description
            "priority": 1,
            "due_date": str(date.today() + timedelta(days=30)),
            "status": "completed",
        }
        serializer = TaskSerializer(data=payload)
        self.assertTrue(serializer.is_valid())

    def test_task_serializer_minimum_fields(self):
        payload = {
            "title": "Min Fields Task",
            "priority": 5,
            "status": "pending",
            "due_date": str(date.today() + timedelta(days=1)),
        }
        serializer = TaskSerializer(data=payload)
        self.assertTrue(serializer.is_valid())

    def test_task_serializer_invalid_status(self):
        payload = {
            "title": "Invalid Status Task",
            "priority": 3,
            "due_date": str(date.today() + timedelta(days=5)),
            "status": "unknown_status",  # invalid status
        }
        serializer = TaskSerializer(data=payload)
        self.assertFalse(serializer.is_valid())
        self.assertIn("status", serializer.errors)

    def test_task_serializer_null_due_date(self):
        payload = {
            "title": "Null Due Date Task",
            "priority": 3,
            "due_date": None,  # null due date
            "status": "pending",
        }
        serializer = TaskSerializer(data=payload)
        self.assertFalse(serializer.is_valid())

    def test_task_serializer_zero_priority(self):
        payload = {
            "title": "Zero Priority Task",
            "priority": 0,  # invalid priority
            "due_date": str(date.today() + timedelta(days=5)),
            "status": "pending",
        }
        serializer = TaskSerializer(data=payload)
        self.assertFalse(serializer.is_valid())
        self.assertIn("priority", serializer.errors)

    def test_task_serializer_negative_priority(self):
        payload = {
            "title": "Negative Priority Task",
            "priority": -1,  # invalid priority
            "due_date": str(date.today() + timedelta(days=5)),
            "status": "pending",
        }
        serializer = TaskSerializer(data=payload)
        self.assertFalse(serializer.is_valid())
        self.assertIn("priority", serializer.errors)

    def test_task_serializer_large_priority(self):
        payload = {
            "title": "Large Priority Task",
            "priority": 100,  # invalid priority
            "due_date": str(date.today() + timedelta(days=5)),
            "status": "pending",
        }
        serializer = TaskSerializer(data=payload)
        self.assertFalse(serializer.is_valid())
        self.assertIn("priority", serializer.errors)

    def test_task_csv_serializer_fields(self):
        task = TaskFactory()
        serializer = TaskCSVSerializer(task)
        data = serializer.data

        expected = {
            "id",
            "title",
            "description",
            "priority",
            "due_date",
            "status",
            "owner",
            "created_at",
            "updated_at",
        }

        self.assertEqual(set(data.keys()), expected)
