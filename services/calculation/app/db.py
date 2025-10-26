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
    # Update the DB connection URL dynamically if needed
    TORTOISE_ORM["connections"]["default"] = db_url  # ← Important: ensure connection is set

    register_tortoise(
        app,
        config=TORTOISE_ORM,
        generate_schemas=False,  # ← Disable auto schema creation! Let Aerich handle it
        add_exception_handlers=True,
    )

async def upgrade_db(app: FastAPI, db_url: str = None):
    """
    Initializes Aerich and applies pending migrations.
    Must be called AFTER Tortoise is registered.
    """
    db_url = db_url or settings.DB_URL

    # 🔧 Rebuild config dynamically
    config = {
        "connections": {"default": db_url},
        "apps": {
            "models": {
                "models": ["app.models", "aerich.models"],
                "default_connection": "default"
            }
        }
    }

    location = "./migrations"
    os.makedirs(location, exist_ok=True)

    # 🆕 Create a FRESH Command instance (never reuse globally!)
    command = Command(tortoise_config=config, app="models", location=location)

    try:
        # Step 1: Initialize Aerich metadata (creates aerich table)
        logger.info("Initializing Aerich metadata (aerich table)...")
        try:
            await command.init_db(safe=True)
            logger.info("Aerich metadata initialized.")
        except FileExistsError:
            logger.info("Aerich metadata already initialized.")

        # Step 2: Ensure migration folder exists
        models_migrations_dir = os.path.join(location, "models")
        if not os.path.exists(models_migrations_dir):
            logger.info("Creating migration directory for models...")
            await command.init()
            logger.info(f"Migration directory created at {models_migrations_dir}")
        else:
            logger.info(f"Migration directory already exists: {models_migrations_dir}")

        # Step 3: Run pending migrations
        migration_files = [
            f for f in os.listdir(models_migrations_dir)
            if f.endswith(".py") and f != "__init__.py"
        ]
        if not migration_files:
            logger.info("No migration files found. Skipping upgrade.")
            return

        logger.info(f"Applying {len(migration_files)} migration(s)...")
        await command.upgrade(run_in_transaction=True)
        logger.info("✅ All migrations applied successfully.")

    except AttributeError as e:
        if "migrate_location" in str(e):
            logger.critical(
                "Aerich error: 'Migrate.migrate_location' is missing. "
                "This usually happens if Command() is created too early or reused. "
                "Ensure you're creating a fresh Command() after DB config is ready."
            )
        raise
    except Exception as e:
        logger.critical(f"Migration failed: {e}", exc_info=True)
        raise
