import math
from fastapi import APIRouter, Request
from fastapi.responses import PlainTextResponse
from starlette.datastructures import FormData

router = APIRouter()

def pt(t: float) -> float:
    """Возвращает давление насыщенного пара при температуре t."""
    if t >= 0:
        return 6.1121 * math.exp((18.678 - t / 234.5) * t / (257.14 + t)) * 100
    else:
        return 6.1115 * math.exp((23.036 - t / 333.7) * t / (279.82 + t)) * 100

def tp(tp_p: float) -> float:
    """Находит температуру по давлению насыщенного пара методом бисекции."""
    tp_tmin = -100.0
    tp_tmax = 100.0
    tp_t = (tp_tmin + tp_tmax) / 2
    
    for _ in range(20):
        tp_p1 = pt(tp_t)
        tp_t1 = tp_t
        
        if tp_p1 > tp_p:
            tp_t = (tp_t + tp_tmin) / 2
            tp_tmax = tp_t1
        elif tp_p1 < tp_p:
            tp_t = (tp_t + tp_tmax) / 2
            tp_tmin = tp_t1
        else:
            return tp_t
    
    return tp_t

def tifi(i1: float, fi1: float) -> float:
    """Находит температуру по внутренней энергии и относительной влажности методом бисекции."""
    tp_tmin = -100.0
    tp_tmax = 100.0
    tp_t = (tp_tmin + tp_tmax) / 2
    
    for _ in range(20):
        fi11 = pd(dit(i1, tp_t)) / pt(tp_t) * 100
        tp_t1 = tp_t
        
        if fi11 < fi1:
            tp_t = (tp_t + tp_tmin) / 2
            tp_tmax = tp_t1
        elif fi11 > fi1:
            tp_t = (tp_t + tp_tmax) / 2
            tp_tmin = tp_t1
        else:
            return tp_t
    
    return tp_t

def tdfi(d1: float, fi1: float) -> float:
    """Находит температуру по давлению насыщенного пара и относительной влажности методом бисекции."""
    tp_tmin = -100.0
    tp_tmax = 100.0
    tp_t = (tp_tmin + tp_tmax) / 2
    
    for _ in range(20):
        fi11 = pd(d1) / pt(tp_t) * 100
        tp_t1 = tp_t
        
        if fi11 < fi1:
            tp_t = (tp_t + tp_tmin) / 2
            tp_tmax = tp_t1
        elif fi11 > fi1:
            tp_t = (tp_t + tp_tmax) / 2
            tp_tmin = tp_t1
        else:
            return tp_t
    
    return tp_t

def dp(p: float) -> float:
    """Возвращает абсолютную влажность по давлению пара."""
    return 622 * p / (101325 - p)

def pd(d: float) -> float:
    """Возвращает давление пара по абсолютной влажности."""
    return d * 101325 / (622 + d)

def idt(d: float, t: float) -> float:
    """Возвращает внутреннюю энергию по абсолютной влажности и температуре."""
    return (1.01 + 0.00197 * d) * t + 2.493 * d

def tid(i: float, d: float) -> float:
    """Возвращает температуру по внутренней энергии и абсолютной влажности."""
    return (i - 2.493 * d) / (1.01 + 0.00197 * d)

def dit(i: float, t: float) -> float:
    """Возвращает абсолютную влажность по внутренней энергии и температуре."""
    return (i - 1.01 * t) / (0.00197 * t + 2.493)

def fidt(d: float, t: float) -> float:
    """Возвращает относительную влажность по абсолютной влажности и температуре."""
    return d * 101325 / (622 + d) / pt(t) * 100

def round1(n: float, m: int) -> str:
    return f"{n:.{max(0, m - int(math.log10(n)))}f}".replace(',', ' ')

