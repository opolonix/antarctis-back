import os, fastapi, importlib, sqlalchemy
from sqlalchemy.orm import Session

def include_handlers(folder: str, app: fastapi.FastAPI, router: str = "router"):
    """подвязывает обработчики из определенной папки"""

    for file in os.listdir(folder):
        if file.endswith(".py") and os.path.isfile(os.path.join(folder, file)):
            module = importlib.import_module(f"{folder}.{file[:-3]}")
            if hasattr(module, router):
                app.include_router(getattr(module, router))

def engine() -> Session:
    """возвращает обьект для создания сессий"""
    from config import CONNECT_RAW
    e = sqlalchemy.create_engine(CONNECT_RAW)
    return Session(bind=e)