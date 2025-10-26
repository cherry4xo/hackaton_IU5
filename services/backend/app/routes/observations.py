from datetime import datetime
from typing import List, Optional
import uuid
from fastapi import APIRouter, Depends, HTTPException
from pydantic import UUID4
from starlette import status
from app.schemas import GetObservations, CreateObservations
from app.models import CalculationTask, CalculationTaskStatus, Comets, User, Observatories
from app.utils.contrib import get_current_user
from app.utils.queue.queue import send_calculation_task
from app.services.observations import get_all, create_observation, get_by_uuid, delete_by_uuid

router = APIRouter(prefix="/observations")

@router.post("/", response_model=CreateObservations, status_code=status.HTTP_201_CREATED)
async def create_new_observation(
    request: CreateObservations,
    user: User = Depends(get_current_user),
):
    observation = await create_observation(observation=CreateObservations)
    new_observation = await observation.to_dict()
    return new_observation

@router.get("/", response_model=List[GetObservations])
async def get_all_positional_observations():
    all_observations = await get_all()
    return all_observations


@router.get("/{observations_id}", response_model=GetObservations)
async def get_positional_observations_by_id(observations_id: UUID4):
    observation = await get_by_uuid(observation_uuid=observations_id)
    return observation