#!/usr/bin/env python3
"""
Script to populate the database with initial data for all main tables.
"""

import os
import sys
import asyncio
import uuid
from datetime import datetime, timedelta
import random

# Add the services directories to the path so we can import the models
sys.path.extend([
    os.path.join(os.path.dirname(__file__), 'services', 'backend'),
    os.path.join(os.path.dirname(__file__), 'services', 'calculation')
])

# Import settings
from services.backend.app.settings import DB_URL, DB_CONNECTIONS
from services.backend.app.db import TORTOISE_ORM
from services.backend.app.enums import UserRole
from services.backend.app.models import (
    User, Observatories, Comets, Observations, 
    Orbits, Close_approaches, CalculationTask, CalculationTaskStatus
)

# Import Tortoise ORM
from tortoise import Tortoise

CONFIG = {
    "connections": DB_CONNECTIONS,
    "apps": {
        "models": {
            "models": ["app.models", "aerich.models"],
            "default_connection": "default"
        }
    }
} 


async def init_db():
    """Initialize the database connection."""
    await Tortoise.init(
        db_url=DB_URL,
        modules={'models': ['app.models']},
        config=CONFIG
    )

async def create_users():
    """Create sample users."""
    print("Creating sample users...")
    
    users_data = [
        {
            "uuid": uuid.uuid4(),
            "username": "admin",
            "email": "admin@example.com",
            "password_hash": "hashed_password_admin",
            "registration_date": datetime.now().date(),
            "role": UserRole.MODERATOR
        },
        {
            "uuid": uuid.uuid4(),
            "username": "researcher1",
            "email": "researcher1@example.com",
            "password_hash": "hashed_password_researcher1",
            "registration_date": datetime.now().date(),
            "role": UserRole.RESEARCHER
        },
        {
            "uuid": uuid.uuid4(),
            "username": "researcher2",
            "email": "researcher2@example.com",
            "password_hash": "hashed_password_researcher2",
            "registration_date": datetime.now().date(),
            "role": UserRole.RESEARCHER
        }
    ]
    
    users = []
    for user_data in users_data:
        user = await User.create(**user_data)
        users.append(user)
        print(f"Created user: {user.username}")
    
    return users

async def create_observatories():
    """Create sample observatories."""
    print("Creating sample observatories...")
    
    observatories_data = [
        {
            "uuid": uuid.uuid4(),
            "code": "MAUNA",
            "name": "Mauna Kea Observatory",
            "latitude": 19.8207,
            "longitude": -155.4681,
            "elevation_m": 4207.0
        },
        {
            "uuid": uuid.uuid4(),
            "code": "PALOMAR",
            "name": "Palomar Observatory",
            "latitude": 33.3563,
            "longitude": -116.8623,
            "elevation_m": 1713.0
        },
        {
            "uuid": uuid.uuid4(),
            "code": "LASILLA",
            "name": "La Silla Observatory",
            "latitude": -29.2833,
            "longitude": -70.7000,
            "elevation_m": 2400.0
        }
    ]
    
    observatories = []
    for obs_data in observatories_data:
        obs = await Observatories.create(**obs_data)
        observatories.append(obs)
        print(f"Created observatory: {obs.name}")
    
    return observatories

async def create_comets(users):
    """Create sample comets."""
    print("Creating sample comets...")
    
    comets_data = [
        {
            "uuid": uuid.uuid4(),
            "designation": "C/2020 F3",
            "name": "Comet NEOWISE",
            "discovered_by": users[1],  # researcher1
            "discovery_date": datetime.now() - timedelta(days=365)
        },
        {
            "uuid": uuid.uuid4(),
            "designation": "C/2021 A1",
            "name": "Comet Leonard",
            "discovered_by": users[2],  # researcher2
            "discovery_date": datetime.now() - timedelta(days=730)
        }
    ]
    
    comets = []
    for comet_data in comets_data:
        comet = await Comets.create(**comet_data)
        comets.append(comet)
        print(f"Created comet: {comet.name}")
    
    return comets

async def create_observations(users, observatories, comets):
    """Create sample observations."""
    print("Creating sample observations...")
    
    observations = []
    
    # Create observations for Comet NEOWISE
    for i in range(5):
        obs_data = {
            "uuid": uuid.uuid4(),
            "comet": comets[0],  # NEOWISE
            "observatory": observatories[i % len(observatories)],
            "observer": users[1 + (i % 2)],  # Alternate between researchers
            "observation_time": datetime.now() - timedelta(days=300 - i*10),
            "ra_deg": 120.5 + i*5.0,
            "dec_deg": 30.2 + i*2.0,
            "altitude_deg": 45.0 + i*3.0,
            "azimuth_deg": 90.0 + i*10.0,
            "processed": True
        }
        obs = await Observations.create(**obs_data)
        observations.append(obs)
        print(f"Created observation for {comets[0].name}")
    
    # Create observations for Comet Leonard
    for i in range(3):
        obs_data = {
            "uuid": uuid.uuid4(),
            "comet": comets[1],  # Leonard
            "observatory": observatories[i % len(observatories)],
            "observer": users[1 + (i % 2)],  # Alternate between researchers
            "observation_time": datetime.now() - timedelta(days=700 - i*20),
            "ra_deg": 80.5 + i*7.0,
            "dec_deg": -15.2 + i*3.0,
            "altitude_deg": 35.0 + i*5.0,
            "azimuth_deg": 120.0 + i*15.0,
            "processed": True
        }
        obs = await Observations.create(**obs_data)
        observations.append(obs)
        print(f"Created observation for {comets[1].name}")
    
    return observations

