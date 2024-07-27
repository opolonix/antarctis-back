from fastapi import APIRouter
from fastapi.responses import HTMLResponse, FileResponse

router = APIRouter()

@router.get("/404", response_class=HTMLResponse)
async def error404() -> FileResponse:
    return FileResponse("html/404.html")