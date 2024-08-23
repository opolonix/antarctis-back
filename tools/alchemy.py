import os, fastapi, importlib, sqlalchemy
from sqlalchemy.orm import sessionmaker

def include_handlers(folder: str, app: fastapi.FastAPI, router: str = "router"):
    """подвязывает обработчики из определенной папки"""

    for file in os.listdir(folder):
        if file.endswith(".py") and os.path.isfile(os.path.join(folder, file)):
            module = importlib.import_module(f"{folder}.{file[:-3]}")
            if hasattr(module, router):
                app.include_router(getattr(module, router))

class Engine:
    _instance = None
    session: sqlalchemy.orm.Session

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Engine, cls).__new__(cls)

            from config import CONNECT_RAW

            cls._instance.engine = sqlalchemy.create_engine(CONNECT_RAW)
            cls._instance.sessionmaker = sessionmaker(bind=cls._instance.engine)
            cls._instance.session = cls._instance.sessionmaker()

        return cls._instance
    
    def __init__(self) -> None:
        self.engine: sqlalchemy.engine.Engine
        self.sessionmaker: sqlalchemy.orm.sessionmaker
        self.session: sqlalchemy.orm.Session
    
engine = Engine()