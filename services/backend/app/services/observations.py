from typing import List
from fastapi import HTTPException, Depends, Response
from pydantic import UUID4
from starlette import status
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
    return observation_db

@log_calls
async def get_all() -> List[Observations]:
    all_observations = await Observations.all()
    return all_observations

@log_calls
async def get_by_uuid(observation_uuid: UUID4) -> Observations:
    observation_db = await Observations.get_or_none(uuid=observation_uuid)
    if not observation_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Наблюдение с UUID '{observation_uuid}' не найдено."
        )

    return observation_db

@log_calls
async def delete_by_uuid(observation_uuid: UUID4):
    delete_count = await Observations.delete_by_uuid(observation_uuid=observation_uuid)
    if not delete_count:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Наблюдение с UUID '{observation_uuid}' не найдено."
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)

