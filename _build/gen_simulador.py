#!/usr/bin/env python3
# Simulador interactivo: diales por dimensión, votabilidad por bloque en vivo.
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
tam = Counter(d["b"] for d in dips.values())

DIMS = [
    ("energia", "Energía", "Tarifas libres, fin de subsidios", "Tarifas reguladas, subsidios",
     "Los siete capítulos del proyecto de energía fijaban precio libre y quitaban subsidios."),
    ("incentivos", "Incentivos a la inversión", "Régimen amplio para grandes inversiones", "Sin régimen, revisión caso por caso",
     "El régimen de incentivos daba beneficios impositivos y aduaneros a inversiones grandes."),
    ("fiscal", "Impuestos", "Reforma que baja y simplifica tributos", "Status quo y más controles",
     "La reforma de la ley 11.683 delegaba facultades y simplificaba el procedimiento."),
    ("bcra", "Banco Central", "Autonomía y meta de inflación", "Control político y financiamiento",
     "La Carta Orgánica fijaba metas y limitaba el financiamiento al Tesoro."),
    ("tratados", "Tratados internacionales", "Ratificar el tratado", "No ratificar",
     "El tratado de patentes comprometía propiedad intelectual con otro país."),
    ("desregulacion", "Desregulación", "Derogar normas", "Mantener las normas",
     "La ley Hojarasca derogaba un paquete de normas consideradas obsoletas."),
]

def dim(s):
    s = (s or "").lower()
    if "energ" in s: return "energia"
    if "incentivos" in s: return "incentivos"
    if "11.683" in s: return "fiscal"
    if "bcra" in s: return "bcra"
    if "hojarasca" in s: return "desregulacion"
    if "patentes" in s: return "tratados"
    if "conciliaciones" in s: return "conciliaciones"
    return "procedimiento"

# posición modal de cada bloque por dimensión
pos = defaultdict(lambda: defaultdict(Counter))
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
            pos[k][b][c[b].most_common(1)[0][0]] += 1

# polo preferido: AF = polo A, NE = polo B
PREF = {}
for k, *_ in DIMS:
    PREF[k] = {AB[b]: ("A" if pos[k][b]["AF"] >= pos[k][b]["NE"] else "B") for b in B}

# --- validación leave-one-out
posx = []
for a in actas:
    c = defaultdict(Counter)
    for dip, voto in a["votos"].items():
        b = dips.get(dip, {}).get("b")
        if voto in VALIDOS and b:
            c[b][voto] += 1
    posx.append({b: (c[b].most_common(1)[0][0] if sum(c[b].values()) >= 4 else None) for b in B})
okv = totv = 0
for i, a in enumerate(actas):
    for b in B:
        hist = Counter()
        for j, x in enumerate(actas):
            if j == i or dim(x["asunto"]) != dim(a["asunto"]):
                continue
            p = posx[j].get(b)
            if p: hist[p] += 1
        if not hist: continue
        pred = hist.most_common(1)[0][0]
        for dip, voto in a["votos"].items():
            if voto in VALIDOS and dips.get(dip, {}).get("b") == b:
                totv += 1
                okv += pred == voto
AC = f"{okv/totv*100:.1f}".replace(".", ",")
NTV = f"{totv:,}".replace(",", ".")

# --- registro visible (tabla)
MAT = ""
for k, titulo, pa, pb, nota in DIMS:
    celdas = ""
    for b in B:
        af, ne = pos[k][b]["AF"], pos[k][b]["NE"]
        if not af and not ne:
            celdas += '<td class="cel sin"><span>sin dato</span></td>'
            continue
        clase = "af" if af > ne else ("ne" if ne > af else "emp")
        signo = "A favor" if af > ne else ("En contra" if ne > af else "Empate")
        celdas += f'<td class="cel {clase}"><b>{signo}</b><span>{max(af,ne)} de {af+ne}</span></td>'
    MAT += (f'<tr><td class="dm"><b>{esc(titulo)}</b><span>{len(actas_de[k])} acta{"s" if len(actas_de[k])>1 else ""}</span></td>{celdas}</tr>')
TH = "".join(f'<th class="bc">{AB[b]}</th>' for b in B)

