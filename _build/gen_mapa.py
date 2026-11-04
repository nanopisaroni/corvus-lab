#!/usr/bin/env python3
# Genera mapa.html desde _build/data/mapa.json
# Fuente: actas de votación nominal de los diarios de sesiones (período 144).
import json, os, html, random

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(BASE, "_build", "data", "mapa.json")
OUT = os.path.join(BASE, "mapa.html")

d = json.load(open(SRC, encoding="utf-8"))
meta, dips = d["meta"], d["dips"]

PARTICULAS = {"de", "del", "la", "las", "los", "por", "para", "y", "el"}
SIGLAS = {"pro", "ucr", "mid", "pts", "fit", "eva", "pst"}


def bloque_txt(b):
    out = []
    for i, w in enumerate(b.split()):
        lw = w.lower()
        if lw in SIGLAS:
            out.append(w.upper())
        elif lw in PARTICULAS:
            out.append(w.capitalize() if i == 0 else lw)
        else:
            out.append(w.capitalize())
    return " ".join(out)


COLOR = {
    "LA LIBERTAD AVANZA": "#6b4fa8",
    "UNIÓN POR LA PATRIA": "#2f6fa8",
    "PRO": "#b8912a",
    "UCR - UNIÓN CÍVICA RADICAL": "#b5442f",
    "PROVINCIAS UNIDAS": "#3f7d6b",
    "ARGENTINA FEDERAL": "#8a5a12",
    "ELIJO CATAMARCA": "#7a5c9e",
    "INDEPENDENCIA": "#7a5c9e",
}
GRIS = "#b3ab9e"


def color(b):
    return COLOR.get(b.upper().replace("Ú", "U"), GRIS)


# --- eje horizontal: cada diputado es un punto ---
random.seed(11)
W, H = 1000, 200
pts = []
for p in dips:
    x = 40 + (p["x"] + 100) / 200 * (W - 80)
    y = 100 + random.gauss(0, 34)
    y = max(24, min(H - 24, y))
    pts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.4" fill="{color(p["b"])}" opacity=".82"><title>{html.escape(p["n"])} · {html.escape(bloque_txt(p["b"]))}</title></circle>')
EJE = "\n".join(pts)

# --- medias por bloque ---
from collections import defaultdict
bl = defaultdict(list)
for p in dips:
    bl[p["b"]].append(p["x"])
medias = sorted(((b, sum(v) / len(v), len(v)) for b, v in bl.items()), key=lambda t: -t[1])
FILAS_BLOQUE = "".join(
    f'<tr><td><span class="dot" style="background:{color(b)}"></span>{html.escape(bloque_txt(b))}</td>'
    f'<td class="num">{n}</td><td class="num">{m:+.0f}</td>'
    f'<td class="bar"><span style="width:{abs(m)/2:.1f}%;margin-left:{50 if m < 0 else 50}%;background:{color(b)}"></span></td></tr>'
    for b, m, n in medias if n >= 2)

# --- disidentes ---
con = [p for p in dips if p.get("vot") and p["vot"] >= meta["actas"] * 0.7 and p.get("dis") is not None]
con.sort(key=lambda p: -(p["dis"] / p["vot"]))
TOP_DIS = "".join(
    f'<li><span class="pos">{i}</span><span class="nm">{html.escape(p["n"])}</span>'
    f'<span class="bl">{html.escape(bloque_txt(p["b"]))}</span>'
    f'<span class="vl">{100*p["dis"]/p["vot"]:.0f}<em>%</em></span></li>'
    for i, p in enumerate(con[:12], 1))
perfectos = sum(1 for p in con if p["dis"] == 0)

# --- extremos ---
izq = [p for p in dips if p["x"] <= -85]
der = [p for p in dips if p["x"] >= 85]

