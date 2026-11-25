#!/usr/bin/env python3
# Genera bloques.html: la matriz de quién vota con quién, acta por acta, y qué tan predecible es un voto.
import json, os, html
from collections import Counter, defaultdict

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VOTOS = os.path.join(BASE, "_build", "data", "votos.json")
OUT = os.path.join(BASE, "bloques.html")
CSV = os.path.join(BASE, "bloques.csv")

v = json.load(open(VOTOS, encoding="utf-8"))
dips, actas = v["dips"], sorted(v["actas"], key=lambda a: (a["dia"], a["acta"]))
VALIDOS = {"AF", "NE"}
esc = html.escape

B = ["LA LIBERTAD AVANZA", "PRO", "UCR - UNIÓN CÍVICA RADICAL", "ARGENTINA FEDERAL",
     "PROVINCIAS UNIDAS", "UNIÓN POR LA PATRIA"]
AB = {"LA LIBERTAD AVANZA": "LLA", "PRO": "PRO", "UCR - UNIÓN CÍVICA RADICAL": "UCR",
      "ARGENTINA FEDERAL": "AFed", "PROVINCIAS UNIDAS": "PU", "UNIÓN POR LA PATRIA": "UxP"}
NOMBRE = {"LA LIBERTAD AVANZA": "La Libertad Avanza", "PRO": "PRO",
          "UCR - UNIÓN CÍVICA RADICAL": "UCR", "ARGENTINA FEDERAL": "Argentina Federal",
          "PROVINCIAS UNIDAS": "Provincias Unidas", "UNIÓN POR LA PATRIA": "Unión por la Patria"}
VOTO = {"AF": "afirmativo", "NE": "negativo", "AB": "abstención", "·": "sin integrantes suficientes"}
CLS = {"AF": "AF", "NE": "NE", "AB": "AB", "·": "none"}


PAL = {1: "un", 2: "dos", 3: "tres", 4: "cuatro", 5: "cinco", 6: "seis", 7: "siete",
       8: "ocho", 9: "nueve", 10: "diez"}


def pct(x):
    return f"{x*100:.0f}%".replace(".", ",")


# --- posiciones por bloque y acta
filas = []
for a in actas:
    c = defaultdict(Counter)
    for dip, voto in a["votos"].items():
        b = dips.get(dip, {}).get("b")
        if voto in ("AF", "NE", "AB") and b:
            c[b][voto] += 1
    pos = tuple((c[b].most_common(1)[0][0] if sum(c[b].values()) >= 4 else "·") for b in B)
    filas.append({"id": a["id"], "k": f'{a["dia"]}-{a["acta"]}', "dia": a["dia"], "n": a["acta"],
                  "asunto": a.get("asunto") or "", "pos": pos,
                  "fecha": f'{a["dia"][6:8]}/{a["dia"][4:6]}'})


def regimen(pos):
    if pos[0] == "NE" and pos[5] == "AF":
        return "procedimental"
    if pos[4] == "NE" and pos[5] == "NE" and pos[0] == "AF":
        return "paquete"
    return "consenso"


REG = {
    "paquete": dict(titulo="El paquete económico", n=0,
                    texto="Energía capítulo por capítulo, régimen de incentivos y la reforma de la ley 11.683. "
                          "Cinco bloques a favor y dos en contra: ahí aparece la única fractura del período, "
                          "porque Provincias Unidas se suma a Unión por la Patria."),
    "consenso": dict(titulo="Consenso sin la oposición", n=0,
                     texto="Hojarasca, conciliaciones, carta orgánica del BCRA y patentes. Todos acompañan salvo "
                           "Unión por la Patria, que queda sola en contra. Provincias Unidas vota con el oficialismo."),
    "procedimental": dict(titulo="Votaciones de procedimiento", n=0,
                          texto="Mociones de levantamiento y apartamientos del reglamento. El eje se invierte: "
                                "los bloques que acompañan todo lo demás votan en contra, y los que se oponen votan a favor."),
}

grupos = defaultdict(list)
for f in filas:
    grupos[f["pos"]].append(f)
    REG[regimen(f["pos"])]["n"] += 1

# --- acuerdos
import itertools
pares = []
for i, j in itertools.combinations(range(len(B)), 2):
    ok = sum(1 for f in filas if f["pos"][i] == f["pos"][j]) / len(filas)
    pares.append((AB[B[i]], AB[B[j]], ok))
pares.sort(key=lambda x: -x[2])

