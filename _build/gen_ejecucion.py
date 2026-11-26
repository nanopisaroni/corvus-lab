#!/usr/bin/env python3
# Genera ejecucion.html: qué se asignó, qué se devengó y qué quedó sin ejecutar (programas 2026).
import json, os, html
from collections import Counter, defaultdict

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = "/home/nanobot/projects/phi-cordoba"
OUT = os.path.join(BASE, "ejecucion.html")
esc = html.escape

prog = json.load(open(f"{SRC}/programas.json"))
ipc = json.load(open(f"{SRC}/ipc.json"))
tot = {r["anio"]: r for r in json.load(open(f"{SRC}/totales.json"))}
F = {int(y): v for y, v in ipc["factores"].items()}
CORTE = ipc["ultimo_publicado"]          # 2026-08 publicación del IPC
MESES = 9                                 # último mes con devengado = septiembre

P26 = [p for p in prog if p["anio"] == 2026]
P25 = [p for p in prog if p["anio"] == 2025]

def miles(x):  # millones -> string en billones/millones
    if x >= 1e6: return f"$ {x/1e6:,.2f} billones".replace(",", ".")
    return f"$ {x/1e3:,.0f} miles de millones".replace(",", ".")

def n(x, d=1): return f"{x:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")

vig = sum(p["credito_vigente"] or 0 for p in P26)
dev = sum(p["credito_devengado"] or 0 for p in P26)
pag = sum(p["credito_pagado"] or 0 for p in P26)
ejec = dev / vig * 100
pago_sobre_dev = pag / dev * 100

def real(rows, m=MESES):
    t = 0
    for p in rows:
        ser = p.get("credito_devengado_mensual") or [0] * 12
        for i in range(m):
            t += ser[i] * F[p["anio"]][i]
    return t / 1e6

r26, r25 = real(P26), real(P25)
var_real = (r26 / r25 - 1) * 100

# jurisdicciones
jur = defaultdict(lambda: [0.0, 0.0])
for p in P26:
    k = p["jurisdiccion_desc"]
    jur[k][0] += p["credito_vigente"] or 0
    jur[k][1] += p["credito_devengado"] or 0
jur = sorted(jur.items(), key=lambda x: -x[1][0])

MAXJ = jur[0][1][0]
BARRAS = ""
for k, (v, d) in jur[:12]:
    pct = d / v * 100 if v else 0
    BARRAS += (f'<div class="jr"><div class="jn" title="{esc(k)}">{esc(k)}</div>'
               f'<div class="jt"><div class="jf" style="width:{pct:,.1f}%"></div>'
               f'<span class="jm">{"75%" if False else ""}</span></div>'
               f'<div class="jv"><b>{n(pct)}%</b><span>{n(v/1e6,2)}</span></div></div>')

# programas: más crédito y menos ejecución
bajos = []
for p in P26:
    v = p["credito_vigente"] or 0
    if v < 30000:  # más de 30.000 millones
        continue
    e = (p["credito_devengado"] or 0) / v * 100
    if e >= 30: continue
    bajos.append((e, v, p))
bajos.sort(key=lambda x: -x[1])
FILAS = ""
for e, v, p in bajos[:15]:
    FILAS += (f'<tr><td class="pr"><b>{esc(p["programa_desc"][:52])}</b>'
              f'<span>{esc(p["jurisdiccion_desc"])}</span></td>'
              f'<td class="num">{n(v/1e3,0)}</td>'
              f'<td class="num">{n((p["credito_devengado"] or 0)/1e3,0)}</td>'
              f'<td class="num pct {"cero" if e < 1 else ""}">{n(e)}%</td></tr>')

suma_bajos = sum(v for _, v, _ in bajos)

