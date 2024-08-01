from fastapi import APIRouter
from pydantic import BaseModel
import math

router = APIRouter()

def pt(t):
    if t >= 0:
        return 6.1121 * math.exp((18.678 - t / 234.5) * t / (257.14 + t)) * 100
    else:
        return 6.1115 * math.exp((23.036 - t / 333.7) * t / (279.82 + t)) * 100

def tp(tp_p):
    tp_tmin = -100
    tp_tmax = 100
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

def tifi(i1, fi1):
    tp_tmin = -100
    tp_tmax = 100
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

def tdfi(d1, fi1):
    tp_tmin = -100
    tp_tmax = 100
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

def dp(p):
    return 622 * p / (101325 - p)

def pd(d):
    return d * 101325 / (622 + d)

def idt(d, t):
    return (1.01 + 0.00197 * d) * t + 2.493 * d

def tid(i, d):
    return (i - 2.493 * d) / (1.01 + 0.00197 * d)

def dit(i, t):
    return (i - 1.01 * t) / (0.00197 * t + 2.493)

def fidt(d, t):
    return d * 101325 / (622 + d) / pt(t) * 100

class CalculationRequest(BaseModel):
    ide1: str | None = None
    ide2: str | None = None
    idi1: float | None = None
    idi2: float | None = None
    ajax: int | None = None
    t1: float | None = None
    fi1: float | None = None
    d1: float | None = None
    i1: float | None = None
    p1: float | None = None
    tr1: float | None = None
    G1: float | None = None
    type: int | None = None
    proc: str | None = None
    t2: float | None = None
    fi2: float | None = None
    d2: float | None = None
    i2: float | None = None
    p2: float | None = None
    tr2: float | None = None
    N2: float | None = None
    W2: float | None = None

    
def handle_ajax_1(vars: dict, request):
    t1 = vars.get('t1')
    fi1 = vars.get('fi1')
    d1 = vars.get('d1')
    i1 = vars.get('i1')
    p1 = vars.get('p1')
    tr1 = vars.get('tr1')

    if t1 is not None and fi1 is not None:
        p1 = pt(t1) * fi1 / 100
        d1 = dp(p1)
        i1 = idt(d1, t1)
        tr1 = tp(p1)
    elif t1 is not None and d1 is not None:
        i1 = idt(d1, t1)
        p1 = pd(d1)
        fi1 = fidt(d1, t1)
        tr1 = tp(p1)
    elif t1 is not None and i1 is not None:
        d1 = dit(i1, t1)
        p1 = pd(d1)
        fi1 = fidt(d1, t1)
        tr1 = tp(p1)
    elif t1 is not None and p1 is not None:
        p1 = p1 * 1000
        d1 = dp(p1)
        i1 = idt(d1, t1)
        fi1 = fidt(d1, t1)
        tr1 = tp(p1)
    elif t1 is not None and tr1 is not None:
        p1 = pt(tr1)
        d1 = dp(p1)
        i1 = idt(d1, t1)
        fi1 = fidt(d1, t1)
    elif fi1 is not None and d1 is not None:
        p1 = pd(d1)
        tr1 = tp(p1)
        t1 = tp(p1 * 100 / fi1)
        i1 = idt(d1, t1)
    elif fi1 is not None and i1 is not None:
        t1 = tifi(i1, fi1)
        d1 = dit(i1, t1)
        p1 = pd(d1)
        tr1 = tp(p1)
    elif fi1 is not None and p1 is not None:
        p1 = p1 * 1000
        d1 = dp(p1)
        tr1 = tp(p1)
        t1 = tp(p1 * 100 / fi1)
        i1 = idt(d1, t1)
    elif fi1 is not None and tr1 is not None:
        p1 = pt(tr1)
        d1 = dp(p1)
        t1 = tp(p1 * 100 / fi1)
        i1 = idt(d1, t1)
    elif d1 is not None and i1 is not None:
        t1 = tid(i1, d1)
        p1 = pd(d1)
        fi1 = fidt(d1, t1)
        tr1 = tp(p1)
    elif i1 is not None and p1 is not None:
        p1 = p1 * 1000
        d1 = dp(p1)
        t1 = tid(i1, d1)
        fi1 = fidt(d1, t1)
        tr1 = tp(p1)
    elif i1 is not None and tr1 is not None:
        p1 = pt(tr1)
        d1 = dp(p1)
        t1 = tid(i1, d1)
        fi1 = fidt(d1, t1)

    return f"{round(t1,2)}|{round(fi1,2)}|{round(d1,2)}|{round(i1,2)}|{round(p1/1000,2)}|{round(tr1,2)}"

    return {
        "t1": round(t1, 2),
        "fi1": round(fi1, 2),
        "d1": round(d1, 2),
        "i1": round(i1, 2),
        "p1": round(p1 / 1000, 2),
        "tr1": round(tr1, 2)
    }