async def handle_ajax_1(data: dict) -> str:
    par = [str(data['ide1']), str(data['ide2'])]
    val = [float(data['idi1']), float(data['idi2'])]
    globals()[par[0]] = val[0]
    globals()[par[1]] = val[1]
    print(par)

    if (t1 := globals().get('t1')) is not None and (fi1 := globals().get('fi1')) is not None:
        p1 = pt(t1) * fi1 / 100
        d1 = dp(p1)
        i1 = idt(d1, t1)
        tr1 = tp(p1)
    elif (t1 := globals().get('t1')) is not None and (d1 := globals().get('d1')) is not None:
        i1 = idt(d1, t1)
        p1 = pd(d1)
        fi1 = fidt(d1, t1)
        tr1 = tp(p1)
    elif (t1 := globals().get('t1')) is not None and (i1 := globals().get('i1')) is not None:
        d1 = dit(i1, t1)
        p1 = pd(d1)
        fi1 = fidt(d1, t1)
        tr1 = tp(p1)
    elif (t1 := globals().get('t1')) is not None and (p1 := globals().get('p1')) is not None:
        p1 = p1 * 1000
        d1 = dp(p1)
        i1 = idt(d1, t1)
        fi1 = fidt(d1, t1)
        tr1 = tp(p1)
    elif (t1 := globals().get('t1')) is not None and (tr1 := globals().get('tr1')) is not None:
        p1 = pt(tr1)
        d1 = dp(p1)
        i1 = idt(d1, t1)
        fi1 = fidt(d1, t1)
    elif (fi1 := globals().get('fi1')) is not None and (d1 := globals().get('d1')) is not None:
        p1 = pd(d1)
        tr1 = tp(p1)
        t1 = tp(p1 * 100 / fi1)
        i1 = idt(d1, t1)
    elif (fi1 := globals().get('fi1')) is not None and (i1 := globals().get('i1')) is not None:
        t1 = tifi(i1, fi1)
        d1 = dit(i1, t1)
        p1 = pd(d1)
        tr1 = tp(p1)
    elif (fi1 := globals().get('fi1')) is not None and (p1 := globals().get('p1')) is not None:
        p1 = p1 * 1000
        d1 = dp(p1)
        tr1 = tp(p1)
        t1 = tp(p1 * 100 / fi1)
        i1 = idt(d1, t1)
    elif (fi1 := globals().get('fi1')) is not None and (tr1 := globals().get('tr1')) is not None:
        p1 = pt(tr1)
        d1 = dp(p1)
        t1 = tp(p1 * 100 / fi1)
        i1 = idt(d1, t1)
    elif (d1 := globals().get('d1')) is not None and (i1 := globals().get('i1')) is not None:
        t1 = tid(i1, d1)
        p1 = pd(d1)
        fi1 = fidt(d1, t1)
        tr1 = tp(p1)
    elif (i1 := globals().get('i1')) is not None and (p1 := globals().get('p1')) is not None:
        p1 = p1 * 1000
        d1 = dp(p1)
        t1 = tid(i1, d1)
        fi1 = fidt(d1, t1)
        tr1 = tp(p1)
    elif (i1 := globals().get('i1')) is not None and (tr1 := globals().get('tr1')) is not None:
        p1 = pt(tr1)
        d1 = dp(p1)
        t1 = tid(i1, d1)
        fi1 = fidt(d1, t1)
    
    return f"{round(t1,2)}|{round(fi1,2)}|{round(d1,2)}|{round(i1,2)}|{round(p1/1000,2)}|{round(tr1,2)}"
    
