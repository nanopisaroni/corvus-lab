#!/usr/bin/env python3
# Genera disidencias.html: qué diputados se apartaron de su bloque, en qué votación y en qué sentido.
import json, os, html
from collections import Counter, defaultdict

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VOTOS = os.path.join(BASE, "_build", "data", "votos.json")
MAPA = os.path.join(BASE, "_build", "data", "mapa.json")
OUT = os.path.join(BASE, "disidencias.html")

v = json.load(open(VOTOS, encoding="utf-8"))
dips, actas = v["dips"], v["actas"]
bsize = Counter(d["b"] for d in dips.values())

def tema(asunto):
    a = asunto or ""
    if "Apartamiento" in a: return "Reglamento"
    if "nergía" in a or "nergia" in a: return "Energía"
    if "11.683" in a: return "Ley 11.683"
    if "BCRA" in a: return "BCRA"
    if "incentivos" in a or "RIGI" in a: return "Régimen de incentivos"
    if "Hojarasca" in a: return "Ley Hojarasca"
    return "Otros"

dis = Counter(); vot = Counter(); pres = Counter()
ev = defaultdict(list); acta_dis = Counter(); acta_vot = Counter(); acta_bloques = defaultdict(set)
for a in actas:
    byb = defaultdict(list)
    for s, c in a["votos"].items():
        if c in ("AF", "NE"):
            byb[dips[s]["b"]].append(c)
    maj = {b: Counter(l).most_common(1)[0][0] for b, l in byb.items()}
    for s, c in a["votos"].items():
        pres[s] += 1
        if c not in ("AF", "NE"):
            continue
        vot[s] += 1
        acta_vot[a["id"]] += 1
        if c != maj.get(dips[s]["b"]):
            dis[s] += 1
            acta_dis[a["id"]] += 1
            if bsize[dips[s]["b"]] >= 3:
                acta_bloques[a["id"]].add(dips[s]["b"])
            ev[s].append(dict(id=a["id"], acta=a["acta"], dia=a["dia"], asunto=a.get("asunto") or "",
                              mi=c, bloque=maj[dips[s]["b"]], proc=bool(a.get("procedimental")),
                              tema=tema(a.get("asunto"))))

ANAL = [s for s in dips if bsize[dips[s]["b"]] >= 3]
sin_dis = sum(1 for s in ANAL if dis[s] == 0)
total_dis = sum(dis[s] for s in ANAL)
total_vot = sum(vot[s] for s in ANAL)

def nf(n): return f"{n:,}".replace(",", ".")
def pct(x): return f"{x:.1f}%".replace(".", ",")
def fecha(d): return f"{d[6:8]}/{d[4:6]}"
VOTO = {"AF": "afirmativo", "NE": "negativo", "AB": "abstención"}

# --- bloques
FILAS_B = ""
for b in sorted([b for b in bsize if bsize[b] >= 3], key=lambda b: -(sum(dis[s] for s in ANAL if dips[s]["b"] == b) / max(1, sum(vot[s] for s in ANAL if dips[s]["b"] == b)))):
    ms = [s for s in ANAL if dips[s]["b"] == b]
    tv = sum(vot[s] for s in ms); td = sum(dis[s] for s in ms); tp = sum(pres[s] for s in ms)
    con = sum(1 for s in ms if dis[s] > 0)
    FILAS_B += (f'<tr><td>{html.escape(b.title())}</td><td class="num">{len(ms)}</td>'
                f'<td class="num">{100*tp/(len(ms)*len(actas)):.1f}%</td>'
                f'<td class="num">{nf(tv)}</td><td class="num">{td}</td>'
                f'<td class="num {"warn" if td and 100*td/tv>=5 else ""}">{pct(100*td/max(1,tv))}</td>'
                f'<td class="num soft">{con}</td></tr>')

# --- actas
FILAS_A = ""
meta = {a["id"]: a for a in actas}
for aid, n in sorted(acta_dis.items(), key=lambda x: -x[1]):
    a = meta[aid]
    FILAS_A += (f'<tr id="v{aid}"><td class="num">{fecha(a["dia"])}</td><td class="num">{a["acta"]}</td>'
                f'<td>{html.escape((a.get("asunto") or "Sin asunto")[:96])}</td>'
                f'<td><span class="tag">{tema(a.get("asunto"))}</span></td>'
                f'<td class="num">{n}</td><td class="num soft">{len(acta_bloques[aid])}</td></tr>')