def handle_ajax_2(vars: dict, request: CalculationRequest):
    t1 = request.t1
    d1 = request.d1
    i1 = request.i1
    fi1 = fidt(d1, t1)
    G1 = request.G1
    ide2 = request.ide2
    idi2 = request.idi2
    vars[ide2] = idi2
    type = request.type
    proc = request.proc
    error = ""

    if proc == 'humi':
        if type == 1:
            i2 = i1
            t2, fi2, d2, p2, tr2, N2, W2 = None, None, None, None, None, None, None

            if request.t2 is not None:
                t2 = request.t2
                d2 = dit(i2, t2)
                p2 = pd(d2)
                tr2 = tp(p2)
                fi2 = fidt(d2, t2)
                N2 = abs((i2 - i1) * 1.2 * G1 / 3600)
                W2 = abs((d2 - d1) * 1.2 * G1 / 1000)
            elif request.fi2 is not None:
                fi2 = request.fi2
                t2 = tifi(i2, fi2)
                d2 = dit(i2, t2)
                p2 = pd(d2)
                tr2 = tp(p2)
                N2 = abs((i2 - i1) * 1.2 * G1 / 3600)
                W2 = abs((d2 - d1) * 1.2 * G1 / 1000)
            elif request.d2 is not None:
                d2 = request.d2
                t2 = tid(i2, d2)
                fi2 = fidt(d2, t2)
                p2 = pd(d2)
                tr2 = tp(p2)
                N2 = abs((i2 - i1) * 1.2 * G1 / 3600)
                W2 = abs((d2 - d1) * 1.2 * G1 / 1000)
            elif request.p2 is not None:
                p2 = request.p2 * 1000
                d2 = dp(p2)
                t2 = tid(i2, d2)
                fi2 = fidt(d2, t2)
                tr2 = tp(p2)
                N2 = abs((i2 - i1) * 1.2 * G1 / 3600)
                W2 = abs((d2 - d1) * 1.2 * G1 / 1000)
            elif request.tr2 is not None:
                tr2 = request.tr2
                p2 = pt(tr2)
                d2 = dp(p2)
                t2 = tid(i2, d2)
                fi2 = fidt(d2, t2)
                N2 = abs((i2 - i1) * 1.2 * G1 / 3600)
                W2 = abs((d2 - d1) * 1.2 * G1 / 1000)
            elif request.W2 is not None:
                W2 = request.W2
                d2 = d1 + W2 * 1000 / 1.2 / G1
                t2 = tid(i2, d2)
                p2 = pd(d2)
                tr2 = tp(p2)
                fi2 = fidt(d2, t2)
                N2 = abs((i2 - i1) * 1.2 * G1 / 3600)

            if (fi2 > 100) or (fi2 < fi1):
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
        else:
            t2 = t1
            fi2, d2, i2, p2, tr2, N2, W2 = None, None, None, None, None, None, None

            if request.fi2 is not None:
                fi2 = request.fi2
                p2 = pt(t2) * fi2 / 100
                d2 = dp(p2)
                i2 = idt(d2, t2)
                tr2 = tp(p2)
                N2 = abs((i2 - i1) * 1.2 * G1 / 3600)
                W2 = abs((d2 - d1) * 1.2 * G1 / 1000)
            elif request.d2 is not None:
                d2 = request.d2
                i2 = idt(d2, t2)
                p2 = pd(d2)
                fi2 = fidt(d2, t2)
                tr2 = tp(p2)
                N2 = abs((i2 - i1) * 1.2 * G1 / 3600)
                W2 = abs((d2 - d1) * 1.2 * G1 / 1000)
            elif request.i2 is not None:
                i2 = request.i2
                d2 = dit(i2, t2)
                p2 = pd(d2)
                fi2 = fidt(d2, t2)
                tr2 = tp(p2)
                N2 = abs((i2 - i1) * 1.2 * G1 / 3600)
                W2 = abs((d2 - d1) * 1.2 * G1 / 1000)
            elif request.p2 is not None:
                p2 = request.p2 * 1000
                d2 = dp(p2)
                i2 = idt(d2, t2)
                fi2 = fidt(d2, t2)
                tr2 = tp(p2)
                N2 = abs((i2 - i1) * 1.2 * G1 / 3600)
                W2 = abs((d2 - d1) * 1.2 * G1 / 1000)
            elif request.tr2 is not None:
                tr2 = request.tr2
                p2 = pt(tr2)
                d2 = dp(p2)
                i2 = idt(d2, t2)
                fi2 = fidt(d2, t2)
                N2 = abs((i2 - i1) * 1.2 * G1 / 3600)
                W2 = abs((d2 - d1) * 1.2 * G1 / 1000)
            elif request.N2 is not None:
                N2 = request.N2
                i2 = i1 + N2 * 3600 / 1.2 / G1
                d2 = dit(i2, t2)
                fi2 = fidt(d2, t2)
                p2 = pd(d2)
                tr2 = tp(p2)
                W2 = abs((d2 - d1) * 1.2 * G1 / 1000)
            elif request.W2 is not None:
                W2 = request.W2
                d2 = d1 + W2 * 1000 / 1.2 / G1
                i2 = idt(d2, t2)
                fi2 = fidt(d2, t2)
                p2 = pd(d2)
                tr2 = tp(p2)
                N2 = abs((i2 - i1) * 1.2 * G1 / 3600)

            if (fi2 > 100) or (fi2 < fi1):
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

        return f"{round(t2,2)}|{round(fi2,2)}|{round(d2,2)}|{round(i2,2)}|{round(p2/1000,2)}|{round(tr2,2)}|{round(N2,2)}|{round(W2,2)}|{error}"
        # return {
        #     "t2": round(t2, 2),
        #     "fi2": round(fi2, 2),
        #     "d2": round(d2, 2),
        #     "i2": round(i2, 2),
        #     "p2": round(p2 / 1000, 2),
        #     "tr2": round(tr2, 2),
        #     "N2": round(N2, 2),
        #     "W2": round(W2, 2),
        #     "error": error
        # }
    
@router.post("/calculate")
async def calculate(request: CalculationRequest):
    ajax = request.ajax
    ide1 = request.ide1
    ide2 = request.ide2
    idi1 = request.idi1
    idi2 = request.idi2

    vars = {ide1: idi1, ide2: idi2}

    if ajax == 1:
        return handle_ajax_1(vars, request)

    elif ajax == 2:
        return handle_ajax_2(vars, request)
