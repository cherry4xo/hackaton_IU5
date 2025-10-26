from app.utils.orbit_calculation import OrbitCalculator
from datetime import datetime
from app.models import CalculationTask
import json
from app.utils.image_processing import get_image_processor
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

calculator = OrbitCalculator()
image_processor = get_image_processor()

async def process_image_for_observations(task_id: str, observations: list, image_reference: Optional[str]) -> list:
    """Process image references and update observations with coordinates from images."""
    processed_observations = observations.copy()
    
    if not image_reference:
        return processed_observations
        
    try:
        logger.info(f"Processing image for task {task_id}: {image_reference}")
        
        # Detect stars in the image
        image = image_processor.download_image(image_reference)
        stars = image_processor.detect_stars(image)
        
        if stars:
            logger.info(f"Detected {len(stars)} stars in image {image_reference}")
            
            # For now, we'll use the first detected star's position to update all observations
            # In a more advanced implementation, we could match stars to specific observations
            if stars:
                # Use the brightest star (assuming it's the first one)
                primary_star = stars[0]
                
                # Update all observations with coordinates derived from the image
                # This is a simplified approach - in reality, we'd need proper astrometric calibration
                for obs in processed_observations:
                    # Extract coordinates from image using the star position
                    coords = image_processor.extract_coordinates_from_image(
                        image_reference,
                        pixel_x=primary_star["x"],
                        pixel_y=primary_star["y"]
                    )
                    
                    if coords:
                        obs["ra"], obs["dec"] = coords
                        logger.info(f"Updated observation with coordinates from image: RA={coords[0]}, Dec={coords[1]}")
                    else:
                        logger.warning(f"Failed to extract coordinates from image: {image_reference}")
        else:
            logger.warning(f"No stars detected in image: {image_reference}")
    except Exception as e:
        logger.error(f"Error processing image {image_reference}: {e}")
        
    return processed_observations

async def calculate_orbit_task(task_data: dict) -> Dict[str, Any]:
    """Calculate orbit parameters from observations."""
    task_id = task_data["task_id"]
    observations = task_data["observations"]
    image_reference = task_data.get("image_reference")
    options = task_data.get("options", {})

    # Process image for the entire task if available
    # processed_observations = await process_image_for_observations(task_id, observations, image_reference)

    try:
        # 1. Расчёт орбиты
        orbit_result = calculator.calculate_orbit(observations=observations)

        return {
            "task_id": task_id,
            "status": "completed",
            "result": {
                "orbit": orbit_result
            },
            "error": None
        }

    except Exception as e:
        return {
            "task_id": task_id,
            "status": "failed",
            "result": None,
            "error": str(e)
        }

async def calculate_closest_approach_task(task_data: dict) -> Dict[str, Any]:
    """Calculate closest approach time based on orbit elements and time range from options."""
    task_id = task_data["task_id"]
    orbit_elements = task_data["orbit_elements"]
    options = task_data.get("options", {})

    try:
        # Извлекаем временные границы из options
        start_time_str = options.get("observation_start_time")
        end_time_str = options.get("observation_end_time")

        # Если не заданы — используем значения по умолчанию
        if start_time_str:
            start_time = datetime.fromisoformat(start_time_str.replace("Z", ""))
        else:
            start_time = datetime.now()

        if end_time_str:
            end_time = datetime.fromisoformat(end_time_str.replace("Z", ""))
        else:
            end_time = datetime.now().replace(year=datetime.now().year + 1)

        # Количество шагов
        time_steps = options.get("time_steps", 1000)

        # Проверяем валидность диапазона
        if start_time >= end_time:
            raise ValueError("observation_start_time must be earlier than observation_end_time")

        # Расчёт сближения
        closest_approach_result = calculator.calculate_closest_approach(
            orbit_elements=orbit_elements,
            start_time=start_time,
            end_time=end_time,
            time_steps=time_steps
        )

        return {
            "task_id": task_id,
            "status": "completed",
            "result": {
                "closest_approach": closest_approach_result
            },
            "error": None
        }

    except Exception as e:
        logger.error(f"Error in calculate_closest_approach_task for task {task_id}: {e}", exc_info=True)
        return {
            "task_id": task_id,
            "status": "failed",
            "result": None,
            "error": str(e)
        }

async def process_task(task_data: dict) -> Dict[str, Any]:
    """Legacy function for backward compatibility - processes both orbit calculation and closest approach."""
    task_id = task_data["task_id"]
    observations = task_data["observations"]
    image_reference = task_data.get("image_reference")
    options = task_data.get("options", {})

    # Process image for the entire task if available
    # processed_observations = await process_image_for_observations(task_id, observations, image_reference)

    try:
        # 1. Расчёт орбиты
        orbit_result = calculator.calculate_orbit(observations=observations)

        # 2. Расчёт сближения
        start_time = datetime.fromisoformat(options.get("start_time", datetime.utcnow().isoformat()))
        end_time = datetime.fromisoformat(options.get("end_time", (datetime.utcnow().replace(year=datetime.utcnow().year + 1)).isoformat()))
        time_steps = options.get("time_steps", 1000)

        closest_approach_result = calculator.calculate_closest_approach(
            orbit_elements=orbit_result,
            start_time=start_time,
            end_time=end_time,
            time_steps=time_steps
        )

        return {
            "task_id": task_id,
            "status": "completed",
            "result": {
                "orbit": orbit_result,
                "closest_approach": closest_approach_result
            },
            "error": None
        }

    except Exception as e:
        return {
            "task_id": task_id,
            "status": "failed",
            "result": None,
            "error": str(e)
        }
