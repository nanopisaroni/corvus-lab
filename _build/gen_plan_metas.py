#!/usr/bin/env python3
"""Genera plan-de-metas.html: visualización del Plan de Metas de Córdoba 2024-2027.

Fuente: _build/data/plan-metas.json, extraído de los tres PDF oficiales
(plan 2024-2027 e informes de avance 2024 y 2025) con parse_pm.py.

Uso: python3 gen_plan_metas.py
"""
import json, re, os
from collections import Counter, defaultdict

BASE = os.path.dirname(os.path.abspath(__file__))
D = json.load(open(os.path.join(BASE, "data", "plan-metas.json")))

ESTADOS = ["Superado", "Alcanzado", "En Curso", "No Iniciado"]
COLOR = {"Superado": "#2f6b4f", "Alcanzado": "#5b8f6a", "En Curso": "#c08a2e", "No Iniciado": "#b04234"}
TXT = {"Superado": "Superado", "Alcanzado": "Alcanzado", "En Curso": "En curso", "No Iniciado": "No iniciado"}
EJES = {"1": "Seguridad", "2": "Bienestar integral e inclusión", "3": "Ciudad y servicios", "4": "Gestión"}

def num(v):
    try:
        return float(str(v).replace(".", "").replace(",", "."))
    except (ValueError, AttributeError):
        return None

def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;"))

def fmt(v):
    n = num(v)
    if n is None:
        return (v or "").strip() or "·"
    return f"{int(n):,}".replace(",", ".") if n == int(n) else f"{n:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# --- datos base
i25 = [f for f in D if f["en_i2025"]]
total_ind = len(i25)
est = Counter(f["i2025_estado"] for f in i25)
metas = set(f["codigo"] for f in D)
obj = sorted(set(f["objetivo"] for f in D), key=lambda o: [int(x) for x in o.split(".")])

# --- progreso normalizado
def progreso(f):
    b, m, a = num(f["i2025_linea_base"]), num(f["i2025_meta_2027"]), num(f["i2025_avance"])
    if None in (b, m, a) or m <= b:
        return None
    return max(0.0, min(1.0, (a - b) / (m - b)))

# --- reja por objetivo
por_obj = defaultdict(list)
for f in i25:
    por_obj[f["objetivo"]].append(f)

# --- cambios de meta
def unidad(v):
    return "%" if "%" in str(v) else "n"

cambiadas = [f for f in D if f["meta_2027_cambiada"] and unidad(f["plan_meta_2027"]) == unidad(f["i2025_meta_2027"])]
unidad_cambiada = [f for f in D if f["meta_2027_cambiada"] and unidad(f["plan_meta_2027"]) != unidad(f["i2025_meta_2027"])]
desaparecidas = sorted(set(f["codigo"] for f in D if f["en_plan"] and not f["en_i2025"]),
                       key=lambda c: [int(x) for x in c.split(".")])
nuevas = sorted(set(f["codigo"] for f in D if f["en_i2025"] and not f["en_plan"]),
                key=lambda c: [int(x) for x in c.split(".")])

# --- barras por objetivo
filas_obj = []
for o in obj:
    fs = por_obj.get(o, [])
    if not fs:
        continue
    c = Counter(f["i2025_estado"] for f in fs)
    filas_obj.append((o, len(fs), c, fs[0].get("objetivo_titulo", "")[:110]))

# --- distribución de avance
vals = [(progreso(f), f) for f in i25]
vals = [(p, f) for p, f in vals if p is not None]
buckets = [0] * 10
for p, _ in vals:
    buckets[min(9, int(p * 10))] += 1
maxb = max(buckets) or 1

rejilla = []
por_eje = defaultdict(list)
for f in i25:
    por_eje[f["eje"]].append(f)
