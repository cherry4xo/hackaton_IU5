# notification_service/redis_listener.py
import asyncio
import json
import os
from datetime import datetime
from app.connections import manager
from app.schemas import Notification
from app import settings

import redis.asyncio as redis

redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    password=settings.REDIS_PASSWORD,
    db=0,
    decode_responses=True
)

async def process_result_message(stream_name: str, msg_data: dict):
    """Process a result message and send notification to user."""
    task_id = msg_data["task_id"]
    user_id = msg_data["user_id"]
    status = msg_data["status"]
    timestamp = msg_data.get("timestamp", datetime.utcnow().isoformat())

    # Determine event type based on queue and status
    if status == "completed":
        if stream_name == "orbit_result_queue":
            event = "orbit_calculation_completed"
        elif stream_name == "closest_approach_result_queue":
            event = "closest_approach_calculation_completed"
        else:  # result_queue (legacy)
            event = "orbit_calculation_completed"
        data = json.loads(msg_data["result"]) if msg_data["result"] else None
        error = None
    else:
        if stream_name == "orbit_result_queue":
            event = "orbit_calculation_failed"
        elif stream_name == "closest_approach_result_queue":
            event = "closest_approach_calculation_failed"
        else:  # result_queue (legacy)
            event = "orbit_calculation_failed"
        data = None
        error = msg_data["error"]

    notification = Notification(
        event=event,
        task_id=task_id,
        status=status,
        data=data,
        error=error,
        timestamp=datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    )

    # Отправляем пользователю
    await manager.send_personal_message(notification.model_dump_json(), user_id)
    print(f"Sent notification to user {user_id} (task_id={task_id}, queue={stream_name})")


async def listen_to_results():
    """
    Слушает все очереди результатов и рассылает уведомления
    """
    print("Notification Service: Listening to all result queues...")
    last_ids = {
        "result_queue": "$",
        "orbit_result_queue": "$",
        "closest_approach_result_queue": "$"
    }
    
    while True:
        try:
            response = await redis_client.xread(
                last_ids,
                count=1,
                block=1000
            )
            if not response:
                continue

            for stream, messages in response:
                for msg_id, msg_data in messages:
                    await process_result_message(stream, msg_data)
                    # Update last ID for this stream
                    last_ids[stream] = msg_id

        except Exception as e:
            print(f"Error while result processing: {e}")
            await asyncio.sleep(5)
