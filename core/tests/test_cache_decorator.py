from unittest.mock import Mock

from django.core.cache import cache
from django.test import TestCase

from core.decorators.cache_decorator import cache_api_call


class TestCacheApiCallDecorator(TestCase):
    def setUp(self):
        # Clear the cache before each test to avoid interference
        cache.clear()

    def test_cache_api_call_caching_behavior(self):
        # Mock function that would be decorated
        mock_function = Mock(return_value="expected result")
        mock_function.__name__ = "mock_function_name"

        decorated_function = cache_api_call("id")(mock_function)

        # First call with a unique identifier, should result in cache miss and function execution
        result1 = decorated_function(id="user_1")
        self.assertEqual(result1, "expected result")
        self.assertEqual(
            mock_function.call_count, 1, "Function should be called once on cache miss"
        )

        # Second call with the same identifier, should result in cache hit and no function execution
        result2 = decorated_function(id="user_1")
        self.assertEqual(result2, "expected result")
        self.assertEqual(
            mock_function.call_count,
            1,
            "Function should not be called again due to cache hit",
        )

        # Call with a different identifier, should result in cache miss and function execution
        result3 = decorated_function(id="user_2")
        self.assertEqual(result3, "expected result")
        self.assertEqual(
            mock_function.call_count,
            2,
            "Function should be called again with a different identifier",
        )

    def test_multiple_keys(self):
        """
        Should accept multiple keys on the decorator
        """
        # Mock function that would be decorated
        mock_function = Mock(return_value="expected result")
        mock_function.__name__ = "mock_function_name"

        decorated_function = cache_api_call("id", "extra_id")(mock_function)

        # first call
        decorated_function(id="user_1", extra_id="task_1")
        # call a second time with the same arguments
        decorated_function(id="user_1", extra_id="task_1")

        self.assertEqual(mock_function.call_count, 1, "Function should be called once")
