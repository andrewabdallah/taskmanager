from .base import *

DEBUG = False
ALLOWED_HOSTS = ["*"]

# Faster password hashing for test speed
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]


# Disable migrations for test performance (optional)
class DisableMigrations:
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return None


MIGRATION_MODULES = DisableMigrations()

# Optional: Configure pytest-factoryboy and faker
INSTALLED_APPS += [
    "pytest_django",
    "factory",
]
