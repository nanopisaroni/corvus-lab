#!/usr/bin/env python3
# Genera viabilidad.html: calculadora de coalición y aritmética real de las 33 votaciones.
import json, os, html
from collections import Counter

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VOTOS = os.path.join(BASE, "_build", "data", "votos.json")
OUT = os.path.join(BASE, "viabilidad.html")
esc = html.escape

v = json.load(open(VOTOS, encoding="utf-8"))
dips, actas = v["dips"], sorted(v["actas"], key=lambda a: (a["dia"], a["acta"]))
tam = Counter(d["b"] for d in dips.values())

GRANDES = ["LA LIBERTAD AVANZA", "UNIÓN POR LA PATRIA", "PROVINCIAS UNIDAS", "PRO",
           "ARGENTINA FEDERAL", "UCR - UNIÓN CÍVICA RADICAL"]
AB = {"LA LIBERTAD AVANZA": "LLA", "UNIÓN POR LA PATRIA": "UxP", "PROVINCIAS UNIDAS": "PU",
      "PRO": "PRO", "ARGENTINA FEDERAL": "AFed", "UCR - UNIÓN CÍVICA RADICAL": "UCR"}
chicos = sum(n for b, n in tam.items() if b not in GRANDES)
TOTAL = sum(tam.values())


def pctf(x):
    return f"{x:.1f}%".replace(".", ",")


# --- tabla de las 33 votaciones
TR = ""
for a in actas:
    af = sum(1 for x in a["votos"].values() if x == "AF")
    ne = sum(1 for x in a["votos"].values() if x == "NE")
    ab = sum(1 for x in a["votos"].values() if x == "AB")
    pres = af + ne + ab
    nec = pres // 2 + 1
    sobra = af - nec
    clase = "pasa" if sobra >= 0 else "cae"
    TR += (f'<tr><td class="fx"><b>{a["dia"][6:8]}/{a["dia"][4:6]}</b> {a["acta"]}</td>'
           f'<td class="asu">{esc(a["asunto"])}</td>'
           f'<td class="n">{af}</td><td class="n ne">{ne}</td><td class="n ab">{ab}</td>'
           f'<td class="n">{pres}</td><td class="n">{nec}</td>'
           f'<td class="n {clase}">{sobra:+d}</td></tr>')

