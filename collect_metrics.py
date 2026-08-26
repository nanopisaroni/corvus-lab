#!/usr/bin/env python3
"""
Corvus Lab — Dashboard Metrics Collector
Pingea cada sitio, extrae métricas propias, guarda metrics.js + historial.
Uso: python3 collect_metrics.py
"""
import json, re, subprocess, time, urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).parent
HIST = ROOT / "metrics_history.json"
OUT = ROOT / "metrics.js"
MAX_HISTORY = 90  # puntos de historial por sitio

SITES = [
    {
        "id": "corvus-lab", "name": "Corvus Lab", "url": "https://corvus-lab.vercel.app",
        "kpi": "Landing del Lab", "tag": "Lab",
    },
    {
        "id": "rigi", "name": "RIGI Tracker", "url": "https://rigi-tracker.vercel.app",
        "kpi": "proyectos RIGI", "tag": "Datos", "data": "https://rigi-tracker.vercel.app/data.js",
    },
    {
        "id": "pdp", "name": "Punto de Partida", "url": "https://punto-de-partida-three.vercel.app",
        "kpi": "indicadores", "tag": "Datos",
    },
    {
        "id": "soberania", "name": "Soberanía Cognitiva", "url": "https://soberaniacognitiva.com.ar",
        "kpi": "firmas", "tag": "Proyecto",
    },
    {
        "id": "cuentos", "name": "100 Cuentos Argentinos", "url": "https://cuentos-argentinos.vercel.app",
        "kpi": "cuentos", "tag": "Archivo",
    },
    {
        "id": "pbp", "name": "Nuestra PBP", "url": "https://nuestra-pbp.vercel.app",
        "kpi": "libros", "tag": "Archivo", "data": "https://nuestra-pbp.vercel.app/data.json",
    },
    {
        "id": "boxy", "name": "Box & Co", "url": "https://boxyco.com.ar",
        "kpi": "productos", "tag": "Comercial",
    },
    {
        "id": "oveja", "name": "La Oveja Industrial", "url": "https://laovejaindustrial.com.ar",
        "kpi": "sitio", "tag": "Comercial",
    },
    {
        "id": "kalei", "name": "Kalei Ventures", "url": "https://kaleiventures.com",
        "kpi": "portcos", "tag": "Comercial",
    },
    {
        "id": "oh", "name": "Only Hwangs", "url": "https://onlyhwangs.com",
        "kpi": "sitio", "tag": "Comercial",
    },
    {
        "id": "hipotecas", "name": "Hipotecas AR", "url": "https://hipotecas-ar.vercel.app",
        "kpi": "ofertas", "tag": "Datos", "data": "https://hipotecas-ar.vercel.app/data.js",
    },
    {
        "id": "personal", "name": "Sitio Personal", "url": "https://nanopisaroni.vercel.app",
        "kpi": "sitio", "tag": "Personal",
    },
]

