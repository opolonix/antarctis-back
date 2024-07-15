from fastapi import APIRouter, status, Response
from fastapi.responses import RedirectResponse, StreamingResponse

from tools.alchemy import engine
from tools.orm import Raport

import datetime
import patterns
import PyPDF2
import io
import urllib.parse
import fitz

router = APIRouter()
db = engine()

@router.get("/{key}.pdf", response_class=StreamingResponse)
async def download_pdf(key, response: Response) -> StreamingResponse:

    file = db.query(Raport).filter(Raport.uuid == key).first()

    if not file:
        return RedirectResponse("/404", status.HTTP_404_NOT_FOUND)

    file.requests_count += 1
    db.commit()

    data = {} # массив метадаты у файла
    datatypes = {
        "float": float,
        "int": int,
        "datetime": datetime.datetime,
        "date": datetime.date
    }

    for d in file.data:
        t = datatypes.get(d.type)
        if t: data[d.key] = t(d.value)
        else: data[d.key] = d.value

    output = io.BytesIO()

    reader1 = PyPDF2.PdfReader(patterns.aura["шаблон"])
    reader2 = PyPDF2.PdfReader(patterns.aura["16"])

    writer = PyPDF2.PdfWriter()

    [writer.add_page(page) for page in reader1.pages]
    [writer.add_page(page) for page in reader2.pages]

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