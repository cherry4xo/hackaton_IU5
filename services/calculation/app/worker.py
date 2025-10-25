import logging
import asyncio
import json
from datetime import datetime
from app.utils.redis_client import redis_client
from app.db import init
from app.calculator import process_task
from app.models import CalculationTask, Comets, Orbits, Close_approaches

logger = logging.getLogger(__name__)


async def run_worker():
    logging.info("Started Calculation Service")

    # Инициализация БД
    await init()

    while True:
        try:
            # Читаем из input_queue (block 1s)
            response = await redis_client.xread(
                {"input_queue": "$"},
                count=1,
                block=1000
            )

            if not response:
                continue

            # Парсим сообщение
            stream, messages = response[0]
            msg_id, msg_data = messages[0]
            task_data = json.loads(json.dumps(msg_data))  # нормализуем

            task_id = task_data["task_id"]

            # Находим задачу в БД
            task = await CalculationTask.get_or_none(uuid=task_id)
            if not task:
                logger.info(f"Not found task {task_id} in DB")
                continue

            # Обновляем статус
            task.status = "processing"
            await task.save()

            # Выполняем расчёт
            result = await process_task(task_data)

            # Обновляем задачу
            task.completed_at = datetime.now()
            task.status = result["status"]

            if result["status"] == "completed":
                # Привязываем или создаём комету
                comet = task.comet
                if not comet:
                    comet = await Comets.create(
                        designation=f"C/{datetime.now().year} {task_id[:6].upper()}",
                        name=f"Comet {task_id[:8]}",
                        discovered_by_id=task.user_id,
                        discovery_date=datetime.now()
                    )
                    task.comet = comet

                # Создаём Orbits
                orbit = await Orbits.create(
                    comet=comet,
                    semi_major_axis=result["result"]["orbit"]["semi_major_axis"],
                    eccentricity=result["result"]["orbit"]["eccentricity"],
                    inclination=result["result"]["orbit"]["inclination"],
                    longitude_ascending_node=result["result"]["orbit"]["longitude_ascending_node"],
                    argument_periapsis=result["result"]["orbit"]["argument_periapsis"],
                    periapsis_time=result["result"]["orbit"]["periapsis_time"],
                    epoch=task.created_at,
                    method="least_squares",
                    is_hyperbolic=result["result"]["orbit"]["semi_major_axis"] is None
                )
                task.orbit = orbit

                # Создаём Close_approaches
                ca = await Close_approaches.create(
                    comet=comet,
                    approach_time=result["result"]["closest_approach"]["time"],
                    distance_au=result["result"]["closest_approach"]["distance_au"],
                    distance_km=result["result"]["closest_approach"]["distance_km"],
                    orbit=orbit
                )
                task.close_approach = ca

            else:
                task.error_message = result["error"]

            await task.save()

            # Отправляем результат в result_queue
            await redis_client.xadd("result_queue", {
                "task_id": task_id,
                "status": result["status"],
                "user_id": task.user_id,
                "result": json.dumps(result["result"]) if result["result"] else "",
                "error": result["error"] or "",
                "timestamp": datetime.utcnow().isoformat()
            })

            logger.info(f"Completed task {task_id}: {result['status']}")

        except Exception as e:
            logger.exception(f"Worker error: {e}")
            await asyncio.sleep(5)