import logging
from datetime import datetime

from app.utils.queue.database import redis_client
from app.utils.queue.schemas import OrbitCalculationRequest

logger = logging.getLogger(__name__)


async def send_calculation_task(task_id: str, user_id: str, request: OrbitCalculationRequest):
    message = {
        "task_id": task_id,
        "user_id": user_id,
        "timestamp": datetime.utcnow().isoformat(),
        "observations": [obs.dict() for obs in request.observations],
        "options": request.options or {}
    }

    try:
        await redis_client.xadd("input_queue", message)
        logger.info(f"Task {task_id} added into input_queue")
        return True
    except Exception as e:
        logger.error(f"Redis sending error: {e}")
        return False