for eje in sorted(por_eje):
    fs_eje = por_eje[eje]
    ce = Counter(f["i2025_estado"] for f in fs_eje)
    titulo_eje = next((f["eje_titulo"] for f in fs_eje if f.get("eje_titulo")), "")
    rejilla.append(
        f'<div class="ejehead"><b>Eje {eje}</b> <span>{esc(titulo_eje)}</span>'
        f'<em>{len(fs_eje)} indicadores · ' + " · ".join(f"{TXT[e]} {ce.get(e,0)}" for e in ESTADOS if ce.get(e)) + '</em></div>')
    for o in [x for x in obj if x.split(".")[0] == str(eje)]:
        fs = por_obj.get(o, [])
        if not fs:
            continue
        c = Counter(f["i2025_estado"] for f in fs)
        celdas = "".join(
            f'<i class="c" style="background:{COLOR.get(f["i2025_estado"], "#ccc")}" '
            f'title="{esc(f["codigo"])} · {esc(TXT.get(f["i2025_estado"], f["i2025_estado"]))} · '
            f'{esc((f["i2025_indicador"] or f["plan_meta"])[:150])}"></i>' for f in fs)
        desg = f'<b style="color:var(--warn)">{c.get("No Iniciado",0)}</b> sin arrancar'
        desgtxt = " · ".join(f"{TXT[e]} {c.get(e,0)}" for e in ESTADOS if c.get(e))
        rejilla.append(
            f'<div class="objrow"><div class="objlab"><b>{o}</b><span>{esc(fs[0].get("objetivo_titulo",""))}</span></div>'
            f'<div class="celdas">{celdas}</div><div class="objn" title="{esc(desgtxt)}"><b class="tot">{len(fs)}</b><em>{desg}</em></div></div>')

barras = []
for o, n, c, txt in filas_obj:
    segs = "".join(
        f'<i style="width:{(c.get(e,0)/n*100):.3f}%;background:{COLOR[e]}" title="{TXT[e]}: {c.get(e,0)}"></i>'
        for e in ESTADOS if c.get(e))
    pend = c.get("No Iniciado", 0)
    barras.append(
        f'<div class="barrow"><div class="barlab" title="{esc(txt)}"><b>{o}</b> <span>{esc(txt)}</span></div>'
        f'<div class="bar">{segs}</div>'
        f'<div class="barn">{n}<em>{pend} sin arrancar</em></div></div>')

pesos = ", ".join(f"el eje {e} tiene {n}" for e, n in sorted(((e, len(v)) for e, v in por_eje.items()), key=lambda x: -x[1])[:2])

dist = "".join(
    f'<div class="col"><i style="height:{(b/maxb*100):.1f}%"></i><span>{i*10}</span><b>{b}</b></div>'
    for i, b in enumerate(buckets))

tabla_cambios = "".join(
    f'<tr><td class="mono">{esc(f["codigo"])}</td>'
    f'<td>{esc((f["i2025_indicador"] or f["plan_indicador"])[:96])}</td>'
    f'<td class="num">{esc(f["plan_meta_2027"])}</td>'
    f'<td class="num">{esc(f["i2025_meta_2027"])}</td>'
    f'<td class="num soft">{esc(f["i2025_pagina"])}</td></tr>' for f in cambiadas)