HTML = f"""<!DOCTYPE html>
<html lang="es-AR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Mapa de votaciones · Cámara de Diputados</title>
<meta name="description" content="Cómo votó cada diputado en el período 144. Posiciones calculadas sobre 76 votaciones nominales, sin interpretación editorial.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Public+Sans:wght@300;400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
:root {{
  --paper: #f8f6f2; --card: #ffffff; --ink: #16130f; --muted: #6d665c;
  --soft: #999083; --rule: #e2dcd1; --rule-strong: #c9c1b3;
}}
* {{ box-sizing: border-box; }}
html {{ -webkit-text-size-adjust: 100%; }}
body {{ margin: 0; background: var(--paper); color: var(--ink);
  font-family: "Public Sans", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  font-size: 16px; line-height: 1.55; -webkit-font-smoothing: antialiased; }}
.wrap {{ max-width: 1080px; margin: 0 auto; padding: 0 28px; }}
.mono {{ font-family: "IBM Plex Mono", monospace; }}
nav.top {{ border-bottom: 1px solid var(--rule); }}
nav.top .wrap {{ display: flex; justify-content: space-between; align-items: baseline; padding: 14px 28px; }}
nav.top a {{ color: var(--muted); text-decoration: none; font-size: 13px; }}
nav.top a:hover {{ color: var(--ink); }}
nav.top .brand {{ font-family: "IBM Plex Mono", monospace; font-size: 12px; letter-spacing: .12em; text-transform: uppercase; color: var(--ink); }}
header.hero {{ padding: 54px 0 30px; border-bottom: 1px solid var(--rule-strong); }}
.kicker {{ font-family: "IBM Plex Mono", monospace; font-size: 11.5px; letter-spacing: .14em;
  text-transform: uppercase; color: var(--soft); margin-bottom: 16px; }}
h1 {{ font-size: clamp(30px, 5vw, 46px); line-height: 1.08; letter-spacing: -.02em; font-weight: 600; margin: 0 0 18px; }}
.dek {{ font-size: 17.5px; color: var(--muted); max-width: 720px; margin: 0; }}
.cifras {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 1px; background: var(--rule);
  border-bottom: 1px solid var(--rule-strong); }}
.cifra {{ background: var(--paper); padding: 24px 28px 22px; }}
.cifra b {{ display: block; font-family: "IBM Plex Mono", monospace; font-size: 30px; font-weight: 500;
  letter-spacing: -.02em; margin-bottom: 4px; }}
.cifra span {{ font-size: 12.5px; color: var(--muted); line-height: 1.35; display: block; }}
section {{ padding: 46px 0 12px; }}
h2 {{ font-size: 22px; font-weight: 600; letter-spacing: -.01em; margin: 0 0 6px; }}
h2 span {{ font-weight: 300; color: var(--soft); font-size: 15px; }}
p.intro {{ color: var(--muted); max-width: 760px; margin: 0 0 26px; font-size: 15.5px; }}
.eje {{ background: var(--card); border: 1px solid var(--rule); border-radius: 3px; padding: 22px 10px 8px; margin-bottom: 12px; overflow-x: auto; }}
.eje svg {{ display: block; width: 100%; min-width: 620px; height: auto; }}
.extremos {{ display: flex; justify-content: space-between; font-family: "IBM Plex Mono", monospace;
  font-size: 11.5px; color: var(--soft); padding: 0 14px 8px; }}
.extremos b {{ display: block; color: var(--ink); font-weight: 500; font-size: 12.5px; margin-top: 3px;
  font-family: "Public Sans", sans-serif; }}
table {{ width: 100%; border-collapse: collapse; font-size: 14.5px; }}
th {{ text-align: left; font-family: "IBM Plex Mono", monospace; font-size: 11px; letter-spacing: .1em;
  text-transform: uppercase; color: var(--soft); font-weight: 500; padding: 0 8px 10px; border-bottom: 1px solid var(--rule-strong); }}
td {{ padding: 9px 8px; border-bottom: 1px solid var(--rule); vertical-align: middle; }}
td.num, th.num {{ text-align: right; font-family: "IBM Plex Mono", monospace; font-variant-numeric: tabular-nums; }}
td.bar {{ width: 30%; }}
td.bar span {{ display: block; height: 7px; border-radius: 1px; opacity: .75; }}
.dot {{ display: inline-block; width: 9px; height: 9px; border-radius: 50%; margin-right: 9px; vertical-align: middle; }}
ol.rank {{ list-style: none; padding: 0; margin: 0; }}
ol.rank li {{ display: flex; align-items: baseline; gap: 10px; padding: 9px 0; border-bottom: 1px solid var(--rule); }}
ol.rank .pos {{ color: var(--soft); font-family: "IBM Plex Mono", monospace; font-size: 12px; width: 20px; }}
ol.rank .nm {{ flex: 1; }}
ol.rank .bl {{ color: var(--soft); font-size: 12.5px; }}
ol.rank .vl {{ font-family: "IBM Plex Mono", monospace; font-variant-numeric: tabular-nums; min-width: 48px; text-align: right; }}
ol.rank .vl em {{ font-style: normal; color: var(--soft); font-size: 11px; }}
.metodo {{ border-top: 1px solid var(--rule-strong); margin-top: 46px; padding: 34px 0 60px; }}
.metodo h2 {{ font-size: 16px; }}
.metodo p {{ color: var(--muted); font-size: 14.5px; max-width: 760px; margin: 0 0 12px; }}
footer {{ border-top: 1px solid var(--rule); padding: 22px 0 40px; color: var(--soft); font-size: 12.5px; }}
@media (max-width: 760px) {{
  .cifras {{ grid-template-columns: 1fr 1fr; }}
  .cifra {{ padding: 18px 20px; }}
  td.bar {{ display: none; }}
}}
</style>
</head>
<body>

<nav class="top"><div class="wrap">
  <a class="brand" href="/">Corvus Lab</a>
  <div><a href="/congreso">Congreso</a> · <a href="/proyectos">Trabajos</a></div>
</div></nav>

<header class="hero"><div class="wrap">
  <div class="kicker">Cámara de Diputados · Período 144 · 2026</div>
  <h1>Dónde está parado cada diputado,<br>según cómo votó</h1>
  <p class="dek">Las posiciones salen de las {meta["actas"]} votaciones nominales del período. Nadie las asignó a mano: se calculan a partir de los votos registrados en las actas de cada sesión.</p>
</div></header>

<div class="cifras">
  <div class="cifra"><b>{meta["dips"]}</b><span>diputados ubicados</span></div>
  <div class="cifra"><b>{meta["actas"]}</b><span>votaciones nominales usadas</span></div>
  <div class="cifra"><b>{meta["pc1"]:.0f}%</b><span>de la varianza en un solo eje</span></div>
  <div class="cifra"><b>{perfectos}</b><span>nunca votaron contra su bloque</span></div>
</div>

<section><div class="wrap">
  <h2>El eje <span>· cada punto es un diputado</span></h2>
  <p class="intro">De izquierda a derecha, la posición que resume todos sus votos. Los colores son el bloque. Cuanto más cerca están dos puntos, más parecido votaron.</p>
  <div class="eje">
    <svg viewBox="0 0 {W} {H}" role="img" aria-label="Distribución de diputados en el eje de votación">
      <line x1="40" y1="{H-14}" x2="{W-40}" y2="{H-14}" stroke="#c9c1b3" stroke-width="1"/>
      {EJE}
    </svg>
  </div>
  <div class="extremos">
    <div>Votó con el oficialismo<b>{html.escape(izq[0]["n"])} · {html.escape(bloque_txt(izq[0]["b"]))}</b></div>
    <div style="text-align:right">Votó con la oposición<b>{html.escape(der[-1]["n"])} · {html.escape(bloque_txt(der[-1]["b"]))}</b></div>
  </div>
</div></section>

<section><div class="wrap">
  <h2>Los bloques <span>· posición media</span></h2>
  <p class="intro">La media de cada bloque sobre el mismo eje. Los bloques chicos no aparecen si tienen menos de dos diputados ubicados.</p>
  <table>
    <thead><tr><th>Bloque</th><th class="num">Diputados</th><th class="num">Posición</th><th></th></tr></thead>
    <tbody>{FILAS_BLOQUE}</tbody>
  </table>
</div></section>

<section><div class="wrap">
  <h2>Los que se corren del bloque <span>· % de votos contra la mayoría</span></h2>
  <p class="intro">Para cada votación se toma la posición mayoritaria del bloque de cada diputado y se cuenta cuántas veces votó distinto. Solo se incluyen los que participaron en al menos el 70% de las votaciones.</p>
  <ol class="rank">{TOP_DIS}</ol>
  <p class="intro" style="margin-top:20px">{perfectos} diputados no se corrieron nunca. El promedio del cuerpo es {100*sum(p["dis"] for p in con)/max(1,sum(p["vot"] for p in con)):.1f}%.</p>
</div></section>

<div class="metodo"><div class="wrap">
  <h2>Método</h2>
  <p>Se leyeron las actas de votación nominal publicadas en el apéndice de los diarios de sesiones del período 144. Cada acta trae el voto de cada diputado, con nombre, bloque y distrito. Se usaron las {meta["actas"]} votaciones donde el resultado no fue unánime.</p>
  <p>Cada voto se codificó como +1 afirmativo, −1 negativo, 0 abstención. Los ausentes no entran. Se centró cada votación y se calculó el primer componente principal de la matriz de diputados por votaciones. Ese componente explica el {meta["pc1"]:.1f}% de la varianza total; el segundo, apenas el {meta["pc2"]:.1f}%. En la práctica hay un solo eje de conflicto.</p>
  <p>El eje separa oficialismo de oposición. Mide comportamiento legislativo, no convicciones: dos diputados pueden votar igual por razones opuestas. La posición no dice si un voto fue acertado, solo con quién se alineó.</p>
  <p>Fuente: Honorable Cámara de Diputados de la Nación, diarios de sesiones, período 144.</p>
</div></div>

<footer><div class="wrap">Corvus Lab · datos abiertos del Congreso</div></footer>
</body>
</html>
"""

open(OUT, "w", encoding="utf-8").write(HTML)
print(f"OK mapa.html · {len(HTML):,} bytes · {meta['dips']} diputados · {meta['actas']} actas")
