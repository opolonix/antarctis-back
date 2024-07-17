from typing import Optional
from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.responses import RedirectResponse, StreamingResponse

from sqlalchemy.orm import Session

from tools.alchemy import engine
from tools.orm import Raport, Auth

import datetime
import patterns
import PyPDF2
import io
import urllib.parse
import fitz

from tools.verefy import get_client
from tools.schemas import parse_client_schema, ClientSchema

router = APIRouter()
sess = engine()

patterns_map: dict[str, str] = {
    "economizer": "", 
    "conditioner": "Прецизионные кондиционеры", 
    "absorber": "", 
    "chiller-1": "", 
    "chiller-2": ""
}

datatypes = {
    "float": float,
    "int": int,
    "datetime": datetime.datetime,
    "date": datetime.date
}


@router.get("/hide/{key}.pdf")
async def hide_raport(key, auth: Optional[Auth] = Depends(get_client)) -> ClientSchema:
    """Скрывает файл из выдачи и личного профиля"""

    if not auth:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)

    with sess() as db:

        file = db.query(Raport).filter(Raport.uuid == key).first()

        if auth.client_id != file.client_id: # можно удалить только свои файлы
            raise HTTPException(status.HTTP_403_FORBIDDEN, detail="можно удалить только свои файлы")

        file.hidden = True
        db.commit()

        return parse_client_schema(client=auth.client)



@router.get("/{key}.pdf", response_class=StreamingResponse)
async def download_pdf(key: str) -> StreamingResponse:
    """Принимает uuid файла, и возвращает созданный файл в формате pdf"""
    with sess() as db:

        file = db.query(Raport).filter(Raport.uuid == key).first()

        if not file or file.hidden:
            return RedirectResponse("/404", status.HTTP_404_NOT_FOUND)

        file.requests_count += 1
        db.commit()

        data = {} # массив метадаты у файла

        for d in file.data:
            t = datatypes.get(d.type)
            if t: data[d.key] = t(d.value)
            else: data[d.key] = d.value

        output = io.BytesIO()


        # здесь нужно провести рассчет мощности


        header = PyPDF2.PdfReader(patterns.headers.get(patterns_map.get(file.key)))
        writer = PyPDF2.PdfWriter()

        [writer.add_page(page) for page in header.pages]

        writer.write(output)
        writer.close()
        output.seek(0)

        document = fitz.open(stream=output, filetype="pdf")

        for page in document:
            page.insert_font(fontname="EXT_0", fontfile="content/fonts/Inter-VariableFont_slnt,wght.ttf")
            areas = page.search_for("{phone}")

            for inst in areas:
                page.add_redact_annot(inst, fill=(0.949, 0.957, 0.961))
                page.apply_redactions()

                fontsize=14
                text_left = inst[0]
                text_top = inst[1] + fontsize + 1

                page.insert_text([text_left, text_top], "+7 (978) 553 88 38", color=(0, 0, 0), fontsize=fontsize, fontfile="content/fonts/Inter-VariableFont_slnt,wght.ttf")

        output = io.BytesIO()
        document.save(output)
        document.close()
        output.seek(0)

        filename = urllib.parse.quote(f'{file.name} {file.date.strftime("%d.%m.%Y")}.pdf')

        headers = {
            'Content-Disposition': f'attachment; filename*=UTF-8\'\'{filename}'
        }

        return StreamingResponse(output, media_type='application/pdf', headers=headers)