html = f"""<!DOCTYPE html>
<html lang="es-AR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Plan de Metas de Córdoba 2024-2027 · qué prometió y qué reporta</title>
<meta name="description" content="Los 400 indicadores del Plan de Metas de la Municipalidad de Córdoba, meta por meta, con el estado que el propio municipio reporta en el informe de avance 2025.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Public+Sans:wght@300;400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
:root {{ --paper:#f8f6f2; --card:#fff; --ink:#16130f; --muted:#6d665c; --soft:#999083; --rule:#e2dcd1; --rule-strong:#c9c1b3; --warn:#a4401c; }}
* {{ box-sizing:border-box; }}
html {{ -webkit-text-size-adjust:100%; }}
body {{ margin:0; background:var(--paper); color:var(--ink); font-family:"Public Sans",-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; font-size:16px; line-height:1.55; -webkit-font-smoothing:antialiased; }}
.wrap {{ max-width:1080px; margin:0 auto; padding:0 28px; }}
.mono {{ font-family:"IBM Plex Mono",monospace; }}
nav.top {{ border-bottom:1px solid var(--rule); }}
nav.top .wrap {{ display:flex; justify-content:space-between; align-items:baseline; padding:14px 28px; }}
nav.top a {{ color:var(--muted); text-decoration:none; font-size:13px; }}
nav.top a:hover {{ color:var(--ink); }}
nav.top .brand {{ font-family:"IBM Plex Mono",monospace; font-size:12px; letter-spacing:.12em; text-transform:uppercase; color:var(--ink); }}
header.hero {{ padding:54px 0 30px; border-bottom:1px solid var(--rule-strong); }}
.kicker {{ font-family:"IBM Plex Mono",monospace; font-size:11.5px; letter-spacing:.14em; text-transform:uppercase; color:var(--soft); margin-bottom:16px; }}
h1 {{ font-size:clamp(29px,5vw,44px); line-height:1.09; letter-spacing:-.02em; font-weight:600; margin:0 0 18px; }}
.dek {{ font-size:17px; color:var(--muted); max-width:740px; margin:0; }}
.cifras {{ display:grid; grid-template-columns:repeat(4,1fr); gap:1px; background:var(--rule); border-bottom:1px solid var(--rule-strong); }}
.cifra {{ background:var(--paper); padding:24px 28px 22px; }}
.cifra b {{ display:block; font-family:"IBM Plex Mono",monospace; font-size:28px; font-weight:500; letter-spacing:-.02em; margin-bottom:4px; }}
.cifra span {{ font-size:12.5px; color:var(--muted); line-height:1.35; display:block; }}
section {{ padding:44px 0 10px; }}
h2 {{ font-size:22px; font-weight:600; letter-spacing:-.01em; margin:0 0 6px; }}
h2 span {{ font-weight:300; color:var(--soft); font-size:15px; }}
p.intro {{ color:var(--muted); max-width:780px; margin:0 0 26px; font-size:15.5px; }}
.leyenda {{ display:flex; gap:18px; flex-wrap:wrap; margin:0 0 22px; font-size:12.5px; color:var(--muted); }}
.leyenda i {{ display:inline-block; width:10px; height:10px; border-radius:1px; margin-right:6px; vertical-align:0; }}
.objrow {{ display:grid; grid-template-columns:250px 1fr 74px; gap:14px; align-items:center; padding:7px 0; border-bottom:1px solid var(--rule); }}
.objlab b {{ font-family:"IBM Plex Mono",monospace; font-size:12px; color:var(--ink); margin-right:6px; }}
.objlab span {{ font-size:12px; color:var(--muted); }}
.celdas {{ display:flex; flex-wrap:wrap; gap:3px; }}
.celdas i.c {{ width:13px; height:13px; border-radius:1px; display:block; }}
.objn {{ text-align:right; font-family:"IBM Plex Mono",monospace; font-size:12px; color:var(--soft); }}
.objn b.tot {{ font-weight:500; }}
.barrow {{ display:grid; grid-template-columns:330px 1fr 118px; gap:14px; align-items:center; padding:6px 0; border-bottom:1px solid var(--rule); }}
.barlab {{ font-size:12.5px; color:var(--muted); overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }}
.barlab b {{ font-family:"IBM Plex Mono",monospace; font-size:12px; color:var(--ink); margin-right:6px; }}
.bar {{ display:flex; height:13px; background:#efece5; border-radius:1px; overflow:hidden; }}
.bar i {{ display:block; height:100%; }}
.barn {{ text-align:right; font-family:"IBM Plex Mono",monospace; font-size:11.5px; color:var(--soft); }}
.barn em {{ display:block; font-style:normal; font-size:10.5px; color:var(--warn); }}
.dist {{ display:flex; align-items:flex-end; gap:6px; height:150px; margin:8px 0 0; }}
.dist .col {{ flex:1; display:flex; flex-direction:column; justify-content:flex-end; align-items:center; height:100%; }}
.dist .col i {{ display:block; width:100%; background:#2f6b4f; border-radius:1px 1px 0 0; min-height:1px; }}
.dist .col span {{ font-family:"IBM Plex Mono",monospace; font-size:10px; color:var(--soft); margin-top:5px; }}
.dist .col b {{ font-family:"IBM Plex Mono",monospace; font-size:10px; color:var(--muted); margin-bottom:3px; }}
table {{ width:100%; border-collapse:collapse; font-size:14px; }}
th {{ text-align:left; font-family:"IBM Plex Mono",monospace; font-size:10.5px; letter-spacing:.09em; text-transform:uppercase; color:var(--soft); font-weight:500; padding:0 10px 9px 0; border-bottom:1px solid var(--rule-strong); }}
td {{ padding:9px 10px 9px 0; border-bottom:1px solid var(--rule); vertical-align:baseline; }}
td.num, th.num {{ text-align:right; font-family:"IBM Plex Mono",monospace; font-size:13.5px; padding-right:14px; white-space:nowrap; }}
td.soft {{ color:var(--muted); }}
.tbox {{ overflow-x:auto; -webkit-overflow-scrolling:touch; }}
.nota {{ background:var(--card); border:1px solid var(--rule); border-left:3px solid var(--warn); padding:18px 20px; margin:24px 0 0; font-size:14.5px; color:var(--muted); }}
.nota b {{ color:var(--ink); }}
.metodo {{ font-size:14px; color:var(--muted); max-width:820px; }}
.metodo li {{ margin-bottom:9px; }}
footer {{ border-top:1px solid var(--rule-strong); margin-top:46px; padding:26px 0 60px; font-size:12.5px; color:var(--soft); }}
footer a {{ color:var(--muted); }}
@media (max-width:760px) {{
  .wrap {{ padding:0 18px; }}
  .cifras {{ grid-template-columns:repeat(2,1fr); }}
  .objrow {{ grid-template-columns:1fr 44px; }}
  .objlab {{ grid-column:1 / -1; }}
  .barrow {{ grid-template-columns:1fr 84px; }}
  .barlab {{ grid-column:1 / -1; white-space:normal; }}
  .celdas i.c {{ width:11px; height:11px; }}
  .objn {{ min-width:58px; }}
  .objn b.tot {{ display:none; }}
  .objn em {{ font-size:9.5px; }}
  .dist .col span {{ display:none; }}
}}
</style>
</head>
<body>
<nav class="top"><div class="wrap"><a class="brand" href="/">Corvus Lab</a><div><a href="/congreso">Congreso</a> · <a href="/bloques">Bloques</a> · <a href="/disidencias">Disidencias</a> · <a href="/mapa">Mapa</a> · <a href="/cordoba">Córdoba</a></div></div></nav>

<header class="hero"><div class="wrap">
<div class="kicker">Plan de Metas · Municipalidad de Córdoba · 2024-2027</div>
<h1>Lo que el municipio prometió, meta por meta</h1>
<p class="dek">El Plan de Metas es obligatorio por ordenanza desde 2011: el intendente fija metas con indicadores y rinde cuentas cada año. Acá están los {total_ind} indicadores del informe de avance 2025 con el estado que el propio municipio declara, más lo que cambió desde el plan original.</p>
</div></header>

<div class="cifras">
<div class="cifra"><b>{len(metas)}</b><span>metas en el plan y los informes</span></div>
<div class="cifra"><b>{len(D)}</b><span>indicadores seguidos</span></div>
<div class="cifra"><b>{est.get("No Iniciado",0)}</b><span>indicadores que el municipio reporta sin iniciar</span></div>
<div class="cifra"><b>{len(cambiadas)}</b><span>indicadores con la meta cambiada</span></div>
</div>

<section><div class="wrap">
<h2>La reja de las promesas <span>un cuadrado por indicador, agrupado por objetivo</span></h2>
<p class="intro">Cada cuadrado es un indicador del informe 2025 y el color es el estado que declara el municipio. Se lee de un golpe dónde está el peso: {pesos}.</p>
<div class="leyenda">{"".join(f'<span><i style="background:{COLOR[e]}"></i>{TXT[e]}: {est.get(e,0)}</span>' for e in ESTADOS)}</div>
{"".join(rejilla)}
</div></section>

<section><div class="wrap">
<h2>Estado por objetivo <span>los 26 objetivos del plan</span></h2>
<p class="intro">Proporción de indicadores en cada estado. El número de la derecha es el total de indicadores del objetivo y, en rojo, cuántos siguen sin arrancar.</p>
<div class="leyenda">{"".join(f'<span><i style="background:{COLOR[e]}"></i>{TXT[e]}</span>' for e in ESTADOS)}</div>
{"".join(barras)}
</div></section>

<section><div class="wrap">
<h2>Cuánto avanzó cada indicador <span>sobre los {len(vals)} con números comparables</span></h2>
<p class="intro">Distribución del avance: cada indicador se ubica en la décima parte del recorrido que va de la línea de base a la meta 2027. Un indicador en la barra del 0 no se movió desde la línea de base, aunque el municipio lo marque en curso.</p>
<div class="dist">{"".join(dist)}</div>
<p class="intro" style="margin-top:18px">Rango del gráfico: de 0 a 100 por ciento del recorrido. Los {len(i25) - len(vals)} indicadores que no tienen números comparables quedan afuera, no se estiman.</p>
</div></section>

<section><div class="wrap">
<h2>Las metas que se movieron <span>{len(cambiadas)} indicadores con la meta al 2027 distinta a la del plan</span></h2>
<p class="intro">El plan fijó un valor para 2027 y el informe de avance 2025 reporta otro. La columna de la derecha es la página del informe donde está el dato.</p>
<div class="tbox"><table>
<thead><tr><th>Meta</th><th>Indicador</th><th class="num">Plan</th><th class="num">Informe 2025</th><th class="num">Pág.</th></tr></thead>
<tbody>{tabla_cambios}</tbody>
</table></div>
<p class="intro" style="margin-top:14px">Otros {len(unidad_cambiada)} indicadores cambiaron de unidad de medida entre el plan y el informe, así que no se comparan acá: se declaran en el método.</p>
<div class="nota"><b>{len(desaparecidas)} metas del plan no aparecen en el informe 2025</b> y aparecen {len(nuevas)} códigos nuevos. El propio informe menciona un «Informe del Plan de Metas Rectificado 2025» que no está publicado: las metas cambiaron y el documento que lo explica no está disponible. Metas que desaparecen: <span class="mono">{esc(", ".join(desaparecidas))}</span>.</div>
</div></section>

<section><div class="wrap">
<h2>Cómo se hizo y qué no dice</h2>
<ul class="metodo">
<li>Fuente: Plan de Metas 2024-2027 (98 páginas) e informes de avance 2024 (153) y 2025 (182), publicados por la Municipalidad de Córdoba. La tabla se extrajo del PDF por coordenadas, no por orden de lectura, y se controló contra las páginas renderizadas.</li>
<li>El grano es el indicador, no la meta: {sum(1 for c, n in Counter(f["codigo"] for f in i25).items() if n > 1)} metas tienen más de un indicador y cada uno tiene su propio avance y su propio estado.</li>
<li>Los estados y los porcentajes son los que declara el municipio. No hay auditoría externa y esta página no verifica los datos: los publica con su fuente y su página.</li>
<li>La columna «Evidencia» del informe repite el código de la meta, no enlaza al respaldo documental.</li>
<li>{len(unidad_cambiada)} indicadores pasaron de porcentaje a valor absoluto, o al revés, entre el plan y el informe, y quedan fuera de la tabla de metas movidas: {esc(", ".join(f["codigo"] for f in unidad_cambiada))}.</li>
<li>Hay metas con plazo 2024 que siguen en curso en 2025, y al menos una marcada como superada con avance por debajo de la meta. Se muestran como están.</li>
<li>La ordenanza 11.942 obliga a elevar el informe al Concejo antes del 10 de marzo y a convocarlo a audiencia pública. El informe 2025 se presentó en la audiencia pública 74, del 15 de mayo de 2026.</li>
</ul>
</div></section>

<footer><div class="wrap">Elaborado con los documentos oficiales del municipio. Cada dato lleva su fuente y su página para que se pueda controlar. · <a href="/">Corvus Lab</a></div></footer>
</body></html>
"""

out = os.path.join(os.path.dirname(BASE), "plan-de-metas.html")
open(out, "w", encoding="utf-8").write(html)
print(f"escrito {out} {len(html)} bytes | {total_ind} indicadores | {len(rejilla)} objetivos en la reja | {len(cambiadas)} cambios | {len(vals)} con avance numérico")
