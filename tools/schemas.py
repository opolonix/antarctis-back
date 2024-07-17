from typing import List
from pydantic import BaseModel
from datetime import datetime

from tools.orm import Client

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
        if r.hidden: continue
        
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