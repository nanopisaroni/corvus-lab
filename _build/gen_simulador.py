#!/usr/bin/env python3
# Genera simulador.html: simulación de apoyo por bloque para un proyecto en preparación.
import json, os, html
from collections import Counter, defaultdict

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VOTOS = os.path.join(BASE, "_build", "data", "votos.json")
OUT = os.path.join(BASE, "simulador.html")
esc = html.escape

v = json.load(open(VOTOS, encoding="utf-8"))
dips, actas = v["dips"], sorted(v["actas"], key=lambda a: (a["dia"], a["acta"]))
VALIDOS = {"AF", "NE"}

B = ["LA LIBERTAD AVANZA", "PRO", "UCR - UNIÓN CÍVICA RADICAL", "ARGENTINA FEDERAL",
     "PROVINCIAS UNIDAS", "UNIÓN POR LA PATRIA"]
AB = {"LA LIBERTAD AVANZA": "LLA", "PRO": "PRO", "UCR - UNIÓN CÍVICA RADICAL": "UCR",
      "ARGENTINA FEDERAL": "AFed", "PROVINCIAS UNIDAS": "PU", "UNIÓN POR LA PATRIA": "UxP"}
NOMBRE = {"LA LIBERTAD AVANZA": "La Libertad Avanza", "PRO": "PRO",
          "UCR - UNIÓN CÍVICA RADICAL": "UCR", "ARGENTINA FEDERAL": "Argentina Federal",
          "PROVINCIAS UNIDAS": "Provincias Unidas", "UNIÓN POR LA PATRIA": "Unión por la Patria"}
tam = Counter(d["b"] for d in dips.values())

DIMS = [
    ("energia", "Energía y tarifas", "Precio de la energía, subsidios, zona fría, hidrocarburos."),
    ("rigi", "Régimen de incentivos a la inversión", "Beneficios impositivos y aduaneros para grandes inversiones."),
    ("fiscal", "Impuestos", "Modificación de la ley 11.683, procedimiento tributario."),
    ("bcra", "Reglas del Banco Central", "Carta orgánica, instrumentos de política monetaria."),
    ("tratados", "Tratados internacionales", "Acuerdos con otros países, propiedad intelectual."),
    ("desregulacion", "Derogación de normas", "Eliminación de regulaciones y normas obsoletas."),
    ("conciliaciones", "Conciliaciones y acuerdos", "Homologación de acuerdos entre privados."),
    ("procedimiento", "Cuestiones de procedimiento", "Mociones, apartamientos del reglamento, cuestión previa."),
]

DIM_DE = {}
for k, _, _ in DIMS:
    DIM_DE[k] = k


def dim(s):
    s = (s or "").lower()
    if "energ" in s: return "energia"
    if "incentivos" in s: return "rigi"
    if "11.683" in s: return "fiscal"
    if "bcra" in s: return "bcra"
    if "hojarasca" in s: return "desregulacion"
    if "patentes" in s: return "tratados"
    if "conciliaciones" in s: return "conciliaciones"
    return "procedimiento"


# --- registro por dimensión y bloque
reg = defaultdict(lambda: defaultdict(Counter))
actas_de = defaultdict(list)
for a in actas:
    k = dim(a["asunto"])
    actas_de[k].append(a)
    c = defaultdict(Counter)
    for dip, voto in a["votos"].items():
        b = dips.get(dip, {}).get("b")
        if voto in VALIDOS and b:
            c[b][voto] += 1
    for b in B:
        if sum(c[b].values()) >= 4:
            reg[k][b][c[b].most_common(1)[0][0]] += 1

REG_JS = {}
for k, _, _ in DIMS:
    REG_JS[k] = {AB[b]: {"AF": reg[k][b]["AF"], "NE": reg[k][b]["NE"]} for b in B}

# --- validación leave-one-out dentro de la dimensión
pos = []
for a in actas:
    c = defaultdict(Counter)
    for dip, voto in a["votos"].items():
        b = dips.get(dip, {}).get("b")
        if voto in VALIDOS and b:
            c[b][voto] += 1
    pos.append({b: (c[b].most_common(1)[0][0] if sum(c[b].values()) >= 4 else None) for b in B})