# --- fichas de los disidentes
D = sorted([s for s in ANAL if dis[s] > 0], key=lambda s: -dis[s] / max(1, vot[s]))
BLOQUE_COLOR = {"PROVINCIAS UNIDAS": "#2f6fa8", "ARGENTINA FEDERAL": "#8a5a12", "PRO": "#b8912a",
                "LA LIBERTAD AVANZA": "#6b4fa8", "UNIÓN POR LA PATRIA": "#3f7d6b", "INDEPENDENCIA": "#7a7386"}
TARJETAS = ""
for s in D:
    p = dips[s]
    filas = ""
    for e in sorted(ev[s], key=lambda e: (e["dia"], e["acta"])):
        dire = "Votó distinto al bloque" if e["mi"] != e["bloque"] else ""
        filas += (f'<li><span class="fv">{fecha(e["dia"])}</span>'
                  f'<a href="#v{e["id"]}">acta {e["acta"]}</a>'
                  f'<span class="fmi">{VOTO.get(e["mi"], e["mi"])}</span>'
                  f'<span class="fbl">bloque {VOTO.get(e["bloque"], e["bloque"])}</span>'
                  f'<span class="ftema">{e["tema"]}</span></li>')
    TARJETAS += f"""
    <div class="ficha" id="d{s}" data-b="{html.escape((p['n']+' '+p['b']).lower())}">
      <div class="fcab">
        <div><a class="fn" href="/diputado/{s}">{html.escape(p['n'])}</a>
        <span class="fb" style="border-color:{BLOQUE_COLOR.get(p['b'],'#999')}">{html.escape(p['b'].title())}</span></div>
        <div class="fnum"><b>{dis[s]}</b> de {vot[s]} votaciones <span>{pct(100*dis[s]/max(1,vot[s]))}</span></div>
      </div>
      <ul class="flist">{filas}</ul>
    </div>"""