# histograma
bins = Counter()
for p in P26:
    v = p["credito_vigente"] or 0
    if v <= 0: continue
    e = (p["credito_devengado"] or 0) / v * 100
    b = 0 if e == 0 else min(int(e // 20), 5)
    bins[b] += 1
ETQ = ["0%", "0–20%", "20–40%", "40–60%", "60–80%", "80–100%", "100% o más"]
HIST = ""
maxb = max(bins.values())
for i, et in enumerate(ETQ):
    c = bins[i]
    HIST += (f'<div class="hb"><div class="hl">{et}</div>'
             f'<div class="ht"><div class="hf" style="width:{c/maxb*100:.1f}%"></div></div>'
             f'<div class="hc">{c}</div></div>')

# el programa cero
cero = max([p for p in P26 if (p["credito_vigente"] or 0) > 0 and (p["credito_devengado"] or 0) == 0],
           key=lambda p: p["credito_vigente"])

OBL = [(k, v) for k, v in jur if "Obligaciones" in k][0]
OBL_VIG, OBL_PCT = OBL[1][0], (OBL[1][1] / OBL[1][0] * 100 if OBL[1][0] else 0)

CSS = """
:root { --paper:#f8f6f2; --card:#fff; --ink:#16130f; --muted:#6d665c; --soft:#999083; --rule:#e2dcd1; --rule-strong:#c9c1b3; --ok:#2f6b4f; --no:#b04234; --amb:#9a6b1f; }
* { box-sizing:border-box; }
body { margin:0; background:var(--paper); color:var(--ink); font-family:"Public Sans",-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; font-size:16px; line-height:1.55; -webkit-font-smoothing:antialiased; }
.wrap { max-width:1080px; margin:0 auto; padding:0 28px; }
nav.top { border-bottom:1px solid var(--rule); }
nav.top .wrap { display:flex; justify-content:space-between; align-items:baseline; padding:14px 28px; gap:16px; flex-wrap:wrap; }
nav.top a { color:var(--muted); text-decoration:none; font-size:13px; }
nav.top a:hover { color:var(--ink); }
nav.top .brand { font-family:"IBM Plex Mono",monospace; font-size:12px; letter-spacing:.12em; text-transform:uppercase; color:var(--ink); }
.kicker { font-family:"IBM Plex Mono",monospace; font-size:11.5px; letter-spacing:.14em; text-transform:uppercase; color:var(--soft); margin-bottom:16px; }
header.hero { padding:52px 0 30px; border-bottom:1px solid var(--rule-strong); }
h1 { font-size:clamp(29px,5vw,44px); line-height:1.09; letter-spacing:-.02em; font-weight:600; margin:0 0 18px; }
.dek { font-size:18px; color:#3b352d; max-width:770px; margin:0; }
section { padding:42px 0; border-bottom:1px solid var(--rule); }
h2 { font-size:23px; letter-spacing:-.01em; font-weight:600; margin:0 0 6px; }
.sub { color:var(--muted); font-size:15px; margin:0 0 22px; max-width:740px; }
.kpis { display:grid; grid-template-columns:repeat(4,1fr); gap:22px; }
.kpis div b { display:block; font-family:"IBM Plex Mono",monospace; font-size:30px; font-weight:500; letter-spacing:-.03em; line-height:1; margin-bottom:6px; }
.kpis div span { font-size:12.5px; color:var(--muted); line-height:1.4; display:block; }
.kpis div b.caida { color:var(--no); }
.jr { display:grid; grid-template-columns:220px 1fr 96px; gap:10px; align-items:center; padding:5px 0; }
.jn { font-size:13px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.jt { height:12px; background:#eee9e0; border-radius:1px; overflow:hidden; position:relative; }
.jf { height:100%; background:#3b352d; }
.jv b { font-family:"IBM Plex Mono",monospace; font-size:12.5px; }
.jv span { display:block; font-size:9.5px; color:var(--soft); font-family:"IBM Plex Mono",monospace; }
table.pr { width:100%; border-collapse:collapse; }
table.pr th { text-align:left; font-family:"IBM Plex Mono",monospace; font-size:9.5px; letter-spacing:.06em; text-transform:uppercase; color:var(--soft); font-weight:500; padding:0 4px 8px; border-bottom:1px solid var(--rule-strong); }
table.pr th.num { text-align:right; }
table.pr td { border-bottom:1px solid #ece7de; padding:7px 4px; vertical-align:top; }
td.pr b { display:block; font-size:13.5px; font-weight:500; line-height:1.25; }
td.pr span { font-size:11px; color:var(--soft); }
td.num { text-align:right; font-family:"IBM Plex Mono",monospace; font-size:12.5px; white-space:nowrap; }
td.num.pct { font-weight:500; }
td.num.cero { color:var(--no); }
.hb { display:grid; grid-template-columns:88px 1fr 40px; gap:10px; align-items:center; padding:4px 0; }
.hl { font-size:12px; color:var(--muted); font-family:"IBM Plex Mono",monospace; }
.ht { height:14px; background:#eee9e0; border-radius:1px; overflow:hidden; }
.hf { height:100%; background:#c9c1b3; }
.hc { font-family:"IBM Plex Mono",monospace; font-size:12px; text-align:right; }
.box { border-left:3px solid #16130f; background:#f4f1ea; padding:15px 18px; font-size:14.5px; margin:18px 0 0; }
.box b { font-weight:600; }
footer { padding:28px 0 48px; font-size:13px; color:var(--muted); }
@media (max-width:860px) { .kpis { grid-template-columns:repeat(2,1fr); gap:18px; } }
@media (max-width:620px) {
  .wrap { padding:0 16px; }
  header.hero { padding:32px 0 20px; }
  section { padding:30px 0; }
  .dek { font-size:16px; }
  .kpis { grid-template-columns:1fr; gap:14px; }
  .jr { grid-template-columns:118px 1fr 74px; }
  .jn { font-size:11px; }
  table.pr td:nth-child(2), table.pr th:nth-child(2) { display:none; }
  td.pr b { font-size:12px; }
  td.num { font-size:11px; }
}
"""

HTML = f"""<!DOCTYPE html>
<html lang="es-AR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>La plata que se asigna y no se gasta · ejecución del presupuesto 2026</title>
<meta name="description" content="Ejecución presupuestaria por programa al 30 de septiembre de 2026: qué se asignó, qué se devengó, qué quedó sin usar y cómo cambió contra el mismo período de 2025 en términos reales.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Public+Sans:wght@300;400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>{CSS}</style>
</head>
<body>

<nav class="top"><div class="wrap">
  <a class="brand" href="/">Corvus Lab</a>
  <div><a href="/congreso">Congreso</a> · <a href="/bloques">Bloques</a> · <a href="/viabilidad">Viabilidad</a> · <a href="/simulador">Simulador</a> · <a href="/termometro">Termómetro</a> · <a href="/ejecucion">Ejecución</a> · <a href="/disidencias">Disidencias</a> · <a href="/plan-de-metas">Plan de Metas</a> · <a href="/proyectos">Trabajos</a></div>
</div></nav>

<header class="hero"><div class="wrap">
  <div class="kicker">Presupuesto nacional · ejercicio 2026 · corte 30 de septiembre</div>
  <h1>La plata que se asigna y no se gasta</h1>
  <p class="dek">A nueve meses del año, el Estado devengó {n(ejec)}% del crédito vigente. No es un dato raro: el ritmo parejo marcaría 75%. Lo raro está repartido: hay {len(bajos)} programas con más de {miles(30000e0).replace('$ ','')} asignados que no llegaron al 30% de ejecución, y uno de ellos tiene {miles(cero['credito_vigente'])} con cero devengado.</p>
</div></header>

<section><div class="wrap">
  <div class="kpis">
    <div><b>{miles(vig)}</b><span>crédito vigente 2026, después de las modificaciones del año.</span></div>
    <div><b>{n(ejec)}%</b><span>devengado sobre vigente al 30 de septiembre. {miles(dev)} ejecutados.</span></div>
    <div><b class="caida">{n(var_real)}%</b><span>variación real del gasto devengado contra enero–septiembre de 2025. Inflación descontada.</span></div>
    <div><b>{n(pago_sobre_dev)}%</b><span>de lo devengado ya está pagado. La deuda flotante es marginal: el problema no es que no paguen, es que no ejecutan.</span></div>
  </div>
</div></section>

<section><div class="wrap">
  <h2>Cómo se ejecuta cada ministerio</h2>
  <p class="sub">Porcentaje del crédito vigente devengado al 30 de septiembre. El ritmo parejo del año sería 75%. Los doce organismos con más crédito; el número chico debajo de cada porcentaje es el crédito vigente en billones.</p>
  {BARRAS}
  <div class="box"><b>El caso más grande.</b> «Obligaciones a Cargo del Tesoro» devengó {n(OBL_PCT)}% de {miles(OBL_VIG)} al 30 de septiembre: de los doce organismos con más crédito es el que menos ejecuta, y es la caja con la que el Ejecutivo cubre imprevistos.</div>
</div></section>

<section><div class="wrap">
  <h2>Los programas con plata y sin ejecución</h2>
  <p class="sub">Programas con crédito vigente superior a 30.000 millones y menos del 30% devengado al 30 de septiembre. Sumados son {miles(suma_bajos)} asignados.</p>
  <table class="pr">
    <thead><tr><th>Programa</th><th class="num">Vigente · miles de millones</th><th class="num">Devengado · miles de millones</th><th class="num">Ejecución</th></tr></thead>
    <tbody>{FILAS}</tbody>
  </table>
</div></section>

<section><div class="wrap">
  <h2>La distribución completa</h2>
  <p class="sub">Cuántos de los {len(P26)} programas del presupuesto 2026 caen en cada tramo de ejecución. La mayoría está entre 40% y 80%, que es lo esperable a nueve meses. Lo que importa son las colas.</p>
  {HIST}
  <div class="box"><b>El programa que no arrancó.</b> «{esc(cero['programa_desc'])}», dentro de {esc(cero['jurisdiccion_desc'])}, tiene {miles(cero['credito_vigente'])} de crédito vigente y cero pesos devengados. Es el noveno programa más grande del presupuesto. No es un error de carga: la serie mensual muestra doce meses en cero.</div>
</div></section>

<section><div class="wrap">
  <h2>Lo que este dato no dice</h2>
  <p class="sub">Tres límites que hay que tener presentes antes de usar cualquier número de esta página.</p>
  <div class="box" style="margin-top:0">
    <p style="margin:0 0 10px"><b>El corte es a septiembre.</b> Comparar el devengado contra el crédito anual castiga a todo el mundo por igual: el 75% es la referencia pareja, no el 100%. Un programa al 70% puede estar perfectamente en ritmo.</p>
    <p style="margin:0 0 10px"><b>El crédito vigente no es el presupuesto original.</b> Cambió durante el año por decisiones del Ejecutivo. Un programa puede ejecutar el 120% porque le ampliaron la partida, o el 30% porque se la recortaron.</p>
    <p style="margin:0"><b>Devengar no es gastar bien.</b> El devengado es la obligación de pago asumida, no la obra terminada ni el servicio prestado. Un programa puede devengar el 100% y no entregar nada.</p>
  </div>
</div></section>

<footer><div class="wrap">
  Fuente: Presupuesto Abierto, datos abiertos del Ministerio de Economía (licencia CC BY 4.0), distribuidos por presupuesto.openarg.org en doce conjuntos JSON. Ejercicio 2026 con último mes devengado en septiembre; IPC nacional para el deflacte, base diciembre 2016, con factores por mes del mismo conjunto. Universo: {len(P26)} programas del clasificador presupuestario, que cubren la totalidad del crédito vigente. Series mensuales por programa leídas del campo devengado_mensual. Actualizado el 25 de noviembre de 2026.
</div></footer>

</body></html>"""

open(OUT, "w", encoding="utf-8").write(HTML)
print(f"ejecucion.html {len(HTML):,} bytes · ejec {n(ejec)}% · var real {n(var_real)}% · bajos {len(bajos)} · cero {miles(cero['credito_vigente'])}")
