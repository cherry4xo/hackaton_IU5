# notification_service/main.py
import asyncio
from fastapi import FastAPI, WebSocket, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
import jwt
from contextlib import asynccontextmanager

from app.connections import manager
from app.redis_listener import listen_to_results
from app import settings

ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

app = FastAPI(title="Notification Service")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Запускаем слушатель Redis в фоне
    task = asyncio.create_task(listen_to_results())
    yield
    task.cancel()

app.router.lifespan_context = lifespan

def decode_jwt(token: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")  # предполагаем, что sub = user_id
    except jwt.PyJWTError:
        return None

@app.websocket("/ws/notify")
async def websocket_endpoint(websocket: WebSocket, token: str = Depends(oauth2_scheme)):
    """
    WebSocket-эндпоинт для получения уведомлений.
    Аутентификация через JWT из query или заголовка.
    """
    user_id = decode_jwt(token)
    if not user_id:
        await websocket.close(code=1008, reason="Invalid token")
        return

    await manager.connect(websocket, user_id)
    print(f"🟢 Пользователь {user_id} подключился к уведомлениям")

    try:
        while True:
            # Держим соединение открытым
            await websocket.receive_text()
    except:
        pass
    finally:
        manager.disconnect(websocket, user_id)
        print(f"🔴 Пользователь {user_id} отключился от уведомлений")