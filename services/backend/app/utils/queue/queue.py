import json
import logging
from datetime import datetime
from typing import Any, Dict

from app.utils.queue.database import redis_client
from app.utils.queue.schemas import OrbitCalculationRequest

logger = logging.getLogger(__name__)


def _clean_message(message: Dict[str, Any]) -> Dict[str, Any]:
    """Clean message data for Redis stream."""
    clean_message = {}
    for k, v in message.items():
        if v is None:
            clean_message[k] = ""
        elif isinstance(v, (dict, list)):
            clean_message[k] = json.dumps(v)
        elif isinstance(v, (str, int, float, bytes)):
            clean_message[k] = v
        else:
            clean_message[k] = str(v)
    return clean_message


async def send_orbit_calculation_task(task_id: str, user_id: str, request: OrbitCalculationRequest):
    """Send orbit calculation task to the orbit calculation queue."""
    message = {
        "task_id": task_id,
        "user_id": user_id,
        "timestamp": datetime.now().isoformat(),
        "observations": json.dumps([obs.model_dump(mode='json') for obs in request.observations]),
        "options": request.options or {}
    }

    clean_message = _clean_message(message)

    try:
        await redis_client.xadd("orbit_calculation_queue", clean_message)
        logger.info(f"Task {task_id} added into orbit_calculation_queue")
        return True
    except Exception as e:
        logger.error(f"Redis sending error: {e}")
        return False


async def send_closest_approach_task(task_id: str, user_id: str, orbit_elements: dict, options: dict = None):
    message = {
        "task_id": task_id,
        "user_id": user_id,
        "timestamp": datetime.now().isoformat(),
        "orbit_elements": json.dumps(orbit_elements),
        "options": json.dumps(options or {})
    }

    clean_message = _clean_message(message)

    try:
        await redis_client.xadd("closest_approach_queue", clean_message)
        logger.info(f"Task {task_id} added into closest_approach_queue")
        return True
    except Exception as e:
        logger.error(f"Redis sending error: {e}")
        return False


# For backward compatibility
async def send_calculation_task(task_id: str, user_id: str, request: OrbitCalculationRequest):
    message = {
        "task_id": task_id,
        "user_id": user_id,
        "timestamp": datetime.now().isoformat(),
        "observations": json.dumps([obs.model_dump(mode='json') for obs in request.observations]),
        "image_reference": request.image_reference or "",
        "options": json.dumps(request.options or {})
    }
    
    clean_message = _clean_message(message)
    
    try:
        await redis_client.xadd("input_queue", clean_message)
        logger.info(f"Task {task_id} added into input_queue")
        return True
    except Exception as e:
        logger.error(f"Redis sending error: {e}")
        return False
