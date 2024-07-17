from fastapi import APIRouter, Depends, status, Response
from fastapi.exceptions import HTTPException

from tools.orm import Auth
from tools.alchemy import engine

from typing import List, Optional

from tools.verefy import get_client
from tools.schemas import ClientSchema, parse_client_schema, EditableSchema, Empty

router = APIRouter(prefix="/client")
sess = engine()


@router.get("")
async def get_myself(auth: Optional[Auth] = Depends(get_client)) -> ClientSchema:
    """Возвращает полную информацию о клиенте, или ошибку 401, если клиент не авторизован"""

    if not auth:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)

    return parse_client_schema(client=auth.client)

@router.get("/logout")
async def logout(response: Response) -> int:
    """Производит логаут для клиента"""

    response.delete_cookie("auth-token")

    return status.HTTP_200_OK


@router.post("/edit")
async def edit_params(new_params: EditableSchema, auth: Optional[Auth] = Depends(get_client)) -> ClientSchema:
    """Ручка для изменения полей пользователя
    Вернет 401 если пользователь не авторизован
    Вернет 400 если значение поля, которое вы пытаетесь изменить  будет равно пустой строке

    При успешной отработке вернет новую схему клиента
    """
    with sess() as db:
        if not auth:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED)
        
        client = auth.client
        for k, v in new_params.dict().items():
            if v is Empty: continue
            if v == '': raise HTTPException(status.HTTP_400_BAD_REQUEST)
            setattr(client, k, v)

        db.commit()

        return parse_client_schema(client=client)