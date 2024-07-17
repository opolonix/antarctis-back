from typing import Optional
from fastapi import APIRouter, Depends, status, Request, Response, Cookie
from fastapi.exceptions import HTTPException

from tools.alchemy import engine
from tools.orm import Auth, Client
from tools.verefy import get_client

from pydantic import BaseModel
from datetime import datetime, timedelta

import re
import random
import string
import requests

from config import SMS

router = APIRouter(prefix="/sms")
db = engine()

class NewClient(BaseModel):
    first_name: str
    last_name: str
    father_name: str | None

    phone: str
    company_name: str
    email: str
    facility_name: str

class SMSCall(BaseModel):
    phone: str
    message: str
    date: datetime = datetime.now()

class SMSCalls:
    def __init__(self, limit_peer_hour: int = 60) -> None:
        self.calls: list[SMSCall] = []
        self.limit = limit_peer_hour

    def send_sms(self, phone: str, message: str):
        this = datetime.now() + timedelta(hours=1)
        limit = 0
        for call in self.calls:
            if call.date < this: 
                limit += 1
            else: 
                break
            if limit == self.limit: # выкидывает исключение если лимит запросов за час превышен
                raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, detail="Линия запросов перегружена")
        self.calls.append(SMSCall(phone=phone, message=message))
        answer = requests.get(f"https://smsc.ru/sys/send.php?login={SMS.login}&psw={SMS.psw}&phones={phone}&mes={message}")
        return answer

sms = SMSCalls()

@router.post("/sendCode")
async def send_sms_code(phone: str, request: Request, response: Response, client: Optional[Auth] = Depends(get_client)) -> int:
    """Ручка посылает смс код с учетом, если клиент на таком номере уже зарегистрирован
    
    Вернет 409 если вы уже авторизованы в системе, следовательно нужно пингануть ручку /client/logout
    Вернет 400 если номер телефона не соответствует базовым параметрам длины
    Вернет 401 если номер телефона не записан в базе (следовательно нужно перекинуть клиента на /login или обратиться к ручке /newClient)

    В успешном результате вернет только код 200
    """

    if client:
        raise HTTPException(status.HTTP_409_CONFLICT, detail="Сначала выйдите из текущей сессии")


    phone = re.sub(r'[^\d]', '', phone)

    if len(phone) < 6 or len(phone) > 20:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Неверно введен номер телефона")
    
    if not (client := db.query(Client).filter(Client.phone == phone).first()):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)

    code = ''.join(random.choices(string.digits, k=4))

    answer = sms.send_sms(phone, message=f"Ваш код авторизации для сервиса antarctis.ru {code}")

    auth = Auth(client_id=client.id, sms_code=code)
    db.add(auth)
    db.commit()
    response.set_cookie("auth-token", auth.token)

    return status.HTTP_200_OK

@router.post("/newClient")
async def send_sms_code(data: NewClient, request: Request, response: Response, client: Optional[Auth] = Depends(get_client)) -> int:
    
    """Ручка для создания нового клиента
    
    Вернет 409 если вы уже авторизованы в системе, следовательно нужно пингануть ручку /client/logout
    Вернет 400 если номер телефона не соответствует базовым параметрам длины
    Вернет 400 если не заполнены обязательные поля (все кроме отчества)
    Вернет 400 если имейл уже привязан к другому аккаунту
    
    Если номер уже зарегистрирован, отправит код без изменения данных клиента

    В успешном результате вернет только код 200
    """
    
    if client:
        raise HTTPException(status.HTTP_409_CONFLICT, detail="Сначала выйдите из текущей сессии")
    
    data.phone = re.sub(r'[^\d]', '', data.phone)


    if len(data.phone) < 6 or len(data.phone) > 20:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Неверно введен номер телефона")
    if not (data.first_name and data.facility_name and data.email and data.last_name):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Заполните обязательные поля")

    if not (client := db.query(Client).filter(Client.phone == data.phone).first()): # проверка наличия клиента в базе

        by_email = db.query(Client).filter(Client.email == data.email).first()
        if by_email:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Этот имейл уже привязан к аккаунту")
        client = Client(**data.dict())
        db.add(client)
        db.commit()

    code = ''.join(random.choices(string.digits, k=4))

    answer = sms.send_sms(data.phone, message=f"Ваш код авторизации для сервиса antarctis.ru {code}")

    auth = Auth(client_id=client.id, sms_code=code)
    db.add(auth)
    db.commit()
    response.set_cookie("auth-token", auth.token)

    return status.HTTP_200_OK

@router.get("/verifyCode")
async def verify_sms_code(code: str, auth: Optional[Auth] = Depends(get_client)) -> int:
    """Принимает code строкой, но состоит полностью из цифр
    
    вернет 400 если код не подошел
    вернет 401 если сессия не была создана, тогда нужно обратиться на ручку /newClient или /sendCode
    """
    if not auth:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)

    if auth.sms_code != code:
        raise HTTPException(status.HTTP_400_BAD_REQUEST)

    auth.verefied = True
    db.commit()

    return status.HTTP_200_OK