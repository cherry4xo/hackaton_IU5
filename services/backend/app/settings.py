import os
import random
import string
from dotenv import load_dotenv
load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

DB_URL = f"postgres://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

DB_CONNECTIONS = {
        "default": DB_URL,
    }

SECRET_KEY = os.getenv("SECRET_KEY", default="".join([random.choice(string.ascii_letters) for _ in range(32)]))
CLIENT_ID = os.getenv("CLIENT_ID", default="".join([random.choice(string.ascii_letters) for _ in range(32)]))

CORS_ORIGINS = ["*"]
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = ["*"]
CORS_ALLOW_HEADERS = ["*"]

DEFAULT_MODERATOR_USERNAME = os.getenv("DEFAULT_MODERATOR_USERNAME", default="moderator")
DEFAULT_MODERATOR_EMAIL = os.getenv("DEFAULT_MODERATOR_EMAIL", default="moderator@example.com")
DEFAULT_MODERATOR_PASSWORD = os.getenv("DEFAULT_MODERATOR_PASSWORD", default="password")

LOGIN_URL = f"http://0.0.0.0:8080/backend/users/access-token"

MODE = os.getenv("MODE", default="DEBUG")

ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 14 # change in release to 15 minutes
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 14 # 2 weeks

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")

# MinIO Configuration
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
MINIO_BUCKET_NAME = os.getenv("MINIO_BUCKET_NAME", "orbit-images")
MINIO_SECURE = os.getenv("MINIO_SECURE", "False").lower() == "true"
