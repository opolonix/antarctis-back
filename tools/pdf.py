import io
from PyPDF2 import PdfMerger
import fitz

def merge_pdfs(pdf_streams: list[io.BytesIO]) -> io.BytesIO:
    merger = PdfMerger()
    
    for pdf_stream in pdf_streams:
        pdf_stream.seek(0)
        merger.append(pdf_stream)
    
    output_stream = io.BytesIO()
    merger.write(output_stream)
    merger.close()
    
    return output_stream


def get_text_length(text, font_size=12, font_path="content/fonts/Inter-VariableFont_slnt,wght.ttf"):
    doc = fitz.open()
    page = doc.new_page()

    # Регистрация шрифта (используем встроенные шрифты для примера)
    page.insert_text((0, 0), text, fontsize=font_size, fontfile=font_path, fontname="Inter")

    # Извлечение размеров текста
    text_length = 0
    blocks = page.get_text("dict", sort=True)['blocks']

    for line in blocks:
        text_length = line['bbox'][2] - line['bbox'][0]
    
    doc.close()
    return text_length