okv = totv = 0
for i, a in enumerate(actas):
    for b in B:
        hist = Counter()
        for j, x in enumerate(actas):
            if j == i or dim(x["asunto"]) != dim(a["asunto"]):
                continue
            p = pos[j].get(b)
            if p: hist[p] += 1
        if not hist: continue
        pred = hist.most_common(1)[0][0]
        for dip, voto in a["votos"].items():
            if voto in VALIDOS and dips.get(dip, {}).get("b") == b:
                totv += 1
                okv += pred == voto
acierto = okv / totv
AC = f"{acierto*100:.1f}".replace(".", ",")
NTV = f"{totv:,}".replace(",", ".")

# --- matriz visible
MAT = ""
for k, titulo, desc in DIMS:
    celdas = ""
    for b in B:
        af, ne = reg[k][b]["AF"], reg[k][b]["NE"]
        if not af and not ne:
            celdas += '<td class="cel sin"><span>sin dato</span></td>'
            continue
        clase = "af" if af > ne else ("ne" if ne > af else "emp")
        signo = "A favor" if af > ne else ("En contra" if ne > af else "Empate")
        celdas += f'<td class="cel {clase}"><b>{signo}</b><span>{max(af,ne)} de {af+ne}</span></td>'
    MAT += (f'<tr><td class="dm"><b>{esc(titulo)}</b><span>{len(actas_de[k])} acta{"s" if len(actas_de[k])>1 else ""}</span></td>{celdas}</tr>')

TH = "".join(f'<th class="bc">{AB[b]}</th>' for b in B)

OPS = ""
for k, titulo, desc in DIMS:
    n = len(actas_de[k])
    OPS += (f'<label class="op"><input type="checkbox" value="{k}">'
            f'<span class="nm">{esc(titulo)}<em>{esc(desc)}</em></span>'
            f'<span class="sd">{n}</span></label>')

EJEMPLOS = [
    ("Ley de energía", ["energia"], "7 actas"),
    ("Régimen de incentivos", ["rigi"], "4 actas"),
    ("Reforma de la ley 11.683", ["fiscal"], "6 actas"),
    ("Carta Orgánica del BCRA", ["bcra"], "3 actas"),
    ("Tratado de patentes", ["tratados"], "1 acta"),
]

