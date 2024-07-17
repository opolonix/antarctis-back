from typing import Literal, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response

from tools.alchemy import engine
from tools.orm import Auth, Raport, RaportData
from tools.verefy import get_client
from tools import bot

from config import DOMAIN


router = APIRouter(prefix="/form")
db = engine()

patterns_map: dict[str, str] = {
    "economizer": "", 
    "conditioner": "Прецизионные кондиционеры", 
    "absorber": "", 
    "chiller-1": "", 
    "chiller-2": ""
}

@router.post("/{name}")
async def form_handler(name: Literal["economizer", "conditioner", "absorber", "chiller-1", "chiller-2"], fields: dict[str, str | int], auth: Optional[Auth] = Depends(get_client)) -> int:
    """Ручка для обработки формы

    Принимает параметры 
    :name - имя формы (economizer, conditioner, absorber, chiller-1, chiller-2)
    :fields - словарь ключ: значение, где ключ - название поля, значение - значение этого поля"""
    if not auth:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)

    # рассчет по формулам происходит при выдаче файла!!!

    raport = Raport(name=n if (n := patterns_map.get(name)) else "Лист подбора", key=name, client_id=auth.client_id)
    db.add(raport)
    db.commit()

    fields = [RaportData(value=str(v), key=k, type=type(v).__name__) for k, v in fields.items()]
    raport.data = fields
    db.commit()

    bot.send_message(-1002149223611, text="Создан новый отчет", button_text="Скачать файл", button_url=f"{DOMAIN}/{raport.uuid}.pdf")

    return status.HTTP_200_OK