# --- diales
DIALES = ""
INICIAL = {"energia": 12, "incentivos": 10, "fiscal": 15, "bcra": 12, "tratados": 10, "desregulacion": 8}
for k, titulo, pa, pb, nota in DIMS:
    DIALES += f"""
    <div class="dial" data-dim="{k}">
      <div class="dhead">
        <label class="dname"><input type="checkbox" class="on" checked> {esc(titulo)}</label>
        <span class="dval" data-val title="posición de la palanca: 0 es el extremo izquierdo, 100 el derecho">{INICIAL[k]} / 100</span>
      </div>
      <input type="range" class="rng" min="0" max="100" value="{INICIAL[k]}" step="1">
      <div class="poles"><span class="pa">{esc(pa)}</span><span class="pb">{esc(pb)}</span></div>
      <div class="dnota">{esc(nota)}</div>
    </div>"""

PRESETS = [
    ("Lo que se votó", {"energia": 12, "incentivos": 10, "fiscal": 15, "bcra": 12, "tratados": 10, "desregulacion": 8}),
    ("Institucional", {"energia": 50, "incentivos": 50, "fiscal": 50, "bcra": 8, "tratados": 8, "desregulacion": 8}),
    ("Neutro", {}),
    ("Hacia la oposición", {"energia": 88, "incentivos": 90, "fiscal": 85, "bcra": 50, "tratados": 50, "desregulacion": 50}),
]
BTNS = "".join(f'<button data-preset=\'{json.dumps(p)}\'>{esc(n)}</button>' for n, p in PRESETS)

JS = """
const PREF = """ + json.dumps(PREF) + """;
const SEATS = """ + json.dumps({AB[b]: tam[b] for b in B}) + """;
const NOMBRE = """ + json.dumps(dict([("LLA","La Libertad Avanza"),("PRO","PRO"),("UCR","UCR"),("AFed","Argentina Federal"),("PU","Provincias Unidas"),("UxP","Unión por la Patria")]), ensure_ascii=False) + """;
const POLOS = """ + json.dumps({k: [pa, pb] for k, _, pa, pb, _ in DIMS}) + """;
const LAB = """ + json.dumps({k: t for k, t, _, _, _ in DIMS}) + """;
const BLOCS = ["LLA","PRO","UCR","AFed","PU","UxP"];

const dials = [...document.querySelectorAll('.dial')].map(el => ({
  el, dim: el.dataset.dim,
  rng: el.querySelector('.rng'),
  on: el.querySelector('.on'),
  val: el.querySelector('[data-val]')
}));
const chicos = document.getElementById('chicos');
const presentes = document.getElementById('pres');
const outCh = document.getElementById('chicosv');
const outPr = document.getElementById('presv');

function alineacion(dim, x, b) {
  // x=0 -> polo A ; x=100 -> polo B
  return PREF[dim][b] === 'A' ? (100 - x) : x;
}

function calcular() {
  const activos = dials.filter(d => d.on.checked);
  const out = {};
  BLOCS.forEach(b => {
    if (!activos.length) { out[b] = {al: 50, estado: 'sin'}; return; }
    let suma = 0;
    activos.forEach(d => { suma += alineacion(d.dim, +d.rng.value, b); });
    const al = suma / activos.length;
    out[b] = {al, estado: al >= 60 ? 'af' : (al <= 40 ? 'ne' : 'duda')};
  });

  // barras
  const cont = document.getElementById('barras');
  cont.innerHTML = BLOCS.map(b => {
    const o = out[b];
    const cl = o.estado === 'af' ? 'af' : (o.estado === 'ne' ? 'ne' : 'duda');
    const txt = o.estado === 'af' ? 'vota a favor' : (o.estado === 'ne' ? 'vota en contra' : 'zona gris');
    return `<div class="bar ${cl}">
      <div class="bl"><b>${NOMBRE[b]}</b><span>${SEATS[b]} bancas</span></div>
      <div class="bt"><div class="bf" style="width:${Math.round(o.al)}%"></div></div>
      <div class="bv"><b>${Math.round(o.al)}%</b><span>${txt}</span></div>
    </div>`;
  }).join('');

  // conteo
  let af = 0;
  BLOCS.forEach(b => { if (out[b].estado === 'af') af += SEATS[b]; });
  af += +chicos.value;
  const pres = +presentes.value;
  af = Math.min(af, pres);
  const nec = Math.floor(pres / 2) + 1;
  document.getElementById('af').textContent = af;
  const res = document.getElementById('res');
  const det = document.getElementById('det');
  if (af >= nec) {
    res.textContent = 'Se aprueba';
    res.className = 'res ok';
    det.textContent = af + ' votos sobre ' + pres + ' presentes. Mínimo ' + nec + ': aguanta ' + (af - nec) + ' deserción(es).';
  } else {
    res.textContent = 'No se aprueba';
    res.className = 'res no';
    det.textContent = af + ' votos sobre ' + pres + ' presentes. Mínimo ' + nec + ': faltan ' + (nec - af) + '.';
  }

  // qué le falta a cada bloque que no acompaña
  const fl = document.getElementById('falta');
  const items = [];
  BLOCS.forEach(b => {
    if (out[b].estado === 'af') return;
    const bajos = activos
      .map(d => ({d, a: alineacion(d.dim, +d.rng.value, b)}))
      .filter(x => x.a < 60)
      .sort((x, y) => x.a - y.a)
      .slice(0, 3);
    if (!bajos.length) return;
    const partes = bajos.map(x => LAB[x.d.dim] + ' hacia «' + POLOS[x.d.dim][PREF[x.d.dim][b] === 'A' ? 0 : 1] + '»');
    items.push('<li><b>' + NOMBRE[b] + '</b>: ' + partes.join(', ') + '</li>');
  });
  fl.innerHTML = items.length ? items.join('') : '<li>Todos los bloques activos acompañan.</li>';
}

dials.forEach(d => {
  d.rng.addEventListener('input', () => { d.val.textContent = d.rng.value; calcular(); });
  d.on.addEventListener('change', calcular);
});
chicos.addEventListener('input', calcular);
presentes.addEventListener('input', () => { outPr.textContent = presentes.value; calcular(); });
document.querySelectorAll('.pret button').forEach(b => b.addEventListener('click', () => {
  const p = JSON.parse(b.dataset.preset);
  dials.forEach(d => {
    if (p[d.dim] !== undefined) { d.rng.value = p[d.dim]; d.val.textContent = p[d.dim]; d.on.checked = true; }
    else { d.rng.value = 50; d.val.textContent = 50; d.on.checked = false; }
  });
  calcular();
}));
calcular();
"""

