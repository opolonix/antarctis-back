from fastapi import APIRouter, Cookie, Depends, status, Request, Response
from fastapi.exceptions import HTTPException

from tools.orm import Auth, Client
from tools.alchemy import engine

from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from tools.verefy import get_client

router = APIRouter(prefix="/client")
db = engine()

class Empty: ...

class RaportSchema(BaseModel):
    unique_name: str
    name: str
    date: datetime
    requests_count: int

class ClientSchema(BaseModel):
    name: str
    phone: str
    company_name: str
    join_at: datetime
    raports: List[RaportSchema]

    email: str
    facility_name: str


class EditableSchema(BaseModel):
    first_name: str | type = Empty
    last_name: str | type = Empty
    father_name: str | type | None = Empty

    company_name: str | type = Empty
    facility_name: str | type = Empty

def parse_client_schema(client: Client) -> ClientSchema:
    raports = []
    
    for r in client.raports:
        raports.append(RaportSchema(
            unique_name=r.uuid,
            name=r.name,
            date=r.date,
            requests_count=r.requests_count
        ))

    return ClientSchema(
        name = f"{client.first_name} {client.last_name}".title(),
        phone = client.phone, 
        join_at = client.join_at, 
        raports = raports, 
        company_name = client.company_name,
        email = client.email,
        facility_name = client.facility_name
    )

@router.get("")
async def get_myself(auth: Optional[Auth] = Depends(get_client)) -> ClientSchema:

    if not auth:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)

    return parse_client_schema(client=auth.client)


@router.post("/edit")
async def edit_params(new_params: EditableSchema, auth: Optional[Auth] = Depends(get_client)) -> ClientSchema:
    if not auth:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)
    
    client = auth.client
    for k, v in new_params.dict().items():
        if v is Empty: continue
        if v == '': raise HTTPException(status.HTTP_400_BAD_REQUEST)
        setattr(client, k, v)

    db.commit()

    return parse_client_schema(client=client)