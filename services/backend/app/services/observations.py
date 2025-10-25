from fastapi import HTTPException, Depends
from pydantic import UUID4
from tortoise.exceptions import IntegrityError

from app.schemas import CreateObservations
from app.models import User, Observations
from app.enums import UserRole
from app.utils import password
from app.utils.contrib import get_current_user
from app.logger import log_calls

@log_calls
async def create_observation(observation: Observations):
    observation_db = await Observations.create(Observations=observation_db)
    # metrics.backend_user_registrations_total.inc()
    return user_db
