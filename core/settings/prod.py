from .base import *

# TODO: Update domain names before deploying
DEBUG = False
ALLOWED_HOSTS = ["dummydomain.com"]

CSRF_TRUSTED_ORIGINS = ["https://dummydomain.com"]
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
