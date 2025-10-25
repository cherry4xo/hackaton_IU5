import redis.asyncio as redis

from app import settings

redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    password=settings.REDIS_PASSWORD,
    db=0,
    decode_responses=True
)

async def ping_redis():
    try:
        await redis_client.ping()
        print("Connected to Redis successfully")
    except Exception as e:
        print(f"Failed to connect to Redis: {e}")