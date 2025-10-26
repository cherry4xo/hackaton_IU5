import asyncio
import json
import logging
from datetime import datetime, timezone
from app.connections import manager
from app.schemas import Notification
from app import settings

import redis.asyncio as redis

logger = logging.getLogger(__name__)

redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    password=settings.REDIS_PASSWORD,
    db=0,
    decode_responses=True
)

def parse_timestamp(ts: str) -> datetime:
    """Безопасный парсинг ISO-формата с поддержкой 'Z'."""
    if ts.endswith('Z'):
        ts = ts[:-1] + '+00:00'
    try:
        return datetime.fromisoformat(ts)
    except ValueError as e:
        logger.error(f"Invalid timestamp format: {ts}")
        return datetime.now(timezone.utc)

async def process_result_message(stream_name: str, msg_data: dict):
    """Process a result message and send notification to user."""
    # Проверка обязательных полей
    if not all(k in msg_data for k in ("task_id", "user_id", "status")):
        logger.error(f"Invalid message format, missing fields: {msg_data}")
        return

    task_id = msg_data["task_id"]
    user_id = msg_data["user_id"]
    status = msg_data["status"]
    raw_result = msg_data.get("result", None)
    error_msg = msg_data.get("error", None)
    timestamp_str = msg_data.get("timestamp", datetime.utcnow().isoformat())

    # Определение события
    if status == "completed":
        event = {
            "orbit_result_queue": "orbit_calculation_completed",
            "closest_approach_result_queue": "closest_approach_calculation_completed",
        }.get(stream_name, "orbit_calculation_completed")
        error = None
        try:
            data = json.loads(raw_result) if raw_result and raw_result.strip() else None
        except (json.JSONDecodeError, TypeError) as e:
            logger.error(f"Failed to parse result JSON for task {task_id}: {e}")
            data = None
            error = "Invalid result data format"
    else:
        event = {
            "orbit_result_queue": "orbit_calculation_failed",
            "closest_approach_result_queue": "closest_approach_calculation_failed",
        }.get(stream_name, "orbit_calculation_failed")
        data = None
        error = error_msg or "Unknown error"

    try:
        timestamp = parse_timestamp(timestamp_str)
    except Exception as e:
        logger.error(f"Invalid timestamp in message: {timestamp_str}, {e}")
        timestamp = datetime.now(timezone.utc)

    notification = Notification(
        event=event,
        task_id=task_id,
        status=status,
        data=data,
        error=error,
        timestamp=timestamp
    )

    try:
        await manager.send_personal_message(notification.model_dump_json(), user_id)
        logger.info(f"Sent notification to user {user_id} (task_id={task_id}, queue={stream_name})")
    except Exception as e:
        logger.error(f"Failed to send notification to user {user_id}: {e}")


async def listen_to_results():
    """Слушает все очереди результатов и рассылает уведомления."""
    logger.info("Notification Service: Listening to all result queues...")
    last_ids = {
        "result_queue": "0",
        "orbit_result_queue": "0",
        "closest_approach_result_queue": "0"
    }

    while True:
        try:
            response = await redis_client.xread(
                last_ids,
                count=10,
                block=1000
            )
            if not response:
                continue

            logger.info(f"Received {len(response)} messages from result queues")

            for stream, messages in response:
                for msg_id, msg_data in messages:
                    await process_result_message(stream, msg_data)
                    last_ids[stream] = msg_id

        except Exception as e:
            logger.error(f"Error while processing results: {e}", exc_info=True)
            await asyncio.sleep(5)