from fastapi import APIRouter
from fastapi.responses import HTMLResponse, FileResponse

router = APIRouter()

@router.get("/404", response_class=HTMLResponse)
async def error404() -> FileResponse:
    return FileResponse("html/404.html")

@router.get("/", response_class=HTMLResponse, include_in_schema=False)
async def index() -> FileResponse:
    return FileResponse("html/index.html")