async def create_orbits(comets):
    """Create sample orbits."""
    print("Creating sample orbits...")
    
    orbits_data = [
        {
            "uuid": uuid.uuid4(),
            "comet": comets[0],  # NEOWISE
            "semi_major_axis": 1000.0,
            "eccentricity": 0.999,
            "inclination": 125.0,
            "longitude_ascending_node": 250.0,
            "argument_periapsis": 150.0,
            "periapsis_time": datetime.now() - timedelta(days=200),
            "epoch": datetime.now() - timedelta(days=300),
            "method": "least_squares",
            "is_hyperbolic": True
        },
        {
            "uuid": uuid.uuid4(),
            "comet": comets[1],  # Leonard
            "semi_major_axis": None,  # Hyperbolic orbit
            "eccentricity": 1.005,
            "inclination": 120.0,
            "longitude_ascending_node": 200.0,
            "argument_periapsis": 100.0,
            "periapsis_time": datetime.now() - timedelta(days=500),
            "epoch": datetime.now() - timedelta(days=600),
            "method": "least_squares",
            "is_hyperbolic": True
        }
    ]
    
    orbits = []
    for orbit_data in orbits_data:
        orbit = await Orbits.create(**orbit_data)
        orbits.append(orbit)
        print(f"Created orbit for {orbit.comet.name}")
    
    return orbits

async def create_close_approaches(comets, orbits):
    """Create sample close approaches."""
    print("Creating sample close approaches...")
    
    approaches_data = [
        {
            "uuid": uuid.uuid4(),
            "comet": comets[0],  # NEOWISE
            "approach_time": datetime.now() + timedelta(days=100),
            "distance_au": 0.5,
            "distance_km": 74800000.0,
            "orbit": orbits[0]
        },
        {
            "uuid": uuid.uuid4(),
            "comet": comets[1],  # Leonard
            "approach_time": datetime.now() - timedelta(days=30),
            "distance_au": 0.233,
            "distance_km": 34860000.0,
            "orbit": orbits[1]
        }
    ]
    
    approaches = []
    for approach_data in approaches_data:
        approach = await Close_approaches.create(**approach_data)
        approaches.append(approach)
        print(f"Created close approach for {approach.comet.name}")
    
    return approaches

async def create_calculation_tasks(users, comets, orbits=None, close_approaches=None):
    """Create sample calculation tasks."""
    print("Creating sample calculation tasks...")
    
    tasks_data = [
        {
            "uuid": uuid.uuid4(),
            "user": users[0],  # admin
            "comet": comets[0],  # NEOWISE
            "status": CalculationTaskStatus.COMPLETED,
            "observation_start_time": datetime.now() - timedelta(days=350),
            "observation_end_time": datetime.now() - timedelta(days=250),
            "location_code": "MAUNA",
            "error_message": None,
            "raw_observations": [
                {
                    "observation_time": (datetime.now() - timedelta(days=300)).isoformat(),
                    "ra": 120.5,
                    "dec": 30.2
                },
                {
                    "observation_time": (datetime.now() - timedelta(days=290)).isoformat(),
                    "ra": 125.5,
                    "dec": 32.2
                }
            ]
        },
        {
            "uuid": uuid.uuid4(),
            "user": users[1],  # researcher1
            "comet": comets[1],  # Leonard
            "status": CalculationTaskStatus.FAILED,
            "observation_start_time": datetime.now() - timedelta(days=750),
            "observation_end_time": datetime.now() - timedelta(days=650),
            "location_code": "PALOMAR",
            "error_message": "Insufficient observations for orbit determination",
            "raw_observations": [
                {
                    "observation_time": (datetime.now() - timedelta(days=700)).isoformat(),
                    "ra": 80.5,
                    "dec": -15.2
                }
            ]
        }
    ]
    
    if orbits and len(orbits) > 0:
        tasks_data[0]["orbit"] = orbits[0]
    
    if close_approaches and len(close_approaches) > 0:
        tasks_data[0]["close_approach"] = close_approaches[0]
    
    tasks = []
    for task_data in tasks_data:
        task = await CalculationTask.create(**task_data)
        tasks.append(task)
        print(f"Created calculation task for {task.user.username}")
    
    return tasks

async def main():
    """Main function to populate the database."""
    print("Starting database population script...")
    
    try:
        # Initialize database connection
        await init_db()
        print("Database connection initialized.")
        
        # Create sample data
        users = await create_users()
        observatories = await create_observatories()
        comets = await create_comets(users)
        observations = await create_observations(users, observatories, comets)
        orbits = await create_orbits(comets)
        close_approaches = await create_close_approaches(comets, orbits)
        calculation_tasks = await create_calculation_tasks(users, comets, orbits, close_approaches)
        
        print("\nDatabase population completed successfully!")
        print(f"Created {len(users)} users")
        print(f"Created {len(observatories)} observatories")
        print(f"Created {len(comets)} comets")
        print(f"Created {len(observations)} observations")
        print(f"Created {len(orbits)} orbits")
        print(f"Created {len(close_approaches)} close approaches")
        print(f"Created {len(calculation_tasks)} calculation tasks")
        
    except Exception as e:
        print(f"Error populating database: {e}")
        raise
    finally:
        await Tortoise.close_connections()

if __name__ == "__main__":
    asyncio.run(main())
