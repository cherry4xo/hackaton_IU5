import logging
import asyncio
import json
from datetime import datetime
from typing import Dict, Any

from fastapi import FastAPI
from app.utils.redis_client import redis_client
from app.db import init
from app.calculator import calculate_orbit_task, calculate_closest_approach_task, process_task
from app.models import CalculationTask, Comets, Orbits, Close_approaches
from app.enums import CalculationTaskType

logger = logging.getLogger(__name__)


async def handle_orbit_calculation(task_data: dict, task: CalculationTask) -> Dict[str, Any]:
    """Handle orbit calculation task and save results to database."""
    result = await calculate_orbit_task(task_data)
    
    # Обновляем задачу
    task.updated_at = datetime.now()
    task.status = result["status"]

    if result["status"] == "completed":
        # Привязываем или создаём комету
        comet = task.comet
        if not comet:
            task_id = task_data["task_id"]
            comet = await Comets.create(
                designation=f"C/{datetime.now().year} {task_id[:6].upper()}",
                name=f"Comet {task_id[:8]}",
                discovered_by_id=task.user_id,
                discovery_date=datetime.now()
            )
            task.comet = comet

        # Создаём Orbits
        orbit_result = result["result"]["orbit"]
        orbit = await Orbits.create(
            comet=comet,
            semi_major_axis=orbit_result["semi_major_axis"],
            eccentricity=orbit_result["eccentricity"],
            inclination=orbit_result["inclination"],
            longitude_ascending_node=orbit_result["longitude_ascending_node"],
            argument_periapsis=orbit_result["argument_periapsis"],
            periapsis_time=orbit_result["periapsis_time"],
            epoch=task.created_at,
            method="least_squares",
            is_hyperbolic=orbit_result["semi_major_axis"] is None
        )
        task.orbit = orbit
    else:
        task.error_message = result["error"]

    await task.save()
    return result


async def handle_closest_approach(task_data: dict, task: CalculationTask) -> Dict[str, Any]:
    """Handle closest approach calculation task and save results to database."""
    result = await calculate_closest_approach_task(task_data)
    
    # Обновляем задачу
    task.updated_at = datetime.now()
    task.status = result["status"]

    if result["status"] == "completed":
        # Создаём Close_approaches
        ca_result = result["result"]["closest_approach"]
        ca = await Close_approaches.create(
            comet=task.comet,
            approach_time=ca_result["time"],
            distance_au=ca_result["distance_au"],
            distance_km=ca_result["distance_km"],
            orbit=task.orbit
        )
        task.close_approach = ca
    else:
        task.error_message = result["error"]

    await task.save()
    return result


async def process_single_task(queue_name: str, task_type: CalculationTaskType):
    """Process a single task from the specified queue."""
    try:
        # Читаем из очереди (block 1s)
        response = await redis_client.xread(
            {queue_name: "$"},
            count=1,
            block=1000
        )

        if not response:
            return

        # Парсим сообщение
        stream, messages = response[0]
        msg_id, msg_data = messages[0]
        task_data = json.loads(json.dumps(msg_data))  # нормализуем

        task_id = task_data["task_id"]

        # Находим задачу в БД
        task = await CalculationTask.get_or_none(uuid=task_id)
        if not task:
            logger.info(f"Not found task {task_id} in DB")
            return

        # Обновляем статус
        task.status = "processing"
        await task.save()

        # Выполняем расчёт в зависимости от типа задачи
        if task_type == CalculationTaskType.ORBIT_CALCULATION:
            result = await handle_orbit_calculation(task_data, task)
            result_queue = "orbit_result_queue"
        elif task_type == CalculationTaskType.CLOSEST_APPROACH:
            result = await handle_closest_approach(task_data, task)
            result_queue = "closest_approach_result_queue"
        else:
            # Legacy handling for backward compatibility
            result = await process_task(task_data)
            
            # Обновляем задачу
            task.updated_at = datetime.now()
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
            result_queue = "result_queue"

        # Отправляем результат в соответствующую очередь
        await redis_client.xadd(result_queue, {
            "task_id": task_id,
            "status": result["status"],
            "user_id": task.user_id,
            "result": json.dumps(result["result"]) if result["result"] else "",
            "error": result["error"] or "",
            "timestamp": datetime.utcnow().isoformat()
        })

        logger.info(f"Completed task {task_id}: {result['status']} from queue {queue_name}")

    except Exception as e:
        logger.exception(f"Worker error processing task from {queue_name}: {e}")
        await asyncio.sleep(1)  # Shorter sleep for individual queue errors


async def run_worker():
    logging.info("Started Calculation Service")

    app = FastAPI()

    # Инициализация БД
    await init(app)

    while True:
        # Process tasks from different queues concurrently
        await asyncio.gather(
            process_single_task("orbit_calculation_queue", CalculationTaskType.ORBIT_CALCULATION),
            process_single_task("closest_approach_queue", CalculationTaskType.CLOSEST_APPROACH),
            process_single_task("input_queue", None),  # For backward compatibility
            return_exceptions=True
        )
        
        # Small delay to prevent excessive CPU usage
        await asyncio.sleep(0.1)
