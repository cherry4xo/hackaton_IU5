from datetime import datetime
import json
from typing import Optional, List
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from starlette import status
from app.utils.queue.schemas import (
    OrbitCalculationRequest, 
    TaskResponse, 
    ClosestApproachRequest,
    TaskListItem,
    TaskResultResponse,
    TaskType,
    OrbitResult,
    ClosestApproachResult
)
from app.models import CalculationTask, CalculationTaskStatus, Comets, User, Observations, Orbits, Close_approaches
from app.utils.contrib import get_current_user
from app.utils.queue.queue import send_orbit_calculation_task, send_closest_approach_task
from app.utils.minio_client import get_minio_client
from PIL import Image
import io
import uuid
from typing import Dict, Any
from uuid import UUID

router = APIRouter()


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
    comet_name: Optional[str] = None,
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
    if comet_name:
        comet = await Comets.get_or_none(name=comet_name)
        if not comet:
            comet = await Comets.create(
                designation=comet_name, 
                discovered_by=user,
                discovery_date=datetime.now(),
            )
        
    task = await CalculationTask.create(
        uuid=task_id,
        user=user,
        comet=comet,
        status=CalculationTaskStatus.PROCESSING,
        raw_observations = [obs.model_dump(mode='json') for obs in request.observations],
        location_code=request.options.get('location_code', '500'),
    )

    success = await send_orbit_calculation_task(
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


@router.get("/task/{task_id}", response_model=TaskResponse)
async def get_task_status(
    task_id: UUID,
    user: User = Depends(get_current_user),
):
    # Get the task from database
    task = await CalculationTask.get_or_none(uuid=task_id)
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Check if user has access to this task
    if task.user_id != user.uuid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this task"
        )
    
    return TaskResponse(
        task_id=task.uuid,
        status=task.status,
        submitted_at=task.created_at
    )


@router.get("/tasks", response_model=List[TaskListItem])
async def get_user_tasks(
    user: User = Depends(get_current_user),
):
    # Get all tasks for the user
    tasks = await CalculationTask.filter(user=user).order_by("-created_at").all()
    
    task_list = []
    for task in tasks:
        # Определяем тип задачи
        task_type = TaskType.ORBIT_CALCULATION
        if task.orbit_id and task.close_approach_id:
            task_type = TaskType.CLOSEST_APPROACH
            
        # Получаем имя кометы, если есть
        comet_name = None
        if task.comet_id:
            comet = await task.comet
            comet_name = comet.name if comet else None
            
        task_item = TaskListItem(
            task_id=task.uuid,
            status=task.status,
            task_type=task_type,
            submitted_at=task.created_at,
            completed_at=task.updated_at if task.status == "completed" else None,
            comet_name=comet_name
        )
        task_list.append(task_item)
    
    return task_list


@router.get("/task/{task_id}/result", response_model=TaskResultResponse)
async def get_task_result(
    task_id: UUID,
    user: User = Depends(get_current_user),
):
    # Get the task from database
    task = await CalculationTask.get_or_none(uuid=task_id)
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Check if user has access to this task
    if task.user_id != user.uuid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this task"
        )
    
    # Определяем тип задачи
    task_type = TaskType.ORBIT_CALCULATION
    if task.orbit_id and task.close_approach_id:
        task_type = TaskType.CLOSEST_APPROACH
    
    # Получаем имя кометы, если есть
    comet_name = None
    if task.comet_id:
        comet = await task.comet
        comet_name = comet.name if comet else None
    
    # Подготавливаем результаты
    orbit_result = None
    closest_approach_result = None
    
    if task.status == "completed":
        if task.orbit_id:
            orbit = await task.orbit
            if orbit:
                orbit_result = OrbitResult(
                    uuid=orbit.uuid,
                    semi_major_axis=orbit.semi_major_axis,
                    eccentricity=orbit.eccentricity,
                    inclination=orbit.inclination,
                    longitude_ascending_node=orbit.longitude_ascending_node,
                    argument_periapsis=orbit.argument_periapsis,
                    periapsis_time=orbit.periapsis_time
                )
        
        if task.close_approach_id:
            close_approach = await task.close_approach
            if close_approach:
                closest_approach_result = ClosestApproachResult(
                    approach_time=close_approach.approach_time,
                    distance_au=close_approach.distance_au,
                    distance_km=close_approach.distance_km
                )
    
    return TaskResultResponse(
        task_id=task.uuid,
        status=task.status,
        task_type=task_type,
        submitted_at=task.created_at,
        completed_at=task.updated_at if task.status == "completed" else None,
        orbit_result=orbit_result,
        closest_approach_result=closest_approach_result,
        comet_name=comet_name,
        error_message=task.error_message
    )


@router.post("/calculate-closest-approach", response_model=TaskResponse)
async def calculate_closest_approach(
    request: ClosestApproachRequest,
    user: User = Depends(get_current_user),
):
    # Find the orbit
    orbit = await Orbits.get_or_none(uuid=request.orbit_id)
    if not orbit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Orbit not found"
        )
    
    comet = await orbit.comet
    
    # Create a new task for closest approach calculation
    task_id = str(uuid.uuid4())
    task = await CalculationTask.create(
        uuid=task_id,
        user=user,
        comet=comet,
        orbit=orbit,
        status=CalculationTaskStatus.PROCESSING,
        location_code=request.options.get('location_code', '500'),
    )

    # Prepare orbit elements for calculation
    orbit_elements = {
        "semi_major_axis": orbit.semi_major_axis,
        "eccentricity": orbit.eccentricity,
        "inclination": orbit.inclination,
        "longitude_ascending_node": orbit.longitude_ascending_node,
        "argument_periapsis": orbit.argument_periapsis,
        "periapsis_time": orbit.periapsis_time
    }

    # Send closest approach calculation task to queue
    success = await send_closest_approach_task(
        task_id,
        str(user.uuid),
        orbit_elements,
        request.options
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
