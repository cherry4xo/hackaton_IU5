from datetime import datetime
from typing import Optional
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from starlette import status
from app.utils.queue.schemas import OrbitCalculationRequest, TaskResponse
from app.models import CalculationTask, CalculationTaskStatus, Comets, User, Observations
from app.utils.contrib import get_current_user
from app.utils.queue.queue import send_calculation_task
from app.utils.minio_client import get_minio_client
from PIL import Image
import io
import uuid
from typing import Dict, Any

router = APIRouter(prefix="/orbit")


@router.post("/upload-image")
async def upload_observation_image(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
):
    # Validate file type
    if file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only JPEG and PNG images are supported"
        )
    
    # Read image data
    image_data = await file.read()
    
    # Validate image with PIL
    try:
        image = Image.open(io.BytesIO(image_data))
        width, height = image.size
        format = image.format
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid image file: {str(e)}"
        )
    
    # Generate unique filename
    file_extension = file.filename.split('.')[-1] if '.' in file.filename else 'jpg'
    object_name = f"observation_images/{uuid.uuid4()}.{file_extension}"
    
    # Upload to MinIO
    minio_client = get_minio_client()
    try:
        url = minio_client.upload_image(image_data, object_name, file.content_type)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload image to storage: {str(e)}"
        )
    
    return {
        "image_reference": object_name,
        "url": url,
        "width": width,
        "height": height,
        "format": format,
        "size": len(image_data)
    }


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
