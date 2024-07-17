from typing import Dict, Literal, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response

from pydantic import BaseModel

from tools.alchemy import engine
from tools.orm import Auth, Raport, RaportData
from tools.verefy import get_client

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
    if not auth:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)

    # рассчет по формулам происходит при выдаче файла!!!

    raport = Raport(name=n if (n := patterns_map.get(name)) else "Лист подбора", key=name, client_id=auth.client_id)
    db.add(raport)
    db.commit()

    fields = [RaportData(value=str(v), key=k, type=type(v).__name__) for k, v in fields.items()]
    raport.data = fields
    db.commit()

    return status.HTTP_200_OK