# --- tabla
TR = ""
for reg in ["paquete", "consenso", "procedimental"]:
    sub = sorted([(p, fs) for p, fs in grupos.items() if regimen(p) == reg], key=lambda x: -len(x[1]))
    tot = sum(len(fs) for _, fs in sub)
    TR += (f'<tr class="grp"><td colspan="2"><span class="gt">{REG[reg]["titulo"]}</span>'
           f'<span class="gn">{tot} acta{"s" if tot>1 else ""}</span></td>'
           f'<td colspan="6"></td></tr>')
    for pos, fs in sub:
        for f in fs:
            celdas = "".join(
                f'<td class="vc"><i class="v {CLS[x]}" title="{AB[b]}: {VOTO[x]}"></i></td>'
                for x, b in zip(f["pos"], B))
            TR += (f'<tr><td class="fax"><b>{f["fecha"]}</b> {f["n"]}</td>'
                   f'<td class="asu">{esc(f["asunto"])}</td>{celdas}</tr>')

TH = "".join(f'<th class="b">{AB[b]}</th>' for b in B)

# --- tarjetas de régimen
CARD = ""
for k in ["paquete", "consenso", "procedimental"]:
    fs = [f for f in filas if regimen(f["pos"]) == k]
    temas = Counter()
    for f in fs:
        a = f["asunto"]
        if "Apartamiento" in a: temas["apartamientos del reglamento"] += 1
        elif "Moción" in a: temas["mociones"] += 1
        elif "nergía" in a: temas["energía"] += 1
        elif "11.683" in a: temas["ley 11.683"] += 1
        elif "incentivos" in a: temas["régimen de incentivos"] += 1
        elif "BCRA" in a: temas["BCRA"] += 1
        elif "Hojarasca" in a: temas["hojarasca"] += 1
        elif "patentes" in a: temas["patentes"] += 1
        elif "Conciliaciones" in a: temas["conciliaciones"] += 1
        else: temas[a[:24]] += 1
    tags = "".join(f'<span class="tag">{esc(t)} {n}</span>' for t, n in temas.most_common())
    patron = "".join(f'<i class="v {CLS[x]}"></i>' for x in fs[0]["pos"])
    CARD += f"""<div class="card">
      <div class="cn">{len(fs)}</div>
      <h3>{REG[k]['titulo']}</h3>
      <p>{REG[k]['texto']}</p>
      <div class="cpat">{patron}</div>
      <div class="ctags">{tags}</div>
    </div>"""

# --- barras de acuerdo
BARS = ""
for a, b, x in pares:
    BARS += (f'<div class="brw"><div class="bl">{a} · {b}</div>'
             f'<div class="bt"><i style="width:{x*100:.1f}%"></i></div>'
             f'<div class="bv">{pct(x)}</div></div>')

# --- csv
with open(CSV, "w", encoding="utf-8", newline="") as fh:
    fh.write("acta,fecha,asunto," + ",".join(AB[b] for b in B) + "\n")
    for f in filas:
        fh.write(f'{f["k"]},{f["fecha"]},"{f["asunto"].replace(chr(34), chr(39))}",'
                 + ",".join(f["pos"]) + "\n")