def http_get(url, timeout=15):
    req = urllib.request.Request(url, headers={"User-Agent": "CorvusLab-Metrics/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")

def probe(url):
    """status + latencia + tamaño"""
    try:
        start = time.time()
        body = http_get(url)
        lat = round((time.time() - start) * 1000)
        return {"up": True, "status": 200, "latency_ms": lat, "size_kb": round(len(body.encode()) / 1024, 1), "body": body}
    except Exception as e:
        return {"up": False, "status": getattr(e, "code", None), "latency_ms": None, "size_kb": None, "body": "", "error": str(e)[:80]}

def extract(site, probe_res):
    """métricas propias por sitio"""
    body = probe_res.get("body", "")
    m = {}
    sid = site["id"]
    if sid == "rigi":
        try:
            d = http_get(site["data"])
            names = re.findall(r"name:\s*['\"]([^'\"]+)['\"]", d)
            amounts = [float(x) for x in re.findall(r"amount:\s*([0-9.]+)", d)]
            provs = set(re.findall(r"province:\s*['\"]([^'\"]+)['\"]", d))
            jobs = [int(x) for x in re.findall(r"directJobs:\s*(\d+)", d) if int(x) > 0]
            st = re.findall(r"status:\s*['\"]([^'\"]+)['\"]", d)
            m["proyectos"] = len(names)
            m["inversion_usd_m"] = round(sum(amounts), 0)
            m["provincias"] = len(provs)
            m["empleos"] = sum(jobs)
            m["aprobados"] = st.count("aprobado") + st.count("operativo")
            m["statuses"] = {s: st.count(s) for s in set(st)}
        except Exception as e:
            m["error_rigi"] = str(e)[:60]
    elif sid == "pdp":
        m["indicadores"] = int(re.search(r"(\d+)\s*indicadores", body).group(1)) if re.search(r"(\d+)\s*indicadores", body) else None
        m["paises"] = int(re.search(r"(\d+)\s*pa[íi]ses", body).group(1)) if re.search(r"(\d+)\s*pa[íi]ses", body) else None
    elif sid == "soberania":
        mm = re.search(r"(\d+)\s*personas?", body)
        m["firmas"] = int(mm.group(1)) if mm else None
    elif sid == "cuentos":
        lista = re.findall(r"disponible:\s*(true|false)", body)
        m["cuentos_total"] = len(lista)
        m["cuentos_disponibles"] = lista.count("true")
    elif sid == "pbp":
        try:
            d = json.loads(http_get(site["data"]))
            m["libros"] = len(d.get("libros", []))
            m["miembros"] = len(d.get("miembros", []))
            m["prestados"] = sum(1 for l in d.get("libros", []) if l.get("estado") == "Prestado")
        except Exception as e:
            m["error_pbp"] = str(e)[:60]
    elif sid == "boxy":
        mm = re.search(r"500 productos|(\d+)\s*productos", body)
        m["productos"] = 500 if "500 productos" in body else (int(mm.group(1)) if mm else None)
    elif sid == "kalei":
        mm = re.search(r"(\d+)\s*portfolio", body)
        m["portcos"] = int(mm.group(1)) if mm else None
    elif sid == "hipotecas":
        try:
            d = http_get(site["data"])
            m["ofertas"] = d.count('"ent":')
        except Exception as e:
            m["error_hipotecas"] = str(e)[:60]
    return m

def main():
    now = datetime.now(timezone.utc).isoformat()
    results = []
    hist = {}
    if HIST.exists():
        try:
            hist = json.loads(HIST.read_text())
        except Exception:
            hist = {}

    for site in SITES:
        p = probe(site["url"])
        metrics = extract(site, p)
        p.pop("body", None)
        entry = {
            "id": site["id"], "name": site["name"], "url": site["url"],
            "tag": site["tag"], "kpi": site["kpi"],
            "up": p["up"], "status": p["status"], "latency_ms": p["latency_ms"],
            "size_kb": p["size_kb"], "metrics": metrics,
        }
        results.append(entry)

        # historial de latencia
        h = hist.setdefault(site["id"], [])
        h.append({"t": now, "latency_ms": p["latency_ms"], "up": p["up"]})
        hist[site["id"]] = h[-MAX_HISTORY:]

    HIST.write_text(json.dumps(hist, ensure_ascii=False, indent=1))
    payload = {"generated_at": now, "sites": results}
    OUT.write_text("window.METRICS = " + json.dumps(payload, ensure_ascii=False, indent=1) + ";\n")
    up = sum(1 for r in results if r["up"])
    print(f"OK — {up}/{len(results)} sitios up — {now}")
    for r in results:
        extra = "; ".join(f"{k}={v}" for k, v in r["metrics"].items() if not isinstance(v, dict))
        print(f"  {'UP ' if r['up'] else 'DOWN'} {r['latency_ms'] if r['latency_ms'] is not None else '-':>5}ms {r['size_kb'] if r['size_kb'] is not None else '-':>6}KB  {r['name']:24s} {extra}")

if __name__ == "__main__":
    main()
