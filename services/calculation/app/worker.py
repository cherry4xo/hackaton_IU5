from contextlib import asynccontextmanager
import logging
import asyncio
import json
from datetime import datetime
from typing import Dict, Any
from uuid import UUID

from fastapi import FastAPI
from tortoise import Tortoise
from app.utils.redis_client import redis_client
from app.db import TORTOISE_ORM, register_db
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
        comet = None
        if task.comet_id:
            comet = await task.comet
        
        if not comet:
            task_id = task_data["task_id"]
            designation = f"C/{datetime.now().year} {task_id[:6].upper()}"
            comet = await Comets.get_or_none(designation=designation)
            if not comet:
                comet = await Comets.create(
                    designation=designation,
                    name=f"Comet {task_id[:8]}",
                    discovered_by_id=task.user_id,
                    discovery_date=datetime.now()
                )
            task.comet = comet
            await task.save()  # <-- Сохраняем, чтобы comet_id сохранился в task

        # Создаём Orbits
        orbit_result = result["result"]["orbit"]
        orbit = await Orbits.create(
            comet=comet,  # Преобразуем UUID в строку
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
        await task.save()
    return result


async def handle_closest_approach(task_data: dict, task: CalculationTask) -> Dict[str, Any]:
    """Handle closest approach calculation task and save results to database."""
    result = await calculate_closest_approach_task(task_data)
    
    # Обновляем задачу
    task.updated_at = datetime.now()
    task.status = result["status"]

    if result["status"] == "completed":
        # Получаем comet и orbit
        comet = await task.comet if task.comet_id else None
        orbit = task.orbit
        
        # Проверяем, что у нас есть необходимые данные
        if not comet or not orbit:
            raise ValueError("Cannot create Close_approaches without comet and orbit")
        
        # Создаём Close_approaches
        ca_result = result["result"]["closest_approach"]
        ca = await Close_approaches.create(
            comet=comet,
            approach_time=ca_result["time"],
            distance_au=ca_result["distance_au"],
            distance_km=ca_result["distance_km"],
            orbit=orbit
        )
        task.close_approach = ca
    else:
        task.error_message = result["error"]

    await task.save()
    return result


async def process_single_task(queue_name: str, task_type: CalculationTaskType, last_ids: dict):
    """Process a single task from the specified queue."""
    try:
        # Читаем из очереди (block 1s)
        response = await redis_client.xread(
            {queue_name: last_ids.get(queue_name, "$")},
            count=1,
            block=1000
        )

        if not response:
            return None

        # Парсим сообщение
        stream, messages = response[0]
        msg_id, msg_data = messages[0]
        
        # Нормализуем данные сообщения
        task_data = {}
        for key, value in msg_data.items():
            # Декодируем значения, если они закодированы в JSON
            if isinstance(value, str):
                try:
                    # Проверяем, является ли строка JSON-закодированным значением
                    if value.startswith(('{', '[')) or value in ('true', 'false') or value.isdigit():
                        task_data[key] = json.loads(value)
                    else:
                        task_data[key] = value
                except (json.JSONDecodeError, TypeError):
                    task_data[key] = value
            else:
                task_data[key] = value

        task_id = task_data["task_id"]

        # Находим задачу в БД
        task = await CalculationTask.get_or_none(uuid=task_id)
        if not task:
            logger.info(f"Not found task {task_id} in DB")
            return (stream, msg_id)

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
                    distance_km=result["result"]["closest_approach"]["distance_km"],
                    orbit=orbit
                )
                # Note: distance_au is nullable, so we only set it if it's not None
                if result["result"]["closest_approach"]["distance_au"] is not None:
                    ca.distance_au = result["result"]["closest_approach"]["distance_au"]
                    await ca.save()
                task.close_approach = ca

            else:
                task.error_message = result["error"]

            await task.save()
            result_queue = "result_queue"

        # Отправляем результат в соответствующую очередь
        await redis_client.xadd(result_queue, {
            "task_id": str(task_id),
            "status": result["status"],
            "user_id": str(task.user_id),
            "result": json.dumps(
                result["result"],
                default=lambda o: o.isoformat() if isinstance(o, datetime) else str(o)
            ) if result["result"] else "",
            "error": result["error"] or "",
            "timestamp": datetime.now().isoformat()
        })

        logger.info(f"Completed task {task_id}: {result['status']} from queue {queue_name}")
        return (stream, msg_id)

    except Exception as e:
        logger.exception(f"Worker error processing task from {queue_name}: {e}")
        await asyncio.sleep(1)  # Shorter sleep for individual queue errors
        return None


async def run_worker():
    logging.info("Started Calculation Service")

    app = FastAPI()

    register_db(app)
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas(safe=True)

    # Initialize last IDs for each queue to "0" to process all existing messages
    last_ids = {
        "orbit_calculation_queue": "0",
        "closest_approach_queue": "0",
        "input_queue": "0"
    }

    # Define queue configurations
    queue_configs = [
        ("orbit_calculation_queue", CalculationTaskType.ORBIT_CALCULATION),
        ("closest_approach_queue", CalculationTaskType.CLOSEST_APPROACH),
        ("input_queue", None)  # For backward compatibility
    ]

    while True:
        # Process tasks from different queues concurrently
        tasks = [
            process_single_task(queue_name, task_type, last_ids)
            for queue_name, task_type in queue_configs
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Update last IDs based on successful results
        for i, result in enumerate(results):
            if isinstance(result, tuple) and len(result) == 2:
                stream_name, msg_id = result
                last_ids[stream_name] = msg_id
        
        # Small delay to prevent excessive CPU usage
        await asyncio.sleep(0.1)