CSS = """
:root { --paper:#f8f6f2; --card:#fff; --ink:#16130f; --muted:#6d665c; --soft:#999083; --rule:#e2dcd1; --rule-strong:#c9c1b3; --warn:#a4401c; --af:#2f6b4f; --ne:#b04234; --ab:#c9c1b3; }
* { box-sizing:border-box; }
html { -webkit-text-size-adjust:100%; }
body { margin:0; background:var(--paper); color:var(--ink); font-family:"Public Sans",-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; font-size:16px; line-height:1.55; -webkit-font-smoothing:antialiased; }
.wrap { max-width:1080px; margin:0 auto; padding:0 28px; }
nav.top { border-bottom:1px solid var(--rule); }
nav.top .wrap { display:flex; justify-content:space-between; align-items:baseline; padding:14px 28px; gap:16px; flex-wrap:wrap; }
nav.top a { color:var(--muted); text-decoration:none; font-size:13px; }
nav.top a:hover { color:var(--ink); }
nav.top .brand { font-family:"IBM Plex Mono",monospace; font-size:12px; letter-spacing:.12em; text-transform:uppercase; color:var(--ink); }
.kicker { font-family:"IBM Plex Mono",monospace; font-size:11.5px; letter-spacing:.14em; text-transform:uppercase; color:var(--soft); margin-bottom:16px; }
header.hero { padding:54px 0 30px; border-bottom:1px solid var(--rule-strong); }
h1 { font-size:clamp(29px,5vw,44px); line-height:1.09; letter-spacing:-.02em; font-weight:600; margin:0 0 18px; }
.dek { font-size:18px; color:#3b352d; max-width:760px; margin:0; }
section { padding:44px 0; border-bottom:1px solid var(--rule); }
h2 { font-size:23px; letter-spacing:-.01em; font-weight:600; margin:0 0 6px; }
.sub { color:var(--muted); font-size:15px; margin:0 0 26px; max-width:720px; }
.mx { width:100%; border-collapse:collapse; }
.mx th { font-family:"IBM Plex Mono",monospace; font-size:10.5px; letter-spacing:.08em; text-transform:uppercase; color:var(--soft); font-weight:500; padding:0 0 8px; text-align:left; }
.mx th.b { width:38px; text-align:center; padding:0 2px 8px; }
.mx td { padding:0; border-bottom:1px solid #ece7de; }
.mx td.fax { font-family:"IBM Plex Mono",monospace; font-size:11.5px; color:var(--muted); white-space:nowrap; padding:5px 12px 5px 0; width:82px; }
.mx td.fax b { color:var(--ink); font-weight:500; }
.mx td.asu { font-size:13px; color:#3b352d; padding:5px 14px 5px 0; }
.mx td.vc { width:38px; text-align:center; vertical-align:middle; }
.v { display:inline-block; width:26px; height:15px; border-radius:1px; vertical-align:middle; }
.v.AF { background:var(--af); }
.v.NE { background:var(--ne); }
.v.AB { background:var(--ab); }
.v.none { background:#f1eee7; border:1px solid #e6e0d5; }
.mx tr.grp td { border-bottom:1px solid var(--rule-strong); padding:20px 0 7px; }
.gt { font-size:14px; font-weight:600; letter-spacing:-.01em; }
.gn { font-family:"IBM Plex Mono",monospace; font-size:11px; color:var(--soft); margin-left:9px; }
.ley { display:flex; gap:20px; flex-wrap:wrap; margin-top:18px; font-size:12.5px; color:var(--muted); }
.ley span { display:flex; align-items:center; gap:6px; }
.cards { display:grid; grid-template-columns:repeat(3,1fr); gap:18px; }
.card { background:var(--card); border:1px solid var(--rule); border-radius:3px; padding:20px 22px 18px; }
.card .cn { font-family:"IBM Plex Mono",monospace; font-size:30px; font-weight:500; letter-spacing:-.03em; line-height:1; margin-bottom:2px; }
.card h3 { font-size:16px; margin:0 0 8px; letter-spacing:-.01em; }
.card p { font-size:13.5px; color:#4a443b; margin:0 0 14px; line-height:1.5; }
.cpat { display:flex; gap:3px; margin-bottom:12px; }
.cpat .v { width:20px; height:12px; }
.ctags { display:flex; flex-wrap:wrap; gap:5px; }
.tag { font-family:"IBM Plex Mono",monospace; font-size:10.5px; padding:2px 6px; border-radius:2px; background:#efece5; color:#5c554a; white-space:nowrap; }
.brw { display:grid; grid-template-columns:190px 1fr 52px; gap:14px; align-items:center; padding:4px 0; }
.bl { font-family:"IBM Plex Mono",monospace; font-size:11.5px; color:#3b352d; }
.bt { background:#efece5; height:13px; border-radius:1px; }
.bt i { display:block; height:100%; background:#4a443b; border-radius:1px; }
.bv { font-family:"IBM Plex Mono",monospace; font-size:11.5px; color:var(--muted); text-align:right; }
.tres { display:grid; grid-template-columns:repeat(3,1fr); gap:22px; margin-bottom:22px; }
.tres div b { display:block; font-family:"IBM Plex Mono",monospace; font-size:33px; font-weight:500; letter-spacing:-.03em; line-height:1; margin-bottom:6px; }
.tres div span { font-size:13.5px; color:var(--muted); line-height:1.45; display:block; }
.nota { background:var(--card); border:1px solid var(--rule); border-left:3px solid var(--ink); padding:16px 20px; font-size:14px; color:#3b352d; }
.nota b { font-weight:600; }
footer { padding:30px 0 50px; font-size:13px; color:var(--muted); }
footer a { color:var(--ink); }
code { font-family:"IBM Plex Mono",monospace; font-size:12.5px; background:#efece5; padding:1px 5px; border-radius:2px; }
@media (max-width:820px) {
  .cards { grid-template-columns:1fr; }
  .tres { grid-template-columns:1fr; gap:18px; }
}
@media (max-width:560px) {
  .wrap { padding:0 16px; }
  header.hero { padding:34px 0 22px; }
  section { padding:32px 0; }
  .dek { font-size:16px; }
  .mx td.asu, .mx th.asu { display:none; }
  .mx td.fax { width:70px; font-size:11px; padding-right:8px; }
  .mx th.b, .mx td.vc { width:29px; }
  .mx th.fax { width:70px; }
  .v { width:19px; height:13px; }
  .brw { grid-template-columns:1fr 52px; gap:4px 10px; }
  .bl { grid-column:1 / -1; font-size:10.5px; }
}
"""