BTNS = "".join(
    f'<button data-set="{",".join(ks)}">{esc(t)}</button>' for t, ks, _ in EJEMPLOS)

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
.sub { color:var(--muted); font-size:15px; margin:0 0 24px; max-width:740px; }
.sim { display:grid; grid-template-columns:1fr 330px; gap:26px; align-items:start; }
.ops { display:grid; grid-template-columns:1fr; gap:0; }
.op { display:grid; grid-template-columns:22px 1fr 32px; align-items:start; gap:9px; padding:9px 0; border-bottom:1px solid #ece7de; cursor:pointer; }
.op input { width:15px; height:15px; accent-color:#16130f; margin:2px 0 0; }
.nm { font-size:14.5px; font-weight:500; line-height:1.3; }
.nm em { display:block; font-style:normal; font-weight:400; font-size:12px; color:var(--muted); margin-top:1px; }
.sd { font-family:"IBM Plex Mono",monospace; font-size:11px; color:var(--soft); text-align:right; }
.panel { background:var(--card); border:1px solid var(--rule); border-radius:3px; padding:20px 22px; position:sticky; top:16px; }
.panel .big { font-family:"IBM Plex Mono",monospace; font-size:38px; font-weight:500; letter-spacing:-.03em; line-height:1; }
.panel .lab { font-family:"IBM Plex Mono",monospace; font-size:10.5px; letter-spacing:.1em; text-transform:uppercase; color:var(--soft); }
.res { font-size:17px; font-weight:600; margin:10px 0 2px; }
.res.ok { color:var(--ok); } .res.no { color:var(--no); }
.det { font-size:13px; color:#4a443b; margin:8px 0 0; line-height:1.5; }
.chips { display:flex; flex-wrap:wrap; gap:5px; margin-top:12px; padding-top:12px; border-top:1px solid var(--rule); }
.chip { font-family:"IBM Plex Mono",monospace; font-size:10.5px; padding:2px 6px; border-radius:2px; }
.chip.af { background:#e3ece6; color:#2f6b4f; } .chip.ne { background:#f5e4e1; color:#b04234; } .chip.sin { background:#efece5; color:#8a8378; }
.pret { display:flex; gap:8px; flex-wrap:wrap; margin-bottom:18px; }
.pret button { font-family:inherit; font-size:12px; padding:5px 10px; border:1px solid var(--rule-strong); background:transparent; border-radius:2px; cursor:pointer; color:#4a443b; }
.pret button:hover { background:#efece5; color:var(--ink); }
table.mx { width:100%; border-collapse:collapse; }
table.mx th { text-align:left; font-family:"IBM Plex Mono",monospace; font-size:9.5px; letter-spacing:.06em; text-transform:uppercase; color:var(--soft); font-weight:500; padding:0 4px 8px; border-bottom:1px solid var(--rule-strong); }
table.mx th.bc { text-align:center; width:70px; }
table.mx td { border-bottom:1px solid #ece7de; padding:6px 4px; }
td.dm { width:230px; }
td.dm b { display:block; font-size:13.5px; font-weight:500; line-height:1.25; }
td.dm span { font-family:"IBM Plex Mono",monospace; font-size:10px; color:var(--soft); }
td.cel { text-align:center; }
td.cel b { display:block; font-size:11px; font-weight:600; }
td.cel span { font-family:"IBM Plex Mono",monospace; font-size:9.5px; color:var(--soft); }
td.cel.af b { color:var(--ok); } td.cel.ne b { color:var(--no); } td.cel.sin b { color:var(--soft); font-weight:400; }
.box { border-left:3px solid #16130f; background:#f4f1ea; padding:14px 18px; font-size:14px; margin:18px 0 0; }
.box b { font-weight:600; }
.tres { display:grid; grid-template-columns:repeat(3,1fr); gap:20px; margin:6px 0 18px; }
.tres div b { display:block; font-family:"IBM Plex Mono",monospace; font-size:30px; font-weight:500; letter-spacing:-.03em; line-height:1; margin-bottom:5px; }
.tres div span { font-size:13px; color:var(--muted); line-height:1.45; display:block; }
footer { padding:30px 0 50px; font-size:13px; color:var(--muted); }
@media (max-width:860px) { .sim { grid-template-columns:1fr; } .panel { position:static; } .tres { grid-template-columns:1fr; gap:14px; } }
@media (max-width:620px) {
  .wrap { padding:0 16px; }
  header.hero { padding:34px 0 22px; }
  section { padding:32px 0; }
  .dek { font-size:16px; }
  table.mx th.bc, table.mx td.cel { width:auto; }
  td.dm { width:120px; }
  td.cel b { font-size:9.5px; }
  td.cel span { font-size:8.5px; }
  table.mx th { font-size:8px; }
}
"""

JS = """
const SEATS = """ + json.dumps({AB[b]: tam[b] for b in B}) + """;
const REG = """ + json.dumps(REG_JS) + """;
const NOMBRE = """ + json.dumps({AB[b]: NOMBRE[b] for b in B}) + """;
const BLOCS = ["LLA","PRO","UCR","AFed","PU","UxP"];

const ops = [...document.querySelectorAll('.op input')];
const rng = document.getElementById('pres');
const rch = document.getElementById('chicos');
const outCh = document.getElementById('chicosv');
const outAF = document.getElementById('af');
const outPres = document.getElementById('presv');
const res = document.getElementById('res');
const det = document.getElementById('det');
const chips = document.getElementById('chips');

function calcular() {
  const sel = ops.filter(o => o.checked).map(o => o.value);
  const presentes = +rng.value;
  const pred = {};
  BLOCS.forEach(b => {
    let af = 0, ne = 0;
    sel.forEach(d => { af += REG[d][b].AF; ne += REG[d][b].NE; });
    pred[b] = (af === 0 && ne === 0) ? '??' : (af > ne ? 'AF' : (ne > af ? 'NE' : '??'));
  });
  let af = 0;
  BLOCS.forEach(b => { if (pred[b] === 'AF') af += SEATS[b]; });
  af += +rch.value;
  outCh.textContent = rch.value;
  af = Math.min(af, presentes);
  const nec = Math.floor(presentes / 2) + 1;
  outAF.textContent = af;
  outPres.textContent = presentes;
  chips.innerHTML = BLOCS.map(b => {
    const c = pred[b] === 'AF' ? 'af' : (pred[b] === 'NE' ? 'ne' : 'sin');
    const t = pred[b] === 'AF' ? 'a favor' : (pred[b] === 'NE' ? 'en contra' : 'sin antecedente');
    return '<span class="chip ' + c + '">' + b + ' · ' + t + '</span>';
  }).join('');
  if (!sel.length) {
    res.textContent = 'Elegí qué toca el proyecto';
    res.className = 'res';
    det.textContent = 'Marcá una o más dimensiones a la izquierda para ver cómo votaría cada bloque.';
    return;
  }
  const sobra = af - nec;
  if (sobra >= 0) {
    res.textContent = 'Se aprueba';
    res.className = 'res ok';
    det.textContent = 'Con ' + af + ' votos sobre ' + presentes + ' presentes. El mínimo es ' + nec + ': aguanta ' + sobra + ' deserción(es).';
  } else {
    res.textContent = 'No se aprueba';
    res.className = 'res no';
    det.textContent = 'Con ' + af + ' votos sobre ' + presentes + ' presentes no alcanza: el mínimo es ' + nec + ' y faltan ' + (-sobra) + '.';
  }
}
ops.forEach(o => o.addEventListener('change', calcular));
rng.addEventListener('input', calcular);
rch.addEventListener('input', calcular);
document.querySelectorAll('.pret button').forEach(b => b.addEventListener('click', () => {
  const set = b.dataset.set ? b.dataset.set.split(',') : [];
  ops.forEach(o => o.checked = set.includes(o.value));
  calcular();
}));
calcular();
"""

HTML = f"""<!DOCTYPE html>
<html lang="es-AR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Simulador de apoyo · qué necesita un proyecto para que lo voten</title>
<meta name="description" content="Simulación de apoyo por bloque para un proyecto en preparación: qué toca, quién lo acompaña y cuántos votos hay que recuperar, sobre el registro real de las 33 votaciones del período 144.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Public+Sans:wght@300;400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>{CSS}</style>
</head>
<body>

<nav class="top"><div class="wrap">
  <a class="brand" href="/">Corvus Lab</a>
  <div><a href="/congreso">Congreso</a> · <a href="/bloques">Bloques</a> · <a href="/viabilidad">Viabilidad</a> · <a href="/simulador">Simulador</a> · <a href="/termometro">Termómetro</a> · <a href="/disidencias">Disidencias</a> · <a href="/mapa">Mapa</a> · <a href="/plan-de-metas">Plan de Metas</a> · <a href="/proyectos">Trabajos</a></div>
</div></nav>

<header class="hero"><div class="wrap">
  <div class="kicker">Cámara de Diputados · Período 144 · simulación de apoyo</div>
  <h1>Qué necesita un proyecto para que lo voten</h1>
  <p class="dek">Un proyecto no se aprueba por su texto sino por lo que toca. Marcá qué intereses mueve y el simulador devuelve qué bloque lo va a acompañar, con qué antecedente, si alcanza y cuántos votos hay que recuperar. Funciona antes de que el proyecto exista como expediente.</p>
</div></header>

<section><div class="wrap">
  <h2>Qué toca el proyecto</h2>
  <p class="sub">Cada dimensión es una familia de votaciones que ya ocurrió. El número a la derecha son las actas que la sostienen. Empezá con un caso real si querés ver cómo se comportó.</p>
  <div class="pret">{BTNS}<button data-set="">Limpiar</button></div>
  <div class="sim">
    <div class="ops">{OPS}</div>
    <div class="panel">
      <div class="lab">Votos a favor estimados</div>
      <div class="big" id="af">0</div>
      <div class="res" id="res">Elegí qué toca el proyecto</div>
      <p class="det" id="det">Marcá una o más dimensiones a la izquierda para ver cómo votaría cada bloque.</p>
      <div class="chips" id="chips"></div>
      <div style="margin-top:16px;padding-top:12px;border-top:1px solid var(--rule);font-size:13px;color:var(--muted)">
        <label for="pres">Presentes</label>
        <div style="display:flex;align-items:center;gap:10px;margin-top:6px">
          <input type="range" id="pres" min="150" max="256" value="235" step="1" style="flex:1;accent-color:#16130f">
          <b id="presv" style="font-family:'IBM Plex Mono',monospace;font-size:13px;color:#16130f;min-width:34px;text-align:right">235</b>
        </div>
        <label for="chicos" style="display:block;margin-top:12px">Votos de los bloques de 1 y 2 <span style="font-family:'IBM Plex Mono',monospace;font-size:10.5px;color:#999083">(en el período aportaron entre 6 y 15)</span></label>
        <div style="display:flex;align-items:center;gap:10px;margin-top:6px">
          <input type="range" id="chicos" min="0" max="24" value="8" step="1" style="flex:1;accent-color:#16130f">
          <b id="chicosv" style="font-family:'IBM Plex Mono',monospace;font-size:13px;color:#16130f;min-width:34px;text-align:right">8</b>
        </div>
      </div>
    </div>
  </div>
  <div class="box"><b>Cómo decide.</b> Para cada bloque se suman sus antecedentes en las dimensiones elegidas. Si votó a favor más veces de las que votó en contra, se estima a favor; si es al revés, en contra. Las abstenciones no cuentan. Cuando un bloque no tiene antecedente en ninguna de las dimensiones elegidas, se marca «sin antecedente» y no se lo suma. Los bloques de uno y dos diputados no se estiman por bloque porque no son un bloque: se cargan a mano con el control de abajo, y en el período aportaron entre 6 y 15 votos a las leyes del paquete económico.</div>
</div></section>

<section><div class="wrap">
  <h2>El registro, dimensión por dimensión</h2>
  <p class="sub">Posición mayoritaria de cada bloque en cada familia de votaciones, con la cantidad de veces que se repitió sobre el total.</p>
  <table class="mx">
    <thead><tr><th>Dimensión</th>{TH}</tr></thead>
    <tbody>{MAT}</tbody>
  </table>
</div></section>

<section><div class="wrap">
  <h2>La línea que separa a los bloques</h2>
  <p class="sub">Mirando el registro entero, cada bloque tiene una frontera clara, y no es ideológica: es temática.</p>
  <div class="tres">
    <div><b>7 de 7</b><span>veces que Provincias Unidas votó contra un proyecto de energía, el régimen de incentivos o impuestos.</span></div>
    <div><b>6 de 6</b><span>veces que acompañó cuando el proyecto era institucional: BCRA, tratados, derogación de normas, conciliaciones.</span></div>
    <div><b>10 de 10</b><span>veces que La Libertad Avanza votó en contra de una cuestión de procedimiento, junto a PRO y UCR.</span></div>
  </div>
  <div class="box"><b>Qué significa para un proyecto en preparación.</b> Un proyecto que solo toca energía, incentivos o impuestos pierde 18 votos de Provincias Unidas y 92 de Unión por la Patria, y se aprueba con el núcleo de 122 más los bloques chicos. Si además toca una cuestión de procedimiento, el eje se invierte y el proyecto cae. Si el proyecto es institucional, Provincias Unidas acompaña y el margen sube a 140.</div>
</div></section>

<section><div class="wrap">
  <h2>Cuánto se puede confiar</h2>
  <p class="sub">El simulador no adivina un proyecto nuevo: supone que el conflicto se repite. Se probó dejando cada votación afuera y prediciendo la posición de cada bloque solo con las otras votaciones de la misma familia.</p>
  <div class="tres">
    <div><b>{AC}%</b><span>de los votos emitidos, predichos correctamente (n = {NTV}).</span></div>
    <div><b>33</b><span>votaciones distintas, ocho familias, tres sesiones.</span></div>
    <div><b>1,6%</b><span>de los votos se apartan del bloque: ahí el simulador falla por diseño.</span></div>
  </div>
  <div class="box"><b>El límite, dicho claro.</b> El {AC}% mide consistencia, no extrapolación: dentro de una familia, las votaciones son capítulos de la misma ley, así que el bloque repite su posición casi por definición. Para un tema que nunca apareció en el período, el simulador no tiene antecedente y lo muestra como tal. Lo que falta para dar el salto son los dictámenes de comisión y más períodos de votaciones.</div>
</div></section>

<footer><div class="wrap">
  Fuente: 33 votaciones nominales del período 144, Cámara de Diputados de la Nación. Regla: posición mayoritaria del bloque en cada familia de votaciones, con abstenciones y ausentes excluidos; bloques de cuatro o más integrantes. El simulador cuenta antecedentes, no predice intenciones. Los votos estimados usan las bancas actuales de cada bloque, sin descontar ausencias.
</div></footer>

<script>{JS}</script>
</body></html>"""

open(OUT, "w", encoding="utf-8").write(HTML)
print(f"simulador.html {len(HTML):,} bytes · acierto LOO {acierto*100:.1f}% (n={totv})")
