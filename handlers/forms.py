from fastapi import APIRouter, status, Request, Response

from tools.alchemy import engine

router = APIRouter(prefix="/form")
db = engine()

@router.post("/{formName}")
async def form_handler(formName: str, request: Request, response: Response) -> int:
    return status.HTTP_200_OK