FILAS_33 = len(actas)
caidas = sum(1 for a in actas
             if sum(1 for x in a["votos"].values() if x == "AF") < (sum(1 for x in a["votos"].values() if x in ("AF", "NE", "AB")) // 2 + 1))

# --- opciones del simulador
OPS = ""
for b in GRANDES:
    OPS += (f'<label class="op"><input type="checkbox" data-s="{tam[b]}" data-b="{AB[b]}" '
            f'value="{AB[b]}"><span class="nm">{AB[b]}</span><span class="sd">{tam[b]}</span></label>')
OPS += (f'<label class="op"><input type="checkbox" data-s="{chicos}" data-b="Chicos" '
        f'value="Chicos"><span class="nm">Bloques de 1 y 2</span><span class="sd">{chicos}</span></label>')

SEATS = json.dumps({AB[b]: tam[b] for b in GRANDES} | {"Chicos": chicos})

CSS = """
:root { --paper:#f8f6f2; --card:#fff; --ink:#16130f; --muted:#6d665c; --soft:#999083; --rule:#e2dcd1; --rule-strong:#c9c1b3; --ok:#2f6b4f; --no:#b04234; }
* { box-sizing:border-box; }
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
.sim { display:grid; grid-template-columns:1fr 330px; gap:26px; align-items:start; }
.ops { display:grid; grid-template-columns:1fr 1fr; gap:2px 18px; }
.op { display:grid; grid-template-columns:22px 1fr 42px; align-items:center; gap:8px; padding:5px 0; border-bottom:1px solid #ece7de; cursor:pointer; }
.op input { width:15px; height:15px; accent-color:#16130f; margin:0; }
.nm { font-size:14px; }
.sd { font-family:"IBM Plex Mono",monospace; font-size:11.5px; color:var(--soft); text-align:right; }
.panel { background:var(--card); border:1px solid var(--rule); border-radius:3px; padding:20px 22px; position:sticky; top:16px; }
.panel .big { font-family:"IBM Plex Mono",monospace; font-size:40px; font-weight:500; letter-spacing:-.03em; line-height:1; }
.panel .lab { font-family:"IBM Plex Mono",monospace; font-size:10.5px; letter-spacing:.1em; text-transform:uppercase; color:var(--soft); }
.res { font-size:17px; font-weight:600; margin:10px 0 2px; }
.res.ok { color:var(--ok); }
.res.no { color:var(--no); }
.det { font-size:13px; color:#4a443b; margin:10px 0 0; line-height:1.5; }
.pres { display:flex; align-items:center; gap:10px; margin-top:16px; padding-top:14px; border-top:1px solid var(--rule); font-size:13px; color:var(--muted); }
.pres input[type=range] { flex:1; accent-color:#16130f; }
.pres b { font-family:"IBM Plex Mono",monospace; font-size:13px; color:var(--ink); min-width:34px; text-align:right; }
.pret { display:flex; gap:8px; flex-wrap:wrap; margin-bottom:18px; }
.pret button { font-family:inherit; font-size:12px; padding:5px 10px; border:1px solid var(--rule-strong); background:transparent; border-radius:2px; cursor:pointer; color:#4a443b; }
.pret button:hover { background:#efece5; color:var(--ink); }
table { width:100%; border-collapse:collapse; }
th { text-align:left; font-family:"IBM Plex Mono",monospace; font-size:10px; letter-spacing:.07em; text-transform:uppercase; color:var(--soft); font-weight:500; padding:0 6px 8px 0; border-bottom:1px solid var(--rule-strong); }
th.n { text-align:right; }
td { border-bottom:1px solid #ece7de; padding:5px 6px 5px 0; font-size:13px; }
td.fx { font-family:"IBM Plex Mono",monospace; font-size:11px; color:var(--muted); white-space:nowrap; width:74px; }
td.fx b { color:var(--ink); font-weight:500; }
td.n { text-align:right; font-family:"IBM Plex Mono",monospace; font-size:12px; width:44px; }
td.ne { color:var(--no); }
td.ab { color:var(--soft); }
td.pasa { color:var(--ok); font-weight:500; }
td.cae { color:var(--no); font-weight:500; }
.cards { display:grid; grid-template-columns:repeat(3,1fr); gap:18px; }
.card { background:var(--card); border:1px solid var(--rule); border-radius:3px; padding:18px 20px; }
.card b { display:block; font-family:"IBM Plex Mono",monospace; font-size:26px; font-weight:500; letter-spacing:-.02em; }
.card span { font-size:13px; color:var(--muted); display:block; margin-top:2px; }
.card em { font-style:normal; font-size:12.5px; color:#4a443b; display:block; margin-top:8px; }
.nota { background:var(--card); border:1px solid var(--rule); border-left:3px solid var(--ink); padding:16px 20px; font-size:14px; color:#3b352d; margin-top:22px; }
footer { padding:30px 0 50px; font-size:13px; color:var(--muted); }
footer a { color:var(--ink); }
@media (max-width:860px) { .sim { grid-template-columns:1fr; } .panel { position:static; } .cards { grid-template-columns:1fr; } }
@media (max-width:560px) {
  .wrap { padding:0 16px; }
  header.hero { padding:34px 0 22px; }
  section { padding:32px 0; }
  .dek { font-size:16px; }
  .ops { grid-template-columns:1fr; }
  td.asu, th.asu { display:none; }
  td.n { width:36px; font-size:11.5px; }
  th { font-size:9px; }
}
"""

JS = """
const SEATS = """ + SEATS + """;
const ops = [...document.querySelectorAll('.op input')];
const rng = document.getElementById('pres');
const outAF = document.getElementById('af');
const outPres = document.getElementById('presv');
const res = document.getElementById('res');
const det = document.getElementById('det');
function calc() {
  const presentes = +rng.value;
  let af = 0, elegidos = [];
  ops.forEach(o => { if (o.checked) { af += +o.dataset.s; elegidos.push(o.dataset.b); } });
  af = Math.min(af, presentes);
  const ne = presentes - af;
  const nec = Math.floor(presentes / 2) + 1;
  const sobra = af - nec;
  outAF.textContent = af;
  outPres.textContent = presentes;
  if (af === 0) { res.textContent = 'Sin bloques elegidos'; res.className = 'res'; det.textContent = 'Marcá los bloques que acompañan el proyecto.'; return; }
  if (sobra >= 0) {
    res.textContent = 'Se aprueba';
    res.className = 'res ok';
    det.textContent = 'Con ' + af + ' votos a favor sobre ' + presentes + ' presentes alcanza: el mínimo es ' + nec + '. Puede perder ' + sobra + ' voto(s) y todavía pasa.';
  } else {
    res.textContent = 'No se aprueba';
    res.className = 'res no';
    det.textContent = 'Con ' + af + ' votos a favor sobre ' + presentes + ' presentes no alcanza: necesita ' + nec + ', le faltan ' + (-sobra) + '.';
  }
}
ops.forEach(o => o.addEventListener('change', calc));
rng.addEventListener('input', calc);
document.querySelectorAll('.pret button').forEach(b => b.addEventListener('click', () => {
  const set = b.dataset.set.split(',');
  ops.forEach(o => o.checked = set.includes(o.dataset.b));
  calc();
}));
calc();
"""

HTML = f"""<!DOCTYPE html>
<html lang="es-AR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>¿Puede aprobarse? · calculadora de coalición en Diputados</title>
<meta name="description" content="Qué combinación de bloques alcanza para aprobar una ley en la Cámara de Diputados, con la aritmética real de las 33 votaciones del período 144.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Public+Sans:wght@300;400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>{CSS}</style>
</head>
<body>

<nav class="top"><div class="wrap">
  <a class="brand" href="/">Corvus Lab</a>
  <div><a href="/congreso">Congreso</a> · <a href="/bloques">Bloques</a> · <a href="/viabilidad">Viabilidad</a> · <a href="/disidencias">Disidencias</a> · <a href="/cordoba">Córdoba</a> · <a href="/mapa">Mapa</a> · <a href="/plan-de-metas">Plan de Metas</a> · <a href="/proyectos">Trabajos</a></div>
</div></nav>

<header class="hero"><div class="wrap">
  <div class="kicker">Cámara de Diputados · Período 144 · {TOTAL} bancas</div>
  <h1>¿Puede aprobarse?</h1>
  <p class="dek">El oficialismo tiene {tam['LA LIBERTAD AVANZA'] + tam['PRO'] + tam['UCR - UNIÓN CÍVICA RADICAL'] + tam['ARGENTINA FEDERAL']} bancas propias sobre {TOTAL}. Cada ley del período se aprobó con entre 6 y 23 votos prestados, y el mínimo para aprobar se movió entre 112 y 126 según cuántos se sentaron. Marcá qué bloques acompañan un proyecto y mirá si alcanza.</p>
</div></header>

<section><div class="wrap">
  <h2>La calculadora</h2>
  <p class="sub">Sumá los bloques que votarían a favor. El mínimo para aprobar es la mitad más uno de los presentes.</p>
  <div class="pret">
    <button data-set="LLA,PRO,UCR,AFed">Núcleo oficialista · 122</button>
    <button data-set="LLA,PRO,UCR,AFed,PU">Con PU · 140</button>
    <button data-set="UxP,PU,AFed,Chicos">UxP, PU y chicos · 143</button>
    <button data-set="">Limpiar</button>
  </div>
  <div class="sim">
    <div class="ops">{OPS}</div>
    <div class="panel">
      <div class="lab">Votos a favor</div>
      <div class="big" id="af">0</div>
      <div class="res" id="res">Sin bloques elegidos</div>
      <p class="det" id="det">Marcá los bloques que acompañan el proyecto.</p>
      <div class="pres">
        <label for="pres">Presentes</label>
        <input type="range" id="pres" min="150" max="{TOTAL}" value="235" step="1">
        <b id="presv">235</b>
      </div>
    </div>
  </div>
  <div class="nota"><b>La asistencia pesa tanto como los votos.</b> En las 33 votaciones se sentaron entre 223 y 250 diputados, así que el mínimo exigido se movió entre 112 y 126. El régimen de incentivos se aprobó con 128 a favor: si ese día hubieran estado 250 en el recinto, el mínimo hubiera sido 126 y la ley pasaba por dos votos. <b>Por qué PU aparece en todo:</b> Provincias Unidas tiene {tam['PROVINCIAS UNIDAS']} bancas y está en las dos mayorías posibles, la de {tam['LA LIBERTAD AVANZA'] + tam['PRO'] + tam['UCR - UNIÓN CÍVICA RADICAL'] + tam['ARGENTINA FEDERAL'] + tam['PROVINCIAS UNIDAS']} con el oficialismo y la de {tam['UNIÓN POR LA PATRIA'] + tam['PROVINCIAS UNIDAS'] + tam['ARGENTINA FEDERAL'] + chicos} con UxP y los bloques chicos.</div>
</div></section>

<section><div class="wrap">
  <h2>Lo que pasó en las 33 votaciones</h2>
  <p class="sub">Votos afirmativos, negativos y abstenciones registrados, con el mínimo que exigía cada votación y cuántos votos sobraron o faltaron.</p>
  <table>
    <thead><tr><th>Acta</th><th class="asu">Asunto</th><th class="n">AF</th><th class="n">NE</th><th class="n">AB</th><th class="n">Pres.</th><th class="n">Mín.</th><th class="n">Sobra</th></tr></thead>
    <tbody>{TR}</tbody>
  </table>
</div></section>

<section><div class="wrap">
  <h2>Los tres escenarios reales</h2>
  <p class="sub">Cada familia de votaciones se aprobó con una coalición distinta y con márgenes distintos.</p>
  <div class="cards">
    <div class="card"><b>+9</b><span>Régimen de incentivos</span><em>128 a favor sobre 237 presentes, mínimo 119. Sobraron 9: diez diputados cambiando de lado la tumbaban.</em></div>
    <div class="card"><b>+11</b><span>Ley de energía</span><em>129 a favor sobre 234 presentes, con Provincias Unidas y los bloques chicos aportando la diferencia.</em></div>
    <div class="card"><b>+27</b><span>Tratado de patentes</span><em>145 a favor sobre 235 presentes. El margen más amplio de todo el período.</em></div>
  </div>
</div></section>

<footer><div class="wrap">
  Fuente: {FILAS_33} votaciones nominales del período 144, Cámara de Diputados de la Nación. El mínimo se calcula como la mitad más uno de los presentes, con las abstenciones contando como presentes, que es como se resolvieron estas votaciones. No incluye el Senado, que tiene su propia aritmética. La calculadora no predice: cuenta.
</div></footer>

<script>{JS}</script>
</body></html>"""

open(OUT, "w", encoding="utf-8").write(HTML)
print(f"viabilidad.html {len(HTML):,} bytes · {FILAS_33} votaciones · caídas {caidas} · chicos {chicos}")