CSS = """
:root { --paper:#f8f6f2; --card:#fff; --ink:#16130f; --muted:#6d665c; --soft:#999083; --rule:#e2dcd1; --rule-strong:#c9c1b3; --ok:#2f6b4f; --no:#b04234; --amb:#9a6b1f; }
* { box-sizing:border-box; }
body { margin:0; background:var(--paper); color:var(--ink); font-family:"Public Sans",-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; font-size:16px; line-height:1.55; -webkit-font-smoothing:antialiased; }
.wrap { max-width:1120px; margin:0 auto; padding:0 28px; }
nav.top { border-bottom:1px solid var(--rule); }
nav.top .wrap { display:flex; justify-content:space-between; align-items:baseline; padding:14px 28px; gap:16px; flex-wrap:wrap; }
nav.top a { color:var(--muted); text-decoration:none; font-size:13px; }
nav.top a:hover { color:var(--ink); }
nav.top .brand { font-family:"IBM Plex Mono",monospace; font-size:12px; letter-spacing:.12em; text-transform:uppercase; color:var(--ink); }
.kicker { font-family:"IBM Plex Mono",monospace; font-size:11.5px; letter-spacing:.14em; text-transform:uppercase; color:var(--soft); margin-bottom:16px; }
header.hero { padding:48px 0 28px; border-bottom:1px solid var(--rule-strong); }
h1 { font-size:clamp(28px,4.6vw,42px); line-height:1.1; letter-spacing:-.02em; font-weight:600; margin:0 0 16px; }
.dek { font-size:17.5px; color:#3b352d; max-width:780px; margin:0; }
section { padding:40px 0; border-bottom:1px solid var(--rule); }
h2 { font-size:22px; letter-spacing:-.01em; font-weight:600; margin:0 0 6px; }
.sub { color:var(--muted); font-size:15px; margin:0 0 22px; max-width:760px; }
.pret { display:flex; gap:8px; flex-wrap:wrap; margin-bottom:20px; }
.pret button { font-family:inherit; font-size:12.5px; padding:6px 12px; border:1px solid var(--rule-strong); background:transparent; border-radius:2px; cursor:pointer; color:#4a443b; }
.pret button:hover { background:#efece5; color:var(--ink); }
.sim { display:grid; grid-template-columns:1fr 380px; gap:30px; align-items:start; }
.dial { padding:12px 0 14px; border-bottom:1px solid #ece7de; }
.dhead { display:flex; justify-content:space-between; align-items:baseline; gap:10px; }
.dname { font-size:14.5px; font-weight:600; cursor:pointer; display:flex; align-items:center; gap:7px; }
.dname input { width:14px; height:14px; accent-color:#16130f; }
.dval { font-family:"IBM Plex Mono",monospace; font-size:12px; color:var(--soft); }
.rng { width:100%; margin:9px 0 4px; accent-color:#16130f; height:18px; }
.poles { display:flex; justify-content:space-between; gap:12px; font-size:11.5px; color:var(--muted); }
.poles .pb { text-align:right; }
.dnota { font-size:11.5px; color:var(--soft); margin-top:5px; line-height:1.4; }
.panel { background:var(--card); border:1px solid var(--rule); border-radius:3px; padding:18px 20px; position:sticky; top:14px; }
.panel .lab { font-family:"IBM Plex Mono",monospace; font-size:10px; letter-spacing:.1em; text-transform:uppercase; color:var(--soft); }
.bar { display:grid; grid-template-columns:118px 1fr 74px; gap:8px; align-items:center; padding:6px 0; }
.bl b { display:block; font-size:12px; font-weight:600; line-height:1.2; }
.bl span { font-family:"IBM Plex Mono",monospace; font-size:9.5px; color:var(--soft); }
.bt { height:9px; background:#eee9e0; border-radius:1px; overflow:hidden; }
.bf { height:100%; background:#c9c1b3; transition:width .18s ease; }
.bar.af .bf { background:var(--ok); } .bar.ne .bf { background:var(--no); } .bar.duda .bf { background:var(--amb); }
.bv b { font-family:"IBM Plex Mono",monospace; font-size:12px; }
.bv span { display:block; font-size:9.5px; color:var(--soft); }
.bar.af .bv b { color:var(--ok); } .bar.ne .bv b { color:var(--no); } .bar.duda .bv b { color:var(--amb); }
.total { border-top:1px solid var(--rule); margin-top:12px; padding-top:14px; }
.total .big { font-family:"IBM Plex Mono",monospace; font-size:36px; font-weight:500; letter-spacing:-.03em; line-height:1; }
.res { font-size:16px; font-weight:600; margin:8px 0 2px; }
.res.ok { color:var(--ok); } .res.no { color:var(--no); }
.det { font-size:12.5px; color:#4a443b; margin:4px 0 0; line-height:1.45; }
.ctrl { margin-top:14px; padding-top:12px; border-top:1px solid var(--rule); font-size:12px; color:var(--muted); }
.ctrl label { display:block; margin-bottom:2px; }
.ctrl input[type=range] { width:100%; accent-color:#16130f; }
.ctrlrow { display:flex; align-items:center; gap:10px; }
.ctrlrow b { font-family:"IBM Plex Mono",monospace; font-size:12px; color:var(--ink); min-width:34px; text-align:right; }
.falta { margin:14px 0 0; padding:0; list-style:none; border-top:1px solid var(--rule); padding-top:12px; }
.falta li { font-size:12px; color:#4a443b; padding:3px 0; line-height:1.4; }
table.mx { width:100%; border-collapse:collapse; }
table.mx th { text-align:left; font-family:"IBM Plex Mono",monospace; font-size:9.5px; letter-spacing:.06em; text-transform:uppercase; color:var(--soft); font-weight:500; padding:0 4px 8px; border-bottom:1px solid var(--rule-strong); }
table.mx th.bc { text-align:center; width:72px; }
table.mx td { border-bottom:1px solid #ece7de; padding:6px 4px; }
td.dm { width:220px; }
td.dm b { display:block; font-size:13.5px; font-weight:500; line-height:1.25; }
td.dm span { font-family:"IBM Plex Mono",monospace; font-size:10px; color:var(--soft); }
td.cel { text-align:center; }
td.cel b { display:block; font-size:11px; font-weight:600; }
td.cel span { font-family:"IBM Plex Mono",monospace; font-size:9.5px; color:var(--soft); }
td.cel.af b { color:var(--ok); } td.cel.ne b { color:var(--no); } td.cel.sin b { color:var(--soft); font-weight:400; }
.box { border-left:3px solid #16130f; background:#f4f1ea; padding:14px 18px; font-size:14px; margin:16px 0 0; }
.tres { display:grid; grid-template-columns:repeat(3,1fr); gap:20px; }
.tres div b { display:block; font-family:"IBM Plex Mono",monospace; font-size:30px; font-weight:500; letter-spacing:-.03em; line-height:1; margin-bottom:5px; }
.tres div span { font-size:13px; color:var(--muted); line-height:1.45; display:block; }
footer { padding:28px 0 48px; font-size:13px; color:var(--muted); }
@media (max-width:900px) { .sim { grid-template-columns:1fr; } .panel { position:static; } .tres { grid-template-columns:1fr; gap:14px; } }
@media (max-width:620px) {
  .wrap { padding:0 16px; }
  header.hero { padding:32px 0 20px; }
  section { padding:28px 0; }
  .dek { font-size:16px; }
  .bar { grid-template-columns:96px 1fr 66px; }
  .bl b { font-size:11px; }
  table.mx th.bc { width:auto; font-size:8.5px; }
  td.dm { width:100px; } td.cel b { font-size:9.5px; } td.cel span { font-size:8.5px; }
}
"""

