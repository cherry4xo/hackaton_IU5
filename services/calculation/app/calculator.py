from app.utils.orbit_calculation import OrbitCalculator
from datetime import datetime
from app.models import CalculationTask
import json

calculator = OrbitCalculator()

async def process_task(task_data: dict):
    task_id = task_data["task_id"]
    observations = task_data["observations"]
    options = task_data.get("options", {})

    try:
        # 1. Расчёт орбиты
        orbit_result = calculator.calculate_orbit(observations)

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