async def handle_ajax_2(data: dict) -> str:
    t1 = float(data['t1'])
    d1 = float(data['d1'])
    i1 = float(data['i1'])
    fi1 = fidt(d1, t1)
    G1 = float(data['G1'])
    globals()[data['ide2']] = float(data['idi2'])
    type_ = int(data['type'])
    if data['proc'] == 'humi':
        if type_ == 1:
            i2 = i1
            error = ""
            if (t2 := globals().get('t2')) is not None:
                d2 = dit(i2, t2)
                p2 = pd(d2)
                tr2 = tp(p2)
                fi2 = fidt(d2, t2)
                N2 = abs((i2 - i1) * 1.2 * G1 / 3600)
                W2 = abs((d2 - d1) * 1.2 * G1 / 1000)
            elif (fi2 := globals().get('fi2')) is not None:
                t2 = tifi(i2, fi2)
                d2 = dit(i2, t2)
                p2 = pd(d2)
                tr2 = tp(p2)
                N2 = abs((i2 - i1) * 1.2 * G1 / 3600)
                W2 = abs((d2 - d1) * 1.2 * G1 / 1000)
            elif (d2 := globals().get('d2')) is not None:
                t2 = tid(i2, d2)
                fi2 = fidt(d2, t2)
                p2 = pd(d2)
                tr2 = tp(p2)
                N2 = abs((i2 - i1) * 1.2 * G1 / 3600)
                W2 = abs((d2 - d1) * 1.2 * G1 / 1000)
            elif (p2 := globals().get('p2')) is not None:
                p2 = p2 * 1000
                d2 = dp(p2)
                t2 = tid(i2, d2)
                fi2 = fidt(d2, t2)
                tr2 = tp(p2)
                N2 = abs((i2 - i1) * 1.2 * G1 / 3600)
                W2 = abs((d2 - d1) * 1.2 * G1 / 1000)
            elif (tr2 := globals().get('tr2')) is not None:
                p2 = pt(tr2)
                d2 = dp(p2)
                t2 = tid(i2, d2)
                fi2 = fidt(d2, t2)
                N2 = abs((i2 - i1) * 1.2 * G1 / 3600)
                W2 = abs((d2 - d1) * 1.2 * G1 / 1000)
            elif (W2 := globals().get('W2')) is not None:
                d2 = d1 + W2 * 1000 / 1.2 / G1
                t2 = tid(i2, d2)
                p2 = pd(d2)
                tr2 = tp(p2)
                fi2 = fidt(d2, t2)
                N2 = abs((i2 - i1) * 1.2 * G1 / 3600)
            
            if fi2 > 100 or fi2 < fi1:
                if fi2 > 100:
                    fi2 = 100
                    error = "Достигнут предел увлажнения"
                if fi2 < fi1:
                    fi2 = fi1
                    error = "Невозможно увлажнить: влажность должна быть выше начальной"
                t2 = tifi(i2, fi2)
                d2 = dit(i2, t2)
                p2 = pd(d2)
                tr2 = tp(p2)
                N2 = abs((i2 - i1) * 1.2 * G1 / 3600)
                W2 = abs((d2 - d1) * 1.2 * G1 / 1000)
            
            return f"{round(t2,2)}|{round(fi2,2)}|{round(d2,2)}|{round(i2,2)}|{round(p2/1000,2)}|{round(tr2,2)}|{round(N2,2)}|{round(W2,2)}|{error}"

        else:
            t2 = t1
            if (fi2 := globals().get('fi2')) is not None:
                p2 = pt(t2) * fi2 / 100
                d2 = dp(p2)
                i2 = idt(d2, t2)
                tr2 = tp(p2)
                N2 = abs((i2 - i1) * 1.2 * G1 / 3600)
                W2 = abs((d2 - d1) * 1.2 * G1 / 1000)
            elif (d2 := globals().get('d2')) is not None:
                i2 = idt(d2, t2)
                p2 = pd(d2)
                fi2 = fidt(d2, t2)
                tr2 = tp(p2)
                N2 = abs((i2 - i1) * 1.2 * G1 / 3600)
                W2 = abs((d2 - d1) * 1.2 * G1 / 1000)
            elif (i2 := globals().get('i2')) is not None:
                d2 = dit(i2, t2)
                p2 = pd(d2)
                fi2 = fidt(d2, t2)
                tr2 = tp(p2)
                N2 = abs((i2 - i1) * 1.2 * G1 / 3600)
                W2 = abs((d2 - d1) * 1.2 * G1 / 1000)
            elif (p2 := globals().get('p2')) is not None:
                p2 = p2 * 1000
                d2 = dp(p2)
                i2 = idt(d2, t2)
                fi2 = fidt(d2, t2)
                tr2 = tp(p2)
                N2 = abs((i2 - i1) * 1.2 * G1 / 3600)
                W2 = abs((d2 - d1) * 1.2 * G1 / 1000)
            elif (tr2 := globals().get('tr2')) is not None:
                p2 = pt(tr2)
                d2 = dp(p2)
                i2 = idt(d2, t2)
                fi2 = fidt(d2, t2)
                N2 = abs((i2 - i1) * 1.2 * G1 / 3600)
                W2 = abs((d2 - d1) * 1.2 * G1 / 1000)
            elif (N2 := globals().get('N2')) is not None:
                i2 = i1 + N2 * 3600 / 1.2 / G1
                d2 = dit(i2, t2)
                fi2 = fidt(d2, t2)
                p2 = pd(d2)
                tr2 = tp(p2)
                W2 = abs((d2 - d1) * 1.2 * G1 / 1000)
            elif (W2 := globals().get('W2')) is not None:
                d2 = d1 + W2 * 1000 / 1.2 / G1
                i2 = idt(d2, t2)
                fi2 = fidt(d2, t2)
                p2 = pd(d2)
                tr2 = tp(p2)
                N2 = abs((i2 - i1) * 1.2 * G1 / 3600)

            if fi2 > 100 or fi2 < fi1:
                if fi2 > 100:
                    fi2 = 100
                    error = "Достигнут предел увлажнения"
                if fi2 < fi1:
                    fi2 = fi1
                    error = "Невозможно увлажнить: влажность должна быть выше начальной"
                p2 = pt(t2) * fi2 / 100
                d2 = dp(p2)
                i2 = idt(d2, t2)
                tr2 = tp(p2)
                N2 = abs((i2 - i1) * 1.2 * G1 / 3600)
                W2 = abs((d2 - d1) * 1.2 * G1 / 1000)


@router.post("/calculate", response_class=PlainTextResponse)
async def calculate(request: Request):
    form_data = await request.form()
    if form_data.get("ajax") == "1":
        return await handle_ajax_1(form_data._dict)
    elif form_data.get("ajax") == "2":
        return await handle_ajax_2(form_data._dict)