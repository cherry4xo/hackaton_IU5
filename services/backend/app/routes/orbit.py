from datetime import datetime
import uuid
from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from app.utils.queue.schemas import OrbitCalculationRequest, TaskResponse
from app.models import User
from app.utils.contrib import get_current_user
from app.utils.queue.queue import send_calculation_task

router = APIRouter()


@router.post("/calculate", response_model=TaskResponse)
async def calculate_orbit(
    request: OrbitCalculationRequest,
    user: User = Depends(get_current_user)
):
    if len(request.observations) < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least 3 observations are required for orbit calculation"
        )
    
    task_id = str(uuid.uuid4())
    submitted_at = datetime.now()

    success = await send_calculation_task(
        task_id,
        str(user.uuid),
        request
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Failed to send task to queue'
        )
    
    return TaskResponse(
        task_id=task_id,
        status="processing",
        submitted_at=submitted_at
    )
