import os
from dotenv import load_dotenv
load_dotenv()

MODE = os.getenv("MODE", default="DEBUG")

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")

SECRET_KEY = os.getenv("SECRET_KEY", "")