HTML = f"""<!DOCTYPE html>
<html lang="es-AR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Disidencias · cómo votó cada diputado contra su bloque</title>
<meta name="description" content="Los 25 diputados que se apartaron de su bloque en el período 144: en qué votación, en qué sentido y sobre qué tema.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Public+Sans:wght@300;400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
:root {{ --paper:#f8f6f2; --card:#fff; --ink:#16130f; --muted:#6d665c; --soft:#999083; --rule:#e2dcd1; --rule-strong:#c9c1b3; --warn:#a4401c; }}
* {{ box-sizing:border-box; }}
html {{ -webkit-text-size-adjust:100%; }}
body {{ margin:0; background:var(--paper); color:var(--ink); font-family:"Public Sans",-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; font-size:16px; line-height:1.55; -webkit-font-smoothing:antialiased; }}
.wrap {{ max-width:1080px; margin:0 auto; padding:0 28px; }}
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
p.intro {{ color:var(--muted); max-width:780px; margin:0 0 24px; font-size:15.5px; }}
table {{ width:100%; border-collapse:collapse; font-size:14.5px; }}
th {{ text-align:left; font-family:"IBM Plex Mono",monospace; font-size:10.5px; letter-spacing:.09em; text-transform:uppercase; color:var(--soft); font-weight:500; padding:0 10px 9px 0; border-bottom:1px solid var(--rule-strong); }}
td {{ padding:9px 10px 9px 0; border-bottom:1px solid var(--rule); vertical-align:baseline; }}
td.num, th.num {{ text-align:right; font-family:"IBM Plex Mono",monospace; font-size:13.5px; padding-right:14px; white-space:nowrap; }}
td.soft {{ color:var(--muted); }}
td.warn {{ color:var(--warn); font-weight:500; }}
.tag {{ font-family:"IBM Plex Mono",monospace; font-size:10.5px; letter-spacing:.03em; padding:2px 6px; border-radius:2px; background:#efece5; color:#5c554a; white-space:nowrap; }}
.tbox {{ overflow-x:auto; }}
.buscador input {{ width:100%; max-width:420px; font:inherit; font-size:15px; padding:10px 14px; border:1px solid var(--rule-strong); border-radius:2px; background:var(--card); margin-bottom:18px; }}
.ficha {{ background:var(--card); border:1px solid var(--rule); border-radius:3px; padding:16px 20px 8px; margin-bottom:12px; }}
.fcab {{ display:flex; justify-content:space-between; align-items:baseline; gap:16px; flex-wrap:wrap; border-bottom:1px solid var(--rule); padding-bottom:10px; margin-bottom:8px; }}
.fn {{ color:var(--ink); text-decoration:none; font-weight:600; font-size:16.5px; border-bottom:1px solid var(--rule-strong); }}
.fb {{ font-family:"IBM Plex Mono",monospace; font-size:10.5px; color:var(--muted); border-left:3px solid; padding-left:7px; margin-left:8px; }}
.fnum {{ font-family:"IBM Plex Mono",monospace; font-size:12.5px; color:var(--muted); }}
.fnum b {{ font-family:"Public Sans",sans-serif; font-size:17px; color:var(--ink); }}
.fnum span {{ font-weight:600; color:var(--ink); }}
.flist {{ list-style:none; margin:0; padding:0; }}
.flist li {{ display:grid; grid-template-columns:52px 78px 1fr 1fr 108px; gap:8px; align-items:baseline; font-size:13.5px; padding:5px 0; border-bottom:1px solid #f0ece5; }}
.flist li:last-child {{ border-bottom:0; }}
.fv {{ font-family:"IBM Plex Mono",monospace; font-size:12px; color:var(--soft); }}
.flist a {{ color:var(--muted); text-decoration:none; font-family:"IBM Plex Mono",monospace; font-size:12px; }}
.flist a:hover {{ color:var(--ink); }}
.fmi {{ font-weight:600; }}
.fbl {{ color:var(--muted); }}
.ftema {{ font-family:"IBM Plex Mono",monospace; font-size:11px; color:var(--soft); text-align:right; }}
.metodo {{ background:var(--card); border:1px solid var(--rule); border-radius:3px; padding:26px 28px; margin:44px 0 10px; }}
.metodo h2 {{ margin-bottom:12px; }}
.metodo p {{ color:var(--muted); font-size:14.5px; margin:0 0 12px; max-width:860px; }}
.metodo p:last-child {{ margin-bottom:0; }}
footer {{ padding:26px 0 60px; color:var(--soft); font-size:12.5px; }}
@media (max-width:760px) {{
  .cifras {{ grid-template-columns:repeat(2,1fr); }}
  .wrap {{ padding:0 18px; }}
  header.hero {{ padding:38px 0 22px; }}
  table {{ font-size:13px; }}
  .flist li {{ grid-template-columns:46px 66px 1fr; row-gap:2px; }}
  .ftema {{ grid-column:1/-1; text-align:left; }}
  .fbl {{ grid-column:3; }}
}}
</style>
</head>
<body>

<nav class="top"><div class="wrap">
  <a class="brand" href="/">Corvus Lab</a>
  <div><a href="/congreso">Congreso</a> · <a href="/cordoba">Córdoba</a> · <a href="/mapa">Mapa</a> · <a href="/bloques">Bloques</a> · <a href="/viabilidad">Viabilidad</a> · <a href="/simulador">Simulador</a> · <a href="/afinidad">Afinidad</a> · <a href="/plan-de-metas">Plan de Metas</a> · <a href="/proyectos">Trabajos</a></div>
</div></nav>

<header class="hero"><div class="wrap">
  <div class="kicker">Cámara de Diputados · Período 144 · 33 votaciones nominales</div>
  <h1>Cómo y por qué votó en disidencia cada diputado</h1>
  <p class="dek">De 238 diputados en bloques de tres o más integrantes, {sin_dis} nunca se apartaron de la posición mayoritaria de su bloque. Los {len(D)} que sí lo hicieron suman {nf(total_dis)} votos apartados sobre {nf(total_vot)} emitidos, y acá está cada uno: la votación, el tema y en qué sentido se corrieron.</p>
</div></header>

<div class="cifras">
  <div class="cifra"><b>{sin_dis} de 238</b><span>nunca se apartaron de su bloque</span></div>
  <div class="cifra"><b>{nf(total_dis)}</b><span>votos en disidencia sobre {nf(total_vot)} emitidos</span></div>
  <div class="cifra"><b>{len(D)}</b><span>diputados con al menos una disidencia</span></div>
  <div class="cifra"><b>{pct(100*total_dis/max(1,total_vot))}</b><span>del total de votos emitidos</span></div>
</div>

<section><div class="wrap">
  <h2>Disciplina por bloque <span>· y cuánto se sientan</span></h2>
  <p class="intro">Porcentaje de votos emitidos en que el integrante se apartó de la mayoría de su propio bloque. Presencia sobre el total de votaciones por integrante. Se excluyen los bloques de uno y dos miembros: ahí la mayoría del bloque se confunde con el voto del propio diputado y el indicador no mide nada.</p>
  <div class="tbox"><table>
    <thead><tr><th>Bloque</th><th class="num">Integrantes</th><th class="num">Presencia</th><th class="num">Votos emitidos</th><th class="num">Disidencias</th><th class="num">%</th><th class="num">Con 1 o más</th></tr></thead>
    <tbody>{FILAS_B}</tbody>
  </table></div>
</div></section>

<section><div class="wrap">
  <h2>Qué se votó cuando se rompió la disciplina <span>· solo las votaciones con disidencia</span></h2>
  <p class="intro">Ordenadas por cantidad de diputados que se corrieron. La última columna cuenta cuántos bloques distintos quedaron partidos en esa votación. «Reglamento» son las mociones de apartamiento del reglamento, que se votan para sancionar o habilitar a un diputado puntual.</p>
  <div class="tbox"><table>
    <thead><tr><th class="num">Fecha</th><th class="num">Acta</th><th>Asunto</th><th>Tema</th><th class="num">Disidencias</th><th class="num">Bloques partidos</th></tr></thead>
    <tbody>{FILAS_A}</tbody>
  </table></div>
</div></section>

<section><div class="wrap">
  <h2>Los {len(D)} diputados <span>· votación por votación</span></h2>
  <p class="intro">Cada línea es un voto en que el diputado no acompañó a la mayoría de su bloque. Se lee: fecha, acta, cómo votó él, cómo votó la mayoría de su bloque y el tema. Las actas enlazan a la tabla de arriba.</p>
  <div class="buscador"><input id="q" type="search" placeholder="Buscar diputado o bloque" autocomplete="off"></div>
  {TARJETAS}
</div></section>

<div class="wrap"><div class="metodo">
  <h2>Método y límites</h2>
  <p><b>Cómo se calcula.</b> En cada una de las 33 votaciones nominales se toma la posición mayoritaria del bloque al que pertenece el diputado, y se cuenta como disidencia todo voto afirmativo o negativo distinto a esa mayoría. Abstenciones y ausencias quedan fuera de la base: no suman como disidencia ni como acompañamiento.</p>
  <p><b>Qué queda afuera.</b> Los 18 diputados de bloques de uno y dos integrantes no entran en el cálculo. En un bloque de un solo miembro la mayoría es su propio voto, y en uno de dos cualquier diferencia da 50% artificial. El mismo problema es el que producía los porcentajes imposibles de versiones anteriores de este indicador.</p>
  <p><b>Qué no dice.</b> Votar distinto del bloque no distingue convicción de estrategia ni de error. Un diputado puede correrse por acuerdo con el oficialismo, por presión de su provincia o porque su bloque votó una posición que no comparte. El dato dice qué pasó en el recinto, no por qué.</p>
  <p><b>Fuente.</b> Cámara de Diputados de la Nación, actas de votación nominal publicadas en el apéndice de los diarios de sesiones del período 144, del 20 de mayo al 26 de agosto de 2026.</p>
</div></div>

<footer><div class="wrap">Corvus Lab · datos abiertos del Congreso · actualizado el 17 de noviembre de 2026</div></footer>

<script>
const q = document.getElementById('q'), fichas = [...document.querySelectorAll('.ficha')];
q.addEventListener('input', () => {{
  const t = q.value.trim().toLowerCase();
  for (const f of fichas) f.style.display = (!t || f.dataset.b.includes(t)) ? '' : 'none';
}});
</script>
</body>
</html>"""

open(OUT, "w", encoding="utf-8").write(HTML)
print("escrito", OUT, len(HTML), "bytes |", len(D), "disidentes |", sin_dis, "sin disidencia |", total_dis, "eventos")
