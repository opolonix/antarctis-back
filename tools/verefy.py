from typing import Optional
from fastapi import Request, Response

from sqlalchemy.orm import Session
from tools.orm import Auth
from tools.alchemy import engine
from datetime import datetime

db = engine()

async def get_client(request: Request, response: Response) -> Optional[Auth]:
    token = request.cookies.get("auth-token")
    if not token:
        return None
    client = db.query(Auth).filter(Auth.token == token).first()
    client.client.last_activity = datetime.now()
    client.last_activity = datetime.now()
    client.host = request.client.host
    db.commit()
    if not client: response.delete_cookie("auth-token")
    return client