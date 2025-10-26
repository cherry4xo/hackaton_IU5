from pydantic import UUID4, BaseModel
from typing import List, Optional
from datetime import datetime

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
