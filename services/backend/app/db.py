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
from app.schemas import UserCreate

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

async def upgrade_db(app: FastAPI, db_url: str = None):
    """
    Initializes Aerich and applies any pending migrations.
    Should be run during application startup.
    """
    global AERICH_COMMAND
    logger.info("Initializing database and applying migrations...")
    logger.debug("Using Aerich config: %s", TORTOISE_ORM)
    logger.debug("Migrations base location: %s", AERICH_COMMAND.location)
    logger.debug("App-specific migration path: %s", MODELS_MIGRATION_PATH)
    logger.debug("Current working directory: %s", os.getcwd())

    try:
        try:
            os.makedirs(AERICH_COMMAND.location, exist_ok=True)
            logger.info(f"Ensured base migration directory exists: {AERICH_COMMAND.location}")
        except OSError as e:
            logger.error(f"Could not create base migration directory {AERICH_COMMAND.location}: {e}", exc_info=True)
            raise

        # Try to initialize the Aerich schema tracking table
        # This should only be needed once, but we handle the case where it already exists
        logger.info("Attempting to initialize Aerich schema tracking table...")
        try:
            await AERICH_COMMAND.init_db(safe=True)
            logger.info("Aerich schema tracking table initialized.")
        except FileExistsError as e:
            logger.info("Aerich schema tracking table already exists, continuing...")
        except Exception as init_db_exc:
            logger.warning(f"Non-critical error during 'aerich init-db': {init_db_exc}", exc_info=True)
            # Continue anyway as the table might already exist

        # Ensure migration directory exists
        if not os.path.exists(MODELS_MIGRATION_PATH):
            logger.info("Creating migration directory...")
            try:
                await AERICH_COMMAND.init()
                logger.info("Migration directory created.")
            except Exception as init_exc:
                logger.warning(f"Error during 'aerich init': {init_exc}", exc_info=True)
        else:
            logger.info(f"Migration directory already exists: {MODELS_MIGRATION_PATH}")

        # Check if there are any migration files before attempting upgrade
        migration_files = []
        if os.path.exists(MODELS_MIGRATION_PATH):
            migration_files = [f for f in os.listdir(MODELS_MIGRATION_PATH) if f.endswith('.py') and f != '__init__.py']
        
        if migration_files:
            logger.info(f"Found {len(migration_files)} migration files, applying...")
            # Apply any pending migrations
            logger.info("Running 'aerich upgrade' to apply pending migrations...")
            try:
                await AERICH_COMMAND.upgrade(run_in_transaction=True)
                logger.info("'aerich upgrade' finished successfully.")
                logger.info("Database migrations applied successfully.")
            except aerich_exceptions.DowngradeError as e:
                logger.error(f"Downgrade error during migration: {e}", exc_info=True)
                raise
            except AttributeError as attr_err:
                if "'Migrate' object has no attribute 'migrate_location'" in str(attr_err):
                    logger.error("Aerich migration error: migrate_location attribute missing. This may indicate a version incompatibility.", exc_info=True)
                    # Try to recreate the migration setup
                    logger.info("Attempting to reset Aerich migration state...")
                    try:
                        # Recreate the command instance
                        AERICH_COMMAND = Command(tortoise_config=TORTOISE_ORM, app="models", location=MIGRATION_LOCATION)
                        await AERICH_COMMAND.upgrade(run_in_transaction=True)
                        logger.info("Retry of 'aerich upgrade' finished successfully.")
                        logger.info("Database migrations applied successfully.")
                    except Exception as retry_err:
                        logger.error(f"Retry of 'aerich upgrade' also failed: {retry_err}", exc_info=True)
                        raise
                else:
                    logger.error(f"Attribute error during 'aerich upgrade': {attr_err}", exc_info=True)
                    raise
            except Exception as upgrade_exc:
                logger.error(f"Error during 'aerich upgrade': {upgrade_exc}", exc_info=True)
                raise
        else:
            logger.info("No migration files found, skipping upgrade step.")

    except Exception as e:
        logger.critical("Failed to apply database migrations due to an unexpected error.", exc_info=True)
        print(f"FATAL: Failed to apply migrations: {e}")
        raise

async def create_default_moderator_user() -> None:
    if not settings.DEFAULT_MODERATOR_PASSWORD:
        logger.warning("DEFAULT_MODERATOR_PASSWORD environment variable not set. Cannot create default moderator.")
        return None

    logger.info(f"Checking for default moderator user: {settings.DEFAULT_MODERATOR_USERNAME}")

    try:
        existing_user = await User.get_by_username(settings.DEFAULT_MODERATOR_USERNAME)
        if existing_user:
            logger.info(f"Default moderator '{settings.DEFAULT_MODERATOR_USERNAME}' already exists.")
            if existing_user.role != UserRole.MODERATOR:
                logger.warning(f"User '{settings.DEFAULT_MODERATOR_USERNAME}' exists but is not a MODERATOR. Updating role.")
                existing_user.role = UserRole.MODERATOR
                await existing_user.save(update_fields=['role', 'updated_at']) # Explicitly save role change
            return existing_user
        else:
            logger.info(f"Default moderator '{settings.DEFAULT_MODERATOR_USERNAME}' not found. Creating...")
            user_model = UserCreate(username=settings.DEFAULT_MODERATOR_USERNAME, 
                                    password=settings.DEFAULT_MODERATOR_PASSWORD, 
                                    email=settings.DEFAULT_MODERATOR_EMAIL)
            new_user = await User.create(user_model)
            new_user.role = UserRole.MODERATOR
            await new_user.save()
    except Exception as e:
        logger.error(f"Failed to create default moderator user: {e}", exc_info=True)
        raise


async def init(app: FastAPI):
    # await upgrade_db(app)
    register_db(app)
    logger.debug("Connected to db")
    # await create_default_moderator_user()
