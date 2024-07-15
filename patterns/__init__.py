import os
import re
import io

patterns: dict[str, dict[int, io.BytesIO]] = {} # паттерны <название кондея> -> <мощность числом> -> <файл кондея>
headers: dict[str, io.BytesIO] = {} # шаблоны заголовков <название кондея> -> <файл заголовка>

for p in os.listdir("patterns"):
    if os.path.isdir(f"patterns/{p}") and (g := re.fullmatch(r"\d\. (.*)", p, re.I)):
        patterns[g.group(1)] = {}
        for i in os.listdir(os.path.join("patterns", p)):
            if (q := re.search(r'\d+', i)):
                patterns[g.group(1)][int(q[0])] = open(os.path.join("patterns", p, i), 'rb')
            if 'шаблон' in i.lower():
                headers[g.group(1)] = open(os.path.join("patterns", p, i), 'rb')