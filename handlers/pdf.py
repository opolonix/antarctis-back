from typing import Optional
from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.responses import RedirectResponse, StreamingResponse

from sqlalchemy.orm import Session

from tools.alchemy import engine
from tools.orm import Raport, Auth
from tools.pdf import merge_pdfs, get_text_length

import datetime
import patterns
import PyPDF2
import io
import urllib.parse
import pymupdf as fitz
import phonenumbers

from tools.verefy import get_client
from tools.schemas import parse_client_schema, ClientSchema

import io
from PyPDF2 import PdfMerger, PdfReader, PdfWriter
import pdfplumber
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

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
        
        if not file.key:

            file.hidden = True
            db.commit()

            return RedirectResponse("/404", status.HTTP_404_NOT_FOUND)

        file.requests_count += 1
        db.commit()

        data = {} # массив метадаты у файла

        for d in file.data:
            t = datatypes.get(d.type)
            if t: data[d.key] = t(d.value)
            else: data[d.key] = d.value

        # тут нужно рассчитать мощность
        power = 20

        powers = [f for p, f in sorted(patterns.patterns[patterns_map[file.key]].items()) if power <= p][:2]
        powers_n = [p for p in sorted(patterns.patterns[patterns_map[file.key]].keys()) if power <= p][:2]
        header = patterns.headers[patterns_map[file.key]]

        c = file.client

        data = {
            "Организация:": c.company_name,
            "Адрес:": c.adress,
            "Контактное лицо:": f"{c.first_name} {c.last_name}".title(),
            "Телефон:": phonenumbers.format_number(phonenumbers.parse('+' + c.phone, None), phonenumbers.PhoneNumberFormat.INTERNATIONAL),
            "Е-почта:": c.email,
            "Теплоприток от оборудования:": "1",
            "Теплоприток от отопления:": f"2",
            "Теплоприток от вентиляции:": f"1",
            "Наличие увлажнителя:": "да",
            "Направление подачи воздуха:": "вверх",
            "Тип модели кондиционера:": "...",
            "Зимний комплект:": "нет",
            "Протокол сетевого взаимодействия:": "glo",
            "Минимальный:": f"{powers_n[0]} квт.",
            "Оптимальный:": f"{powers_n[1]} квт.",
            "С профицитом:": f"{powers_n[1]} квт."
        }

        header.seek(0)
        doc = fitz.open(stream=io.BytesIO(header.read()), filetype="pdf")
        p = fitz.Point(50, 72)
        page = doc[0]
        page.insert_font('Inter', "content/fonts/Inter-VariableFont_slnt,wght.ttf")

        with pdfplumber.open(header) as pdf:
            for page_num, p in enumerate(pdf.pages):
                words = p.extract_words()
                lines: dict[float, list[dict]] = {}
                for word in words:
                    if not lines.get(word['top']): l = lines[word["top"]] = [word]
                    else: lines[word["top"]].append(word)
            width = page.get_text("dict")['width']

            for line in lines.values():
                key = ' '.join([v['text'] for v in line])
                l = line[-1]
                if text := data.get(key):

                    size = get_text_length(text)
                    if (lines_count := ((l['x1'] + 3 + size) / width)) > 0.9:
                        text = text.split()
                        text.append("") # это нужно потому что while проглатывает последний элемент

                        free = width - l['x1'] - 3 - l['x0']
                        line = []
                        position = fitz.Point(l['x1'] + 2, l["top"] + (l['height'] / 2) + 1.5)

                        while len(text) != 0:
                            if free < get_text_length(' '.join(line + [text[0]])) or len(text) == 1:

                                page.insert_text(position, ' '.join(line), fontname = "Inter", fontsize = 12, color = (0.561, 0.545, 0.541))

                                line = []

                                free = width - l['x0']*2 # изменяем стартовый размер доступной области
                                position.x = l['x0'] # смещаем поле как можно левее
                                position.y += 12*1.2 # добавляем 12*1,2 для перехода на новую строку

                                if len(text) == 1: break
                            else:
                                line.append(text[0])
                                text.pop(0)
    
                    else:
                        page.insert_text(fitz.Point(l['x1'] + 3, l["top"] + (l['height'] / 2) + 1.5), text, fontname = "Inter", fontsize = 12, color = (0.561, 0.545, 0.541))

                elif key == "Лист подбора прецизионного кондиционера АУРА №А-":
                    page.insert_text(
                        fitz.Point(l['x1'] - 2, l["top"] + (l['height'] / 2)) + 1.5, f"{file.id}", 
                        fontname = "Inter", 
                        fontsize = 14, 
                        color = (0.372, 0.345, 0.345), 
                        render_mode=0
                    )

        
        header = io.BytesIO()
        doc.save(header)
        doc.close()

        header.seek(0)

        output = merge_pdfs([header] + powers)
        output.seek(0)

        filename = urllib.parse.quote(f'{file.name} {file.date.strftime("%d.%m.%Y")}.pdf')

        headers = {
            'Content-Disposition': f'attachment; filename*=UTF-8\'\'{filename}'
        }

        return StreamingResponse(output, media_type='application/pdf', headers=headers)