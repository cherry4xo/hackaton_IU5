from app.utils.orbit_calculation import OrbitCalculator
from datetime import datetime
from app.models import CalculationTask
import json
from app.utils.image_processing import get_image_processor
import logging

logger = logging.getLogger(__name__)

calculator = OrbitCalculator()
image_processor = get_image_processor()

async def process_task(task_data: dict):
    task_id = task_data["task_id"]
    observations = task_data["observations"]
    options = task_data.get("options", {})

    # Process images in observations if available
    processed_observations = []
    for obs in observations:
        processed_obs = obs.copy()
        
        # Check if observation has an image reference
        if "image_reference" in obs and obs["image_reference"]:
            try:
                # Extract coordinates from image
                coords = image_processor.extract_coordinates_from_image(
                    obs["image_reference"]
                )
                
                if coords:
                    # Update observation with extracted coordinates
                    processed_obs["ra"], processed_obs["dec"] = coords
                    logger.info(f"Updated observation with coordinates from image: RA={coords[0]}, Dec={coords[1]}")
                else:
                    logger.warning(f"Failed to extract coordinates from image: {obs['image_reference']}")
            except Exception as e:
                logger.error(f"Error processing image {obs['image_reference']}: {e}")
        
        processed_observations.append(processed_obs)

    try:
        # 1. Расчёт орбиты
        orbit_result = calculator.calculate_orbit(processed_observations)

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