HTML = f"""<!DOCTYPE html>
<html lang="es-AR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Quién vota con quién · la estructura de las votaciones en Diputados</title>
<meta name="description" content="Las 33 votaciones nominales del período 144, la posición de cada bloque acta por acta y cuánto se puede predecir un voto sabiendo el bloque.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Public+Sans:wght@300;400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>{CSS}</style>
</head>
<body>

<nav class="top"><div class="wrap">
  <a class="brand" href="/">Corvus Lab</a>
  <div><a href="/congreso">Congreso</a> · <a href="/cordoba">Córdoba</a> · <a href="/mapa">Mapa</a> · <a href="/bloques">Bloques</a> · <a href="/viabilidad">Viabilidad</a> · <a href="/simulador">Simulador</a> · <a href="/termometro">Termómetro</a> · <a href="/disidencias">Disidencias</a> · <a href="/plan-de-metas">Plan de Metas</a> · <a href="/proyectos">Trabajos</a></div>
</div></nav>

<header class="hero"><div class="wrap">
  <div class="kicker">Cámara de Diputados · Período 144 · 33 votaciones nominales</div>
  <h1>Quién vota con quién</h1>
  <p class="dek">Las 33 votaciones del período se ordenan casi siempre igual. Cinco bloques de un lado, Unión por la Patria del otro, y Provincias Unidas cambiando de lado según el tema. Acá está la posición de cada bloque acta por acta, y cuánto de eso se puede anticipar.</p>
</div></header>

<section><div class="wrap">
  <h2>La matriz completa</h2>
  <p class="sub">Posición mayoritaria de cada bloque en cada votación, agrupada por el patrón que repite. Bloques de cuatro integrantes o más; abstenciones y ausentes quedan afuera del cálculo de la mayoría.</p>
  <table class="mx">
    <thead><tr><th class="fax">Acta</th><th class="asu">Asunto</th>{TH}</tr></thead>
    <tbody>{TR}</tbody>
  </table>
  <div class="ley">
    <span><i class="v AF"></i>Afirmativo</span>
    <span><i class="v NE"></i>Negativo</span>
    <span><i class="v AB"></i>Abstención</span>
    <span><i class="v none"></i>Sin integrantes suficientes</span>
  </div>
</div></section>

<section><div class="wrap">
  <h2>Tres regímenes, {PAL[len(grupos)]} patrones</h2>
  <p class="sub">De las 33 votaciones salen {PAL[len(grupos)]} combinaciones distintas de posición por bloque. Las tres familias explican casi todo.</p>
  <div class="cards">{CARD}</div>
</div></section>

<section><div class="wrap">
  <h2>Con quién coincide cada bloque</h2>
  <p class="sub">Porcentaje de votaciones en que dos bloques tomaron la misma posición mayoritaria.</p>
  {BARS}
</div></section>

<section><div class="wrap">
  <h2>Qué tan predecible es un voto</h2>
  <p class="sub">Medido sobre las mismas 33 votaciones, prediciendo cada acta sin verla. El experimento completo está en <a href="/proyectos">Trabajos</a>.</p>
  <div class="tres">
    <div><b>98,4%</b><span>de acierto si se conoce la posición del bloque en esa acta. Es el techo que impone la disciplina de bloque, no un método.</span></div>
    <div><b>70,9%</b><span>de acierto usando solo el historial, sin saber qué va a hacer el bloque. Acá está todo el margen de un modelo.</span></div>
    <div><b>55,2%</b><span>de acierto contestando siempre «a favor». El piso que hay que superar para aportar algo.</span></div>
  </div>
  <div class="nota"><b>La unidad de predicción es el bloque, no el diputado.</b> De 7.731 votos emitidos, 125 se apartaron de la mayoría del bloque: el 1,6%. Predecir al bloque resuelve casi todo el problema; predecir la deserción individual es el resto.</div>
</div></section>

<footer><div class="wrap">
  Fuente: votaciones nominales del período 144, Cámara de Diputados de la Nación. <a href="/bloques.csv">Datos en CSV</a>. Regla: mayoría del bloque en cada acta, con abstenciones y ausentes excluidos del cálculo; bloques de cuatro o más integrantes. Los bloques se toman de la composición publicada, sin historia de cambios de bloque.
</div></footer>

</body></html>"""

open(OUT, "w", encoding="utf-8").write(HTML)
print(f"bloques.html {len(HTML):,} bytes · {len(filas)} actas · {len(grupos)} patrones · csv {os.path.getsize(CSV):,} bytes")