HTML = f"""<!DOCTYPE html>
<html lang="es-AR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Simulador · cuánto se puede mover un proyecto para que lo voten</title>
<meta name="description" content="Simulador interactivo: movés cada dimensión del proyecto hacia un lado o el otro y ves en vivo qué bloques lo acompañan, cuántos votos suma y qué le falta a cada uno para votar a favor.">
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
  <div class="kicker">Cámara de Diputados · Período 144 · simulador de proyecto</div>
  <h1>Movés el proyecto, cambia el que lo vota</h1>
  <p class="dek">Cada palanca es una decisión de redacción. A la izquierda y a la derecha están los dos extremos que efectivamente se votaron en el período. Movelas y vas a ver, en vivo, cómo se mueve cada bloque, cuántos votos junta el proyecto y qué le falta a cada uno para acompañarlo.</p>
</div></header>

<section><div class="wrap">
  <div class="pret">{BTNS}</div>
  <div class="sim">
    <div>{DIALES}</div>
    <div class="panel">
      <div class="lab">Votabilidad por bloque</div>
      <div id="barras" style="margin-top:10px"></div>
      <div class="total">
        <div class="lab">Votos a favor</div>
        <div class="big" id="af">0</div>
        <div class="res" id="res">—</div>
        <p class="det" id="det"></p>
      </div>
      <ul class="falta" id="falta"></ul>
      <div class="ctrl">
        <label>Presentes</label>
        <div class="ctrlrow"><input type="range" id="pres" min="150" max="256" value="235" step="1"><b id="presv">235</b></div>
        <label style="margin-top:10px">Votos de los bloques de 1 y 2 <span style="font-size:10.5px;color:#999083;display:block;line-height:1.3">Los 24 diputados de bloques de uno y dos no se estiman por bloque. En el período aportaron entre 6 y 15 votos a las leyes del oficialismo.</span></label>
        <div class="ctrlrow"><input type="range" id="chicos" min="0" max="24" value="8" step="1"><b id="chicosv">8</b></div>
      </div>
    </div>
  </div>
</div></section>

<section><div class="wrap">
  <h2>Cómo se calcula</h2>
  <p class="sub">Cada palanca vale lo mismo. Para cada bloque se mide qué tan cerca quedó el proyecto del extremo que ese bloque votó en las actas de esa familia. El promedio de esas distancias es la votabilidad: arriba de 60% se cuenta como voto a favor, abajo de 40% como voto en contra, y en el medio queda la zona gris, donde el bloque no tiene antecedente de haber votado algo intermedio.</p>
  <div class="tres">
    <div><b>{AC}%</b><span>de los votos emitidos, predichos correctamente al dejar cada acta afuera (n = {NTV}).</span></div>
    <div><b>33</b><span>votaciones nominales, seis familias de tema, tres sesiones.</span></div>
    <div><b>0</b><span>veces que un bloque votó distinto dentro de la misma familia, salvo Provincias Unidas en impuestos.</span></div>
  </div>
  <div class="box"><b>El límite.</b> Los polos de cada palanca salen de lo que las actas efectivamente proponían, no de una escala ideológica. Un proyecto con una cláusula nueva que no apareció en el período queda en zona gris por definición: el simulador no extrapola, informa que no tiene antecedente.</div>
</div></section>

<section><div class="wrap">
  <h2>El registro que sostiene cada palanca</h2>
  <p class="sub">Posición mayoritaria de cada bloque en cada familia de votaciones, con la cantidad de veces que se repitió sobre el total.</p>
  <table class="mx">
    <thead><tr><th>Dimensión</th>{TH}</tr></thead>
    <tbody>{MAT}</tbody>
  </table>
</div></section>

<footer><div class="wrap">
  Fuente: 33 votaciones nominales del período 144, Cámara de Diputados de la Nación. Regla: posición mayoritaria del bloque en cada familia de votaciones, abstenciones y ausentes excluidos, bloques de cuatro o más integrantes. Los polos de cada palanca describen lo que proponían las actas de esa familia. Votos estimados con las bancas actuales, sin descontar ausencias.
</div></footer>

<script>{JS}</script>
</body></html>"""

open(OUT, "w", encoding="utf-8").write(HTML)
print(f"simulador.html {len(HTML):,} bytes · {len(DIMS)} palancas · acierto LOO {AC}%")
