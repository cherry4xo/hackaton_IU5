from pydantic import BaseModel
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

class TaskResponse(BaseModel):
    task_id: str
    status: str
    submitted_at: datetime
