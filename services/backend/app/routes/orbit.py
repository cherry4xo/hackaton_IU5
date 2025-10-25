from datetime import datetime
from typing import Optional
import uuid
from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from app.utils.queue.schemas import OrbitCalculationRequest, TaskResponse
from app.models import CalculationTask, CalculationTaskStatus, Comets, User
from app.utils.contrib import get_current_user
from app.utils.queue.queue import send_calculation_task

router = APIRouter(prefix="/orbit")


@router.post("/calculate", response_model=TaskResponse)
async def calculate_orbit(
    request: OrbitCalculationRequest,
    comet_uuid: Optional[str] = None,
    user: User = Depends(get_current_user),
):
    if len(request.observations) < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least 3 observations are required for orbit calculation"
        )
    
    task_id = str(uuid.uuid4())
    submitted_at = datetime.now()

    comet = None
    if comet_uuid:
        comet = Comets.get_or_none(uuid=comet_uuid)
        if not comet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comet not found"
            )
        
    task = await CalculationTask.create(
        uuid=task_id,
        user=user,
        comet=comet,
        status=CalculationTaskStatus.PROCESSING,
        raw_observations=[obs.model_dump() for obs in request.observations],
        location_code=request.options.get('location_code', '500'),
    )

    success = await send_calculation_task(
        task_id,
        str(user.uuid),
        request
    )

    if not success:
        task.status = CalculationTaskStatus.FAILED
        task.error_message = "Failed to send to queue"
        await task.save()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Failed to send task to queue'
        )
    
    return TaskResponse(
        task_id=task.uuid,
        status=task.status,
        submitted_at=task.created_at
    )
