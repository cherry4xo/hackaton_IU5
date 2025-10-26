from pydantic import UUID4, BaseModel
from typing import List, Optional, Union
from datetime import datetime
from enum import Enum

class Observation(BaseModel):
    observation_time: datetime
    ra: float
    dec: float

class OrbitCalculationRequest(BaseModel):
    observations: List[Observation]
    image_reference: Optional[str] = None
    options: Optional[dict] = {}

class ClosestApproachRequest(BaseModel):
    orbit_id: UUID4
    options: Optional[dict] = {}

class TaskResponse(BaseModel):
    task_id: UUID4
    status: str
    submitted_at: datetime

class TaskType(str, Enum):
    ORBIT_CALCULATION = "orbit_calculation"
    CLOSEST_APPROACH = "closest_approach"

class TaskListItem(BaseModel):
    task_id: UUID4
    status: str
    task_type: TaskType
    submitted_at: datetime
    completed_at: Optional[datetime] = None
    comet_name: Optional[str] = None

class OrbitResult(BaseModel):
    uuid: UUID4
    semi_major_axis: float
    eccentricity: float
    inclination: float
    longitude_ascending_node: float
    argument_periapsis: float
    periapsis_time: datetime

class ClosestApproachResult(BaseModel):
    approach_time: datetime
    distance_au: Optional[float]
    distance_km: float

class TaskResultResponse(BaseModel):
    task_id: UUID4
    status: str
    task_type: TaskType
    submitted_at: datetime
    completed_at: Optional[datetime] = None
    orbit_result: Optional[OrbitResult] = None
    closest_approach_result: Optional[ClosestApproachResult] = None
    comet_name: Optional[str] = None
    error_message: Optional[str] = None
