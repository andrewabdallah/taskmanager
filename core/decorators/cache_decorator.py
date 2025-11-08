import logging
from functools import wraps

from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)


def cache_api_call(*keys, timeout=None):
    """
    A decorator that caches a function's result based on keyword arguments.

    Args:
        *keys: Names of kwargs used to build the cache key.
        timeout: Optional cache timeout (in seconds).
                 If not provided, uses settings.CACHE_TIMEOUT or defaults to 300.

    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            use_cache = kwargs.pop("cache", True)
            if not use_cache:
                return func(*args, **kwargs)

            # Make sure all cache key parameters exist in kwargs
            if not all(key in kwargs for key in keys):
                logger.warning(f"Missing cache keys {keys} in kwargs for {func.__name__}")
                return func(*args, **kwargs)

            # Build cache key from function name + keys
            cache_key = f"{func.__name__}:" + "-".join(str(kwargs[key]) for key in keys)

            # Determine timeout priority
            effective_timeout = timeout or settings.CACHE_TIMEOUT or 300

            # Check cache
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                logger.debug(f"Cache hit for {cache_key}")
                return cached_value

            # Cache miss → compute and store result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, timeout=effective_timeout)
            logger.debug(f"Cache set for {cache_key} with timeout={effective_timeout}s")
            return result

        return wrapper

    return decorator
