from xhtml2pdf import pisa

from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

import io, random, string, os

pdfmetrics.registerFont(TTFont("Helvetica", "content/fonts/Inter-VariableFont_slnt,wght.ttf"))

def html_to_pdf(content: str) -> io.BytesIO:
    key = ''.join(random.choice(string.ascii_letters) for i in range(24))

    with open(f"content/buffer/{key}.pdf", 'wb+') as f:
        pisa.CreatePDF(content, dest=f, encoding="utf-8")

    return f"content/buffer/{key}.pdf"