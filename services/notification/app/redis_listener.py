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

async def listen_to_results():
    """
    Слушает result_queue и рассылает уведомления
    """
    print("Notification Service: Listening to result_queue...")
    while True:
        try:
            response = await redis_client.xread(
                {"result_queue": "$"},
                count=1,
                block=1000
            )
            if not response:
                continue

            stream, messages = response[0]
            msg_id, msg_data = messages[0]

            task_id = msg_data["task_id"]
            user_id = msg_data["user_id"]
            status = msg_data["status"]
            timestamp = msg_data.get("timestamp", datetime.utcnow().isoformat())

            # Формируем уведомление
            if status == "completed":
                event = "orbit_calculation_completed"
                data = json.loads(msg_data["result"]) if msg_data["result"] else None
                error = None
            else:
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
            await manager.send_personal_message(notification.json(), user_id)
            print(f"Sent notification to user {user_id} (task_id={task_id})")

        except Exception as e:
            print(f"Error while result processing: {e}")
            await asyncio.sleep(5)