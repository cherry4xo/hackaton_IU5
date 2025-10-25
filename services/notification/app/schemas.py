from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any

class Notification(BaseModel):
    event: str  # "orbit_calculation_completed" | "orbit_calculation_failed"
    task_id: str
    status: str  # "completed" | "failed"
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: datetime