import os
import uuid
import logging
import errno

from tortoise.contrib.fastapi import register_tortoise
from aerich import Command, exceptions as aerich_exceptions
from fastapi import FastAPI

from app import settings
from app.enums import UserRole
from app.models import User

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.DEBUG,  # set to DEBUG to capture all logs
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

def get_tortoise_config() -> dict:
    app_list = ["app.models", "aerich.models"]
    config = {
        "connections": settings.DB_CONNECTIONS,
        "apps": {
            "models": {
                "models": app_list,
                "default_connection": "default"
            }
        }
    }   
    return config

TORTOISE_ORM = get_tortoise_config()
MIGRATION_LOCATION = "./migrations"
AERICH_COMMAND = Command(tortoise_config=TORTOISE_ORM, app="models", location=MIGRATION_LOCATION)
MODELS_MIGRATION_PATH = os.path.join(AERICH_COMMAND.location, AERICH_COMMAND.app)

def register_db(app: FastAPI, db_url: str = None) -> None:
    db_url = db_url or settings.DB_URL
    app_list = ["app.models", "aerich.models"]
    register_tortoise(
        app,
        config=TORTOISE_ORM,
        generate_schemas=True,
        add_exception_handlers=True
    )

async def init(app: FastAPI):
    register_db(app)