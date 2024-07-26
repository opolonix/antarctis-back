from typing import List, Literal
from sqlalchemy import Column, Boolean, String, Integer, DateTime, ForeignKey, JSON
from sqlalchemy.orm import DeclarativeBase, relationship, Mapped

from datetime import datetime
import random
import string
import uuid

class Base(DeclarativeBase):
    pass

class Client(Base):
    __tablename__ = 'clients'

    id: int = Column(Integer, primary_key=True, autoincrement=True)

    first_name: str = Column(String(128), comment="имя клиента", default="")
    last_name: str = Column(String(128), comment="фамилия клиента", default="")
    father_name: str = Column(String(128), comment="отчество клиента", default="")

    phone: str = Column(String(20), comment="номер телефона клиента", index=True)
    company_name: str = Column(String(256), comment="название компании клиента")
    email: str = Column(String(128), comment="имеил клиента клиента")
    facility_name: str = Column(String(128), comment="название обьекта клиента")
    adress: str = Column(String(256), comment="адрес у клиента")

    join_at: datetime = Column(DateTime, default=datetime.now, comment="когда клиент присоеденился к системе")
    last_activity: datetime = Column(DateTime, default=datetime.now, comment="дата последней активности клиента")
    blocked: bool = Column(Boolean, default=False, comment="флаг о блокировке, на будущее")
    is_admin: bool = Column(Boolean, default=False, comment="Разрешение на чтение чужих рапортов")

    sessions: Mapped[List["Auth"]] = relationship("Auth", back_populates="client", cascade="all, delete-orphan")
    raports: Mapped[List["Raport"]] = relationship("Raport", back_populates="client")

class Auth(Base):
    __tablename__ = 'sessions'

    id: int = Column(Integer, primary_key=True, autoincrement=True)

    token: str = Column(String(64), comment="токен авторизации", index=True, default=lambda: ''.join(random.choice(string.ascii_letters + string.digits) for i in range(64)))
    client_id: int = Column(Integer, ForeignKey("clients.id"), comment="ссылка на клиента")
    client: Mapped["Client"] = relationship(back_populates="sessions")

    sms_code: str = Column(String(10), nullable=False) # ожидаемый смс код для входа
    verefied: bool = Column(Boolean, default=False) # флаг устанавливается на True, когда приходит правильный ответ на /sms/verifyCode?code=...

    date: datetime = Column(DateTime, default=datetime.now, comment="когда клиент авторизовался")
    last_activity: datetime = Column(DateTime, default=datetime.now, comment="когда клиент авторизовался")
    host: str = Column(String(16))

class Raport(Base):
    __tablename__ = 'raports'

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    uuid: str = Column(String(36), index=True, default=lambda: str(uuid.uuid4()), comment="уникальный ключ рапорта")
    name: str = Column(String(128), nullable=False, comment="Читаемое название рапорта")
    key: str = Column(String(32), comment="Ключ к листу подбора")
    date: datetime = Column(DateTime, default=datetime.now, comment="дата создания рапорта")

    client_id: int = Column(Integer, ForeignKey("clients.id"), comment="ссылка на клиента")
    client: Mapped["Client"] = relationship(back_populates="raports")
    hidden: bool = Column(Boolean, default=False, comment="Флаг скрывает файл из выдачи")

    data: Mapped[List["RaportData"]] = relationship("RaportData")
    requests_count: int = Column(Integer, default=0, comment="колличество запросов файла")
    last_requests: datetime = Column(DateTime, default=datetime.now, comment="последнего запроса")

class RaportData(Base):
    __tablename__ = 'raports_data'

    id: int = Column(Integer, primary_key=True, autoincrement=True)

    key: str = Column(String(128))
    value: str = Column(String(256))
    subname: str = Column(String(64))
    type: Literal["str", "float", "int", "datetime"] = Column(String(32), default="str")

    raport_id: int = Column(Integer, ForeignKey("raports.id"), comment="ссылка на рапорт")