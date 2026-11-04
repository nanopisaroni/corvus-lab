#!/usr/bin/env python3
# Extrae todos los proyectos de cada diputado (cola plana de páginas, reanudable).
import urllib.request, re, json, os, time, threading, concurrent.futures as cf

UA = {"User-Agent": "Mozilla/5.0 (compatible; CorvusLab/1.0)"}
DEST = "/tmp/hcdn_pages"
os.makedirs(DEST, exist_ok=True)
SLUGS = json.load(open("/tmp/slugs.json"))
BASE = "https://www.hcdn.gob.ar/diputados/{s}/listado-proyectos.html"
_LOCKS = {}
_LOCKS_GUARD = threading.Lock()


def lock_de(slug):
    with _LOCKS_GUARD:
        return _LOCKS.setdefault(slug, threading.Lock())


def get(u, tries=3):
    for i in range(tries):
        try:
            return urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=40).read().decode("utf-8", "ignore")
        except Exception:
            time.sleep(0.6 * (i + 1))
    return ""


def limpia(x):
    x = re.sub(r"<[^>]+>", " ", x)
    for a, b in (("&nbsp;", " "), ("&aacute;", "á"), ("&eacute;", "é"), ("&iacute;", "í"),
                 ("&oacute;", "ó"), ("&uacute;", "ú"), ("&ntilde;", "ñ"), ("&amp;", "&"),
                 ("&quot;", '"'), ("&#39;", "'")):
        x = x.replace(a, b)
    return re.sub(r"\s+", " ", x).strip()


def parse(h):
    mt = re.search(r"([\d\.]+)\s*Proyectos?\s*Encontrados", h)
    total = int(mt.group(1).replace(".", "")) if mt else 0
    mp = re.search(r"Página\s*(\d+)\s*de\s*(\d+)", h)
    paginas = int(mp.group(2)) if mp else 1
    filas = []
    for f in re.findall(r"<tr[^>]*>(.*?)</tr>", h, re.S):
        cols = [limpia(c) for c in re.findall(r"<td[^>]*>(.*?)</td>", f, re.S)]
        if len(cols) >= 4 and re.match(r"^\d+-[A-Z]-?\d{4}$", cols[0]):
            filas.append({"exp": cols[0], "tipo": cols[1], "sumario": cols[2][:300], "fecha": cols[3]})
    return total, paginas, filas


def guardar(slug, paginas, extra=None):
    """escribe/actualiza el json del diputado con una página nueva"""
    p = f"{DEST}/{slug}.json"
    d = json.load(open(p)) if os.path.exists(p) else {}
    d.setdefault("total", 0); d.setdefault("paginas", 0); d.setdefault("hechas", []); d.setdefault("filas", [])
    if extra:
        d["total"] = extra[0] or d["total"]
        d["paginas"] = extra[1] or d["paginas"]
    return d


def bajar_tarea(t):
    slug, pagina = t
    with lock_de(slug):
        return _bajar(slug, pagina)


def _bajar(slug, pagina):
    p = f"{DEST}/{slug}.json"
    d = json.load(open(p)) if os.path.exists(p) else {}
    d.setdefault("total", 0); d.setdefault("paginas", 0); d.setdefault("hechas", []); d.setdefault("filas", [])
    if pagina in d.get("hechas", []):
        return slug, pagina, 0
    h = get(BASE.format(s=slug) + (f"?pagina={pagina}" if pagina > 1 else ""))
    if not h:
        return slug, pagina, -1
    total, paginas, filas = parse(h)
    d["total"] = total or d["total"]
    d["paginas"] = paginas or d["paginas"]
    d["hechas"] = sorted(set(list(d.get("hechas", [])) + [pagina]))
    vistos = {f["exp"] + f["fecha"] for f in d["filas"]}
    for f in filas:
        k = f["exp"] + f["fecha"]
        if k not in vistos:
            d["filas"].append(f)
            vistos.add(k)
    d["completo"] = len(d["hechas"]) >= d["paginas"]
    tmp = p + ".tmp"
    with open(tmp, "w") as fh:
        json.dump(d, fh, ensure_ascii=False)
    os.replace(tmp, p)
    return slug, pagina, len(filas)


def estado():
    comp = 0
    for s in SLUGS:
        p = f"{DEST}/{s}.json"
        if os.path.exists(p):
            try:
                d = json.load(open(p))
                if d.get("completo"):
                    comp += 1
            except Exception:
                pass
    return comp


# fase 1: página 1 de quienes no tienen nada
faltan = [s for s in SLUGS if not os.path.exists(f"{DEST}/{s}.json")]
if faltan:
    with cf.ThreadPoolExecutor(max_workers=8) as ex:
        list(ex.map(bajar_tarea, [(s, 1) for s in faltan]))
    print(f"fase 1: {len(faltan)} primeras páginas · completos {estado()}", flush=True)

# fase 2: cola plana con todas las páginas restantes
tareas = []
for s in SLUGS:
    p = f"{DEST}/{s}.json"
    if not os.path.exists(p):
        continue
    d = json.load(open(p))
    for pg in range(1, d.get("paginas", 1) + 1):
        if pg not in d.get("hechas", []):
            tareas.append((s, pg))
print(f"fase 2: {len(tareas)} páginas pendientes", flush=True)

import traceback
def seguro(t):
    try:
        return bajar_tarea(t)
    except Exception:
        traceback.print_exc()
        return t[0], t[1], -2

t0 = time.time()
hechas = 0
LOTE = 60
for k in range(0, len(tareas), LOTE):
    lote = tareas[k:k+LOTE]
    with cf.ThreadPoolExecutor(max_workers=10) as ex:
        list(ex.map(seguro, lote))
    hechas += len(lote)
    if hechas % 300 == 0 or hechas >= len(tareas):
        print(f"  {hechas}/{len(tareas)} · {time.time()-t0:.0f}s · completos {estado()}", flush=True)
print(f"FIN: {hechas} páginas · completos {estado()}/{len(SLUGS)} · {time.time()-t0:.0f}s", flush=True)
