from typing import Optional
from fastapi import APIRouter, Depends, status, Request, Response, Cookie
from fastapi.exceptions import HTTPException

from tools.alchemy import engine
from tools.orm import Auth, Client
from tools.verefy import get_client

from pydantic import BaseModel

import re
import random
import string

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

@router.post("/sendCode")
async def send_sms_code(phone: str, request: Request, response: Response, client: Optional[Auth] = Depends(get_client)) -> int:

    if client:
        raise HTTPException(status.HTTP_409_CONFLICT, detail="Сначала выйдите из текущей сессии")


    phone = re.sub(r'[^\d]', '', phone)

    if len(phone) < 6 or len(phone) > 20:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Неверно введен номер телефона")
    
    if not (client := db.query(Client).filter(Client.phone == phone).first()):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)

    code = ''.join(random.choices(string.digits, k=4))

    # здесь нужно доставить код клиенту

    auth = Auth(client_id=client.id, sms_code=code)
    db.add(auth)
    db.commit()
    response.set_cookie("auth-token", auth.token)

    return status.HTTP_200_OK

@router.post("/newClient")
async def send_sms_code(data: NewClient, request: Request, response: Response, client: Optional[Auth] = Depends(get_client)) -> int:
    
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

    # здесь нужно доставить код клиенту

    auth = Auth(client_id=client.id, sms_code=code)
    db.add(auth)
    db.commit()
    response.set_cookie("auth-token", auth.token)

    return status.HTTP_200_OK

@router.get("/verifyCode")
async def verify_sms_code(code: str, request: Request, response: Response, auth: Optional[Auth] = Depends(get_client)) -> int:

    if not auth:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)

    if auth.sms_code != code:
        raise HTTPException(status.HTTP_400_BAD_REQUEST)

    auth.verefied = True
    db.commit()

    return status.HTTP_200_OK