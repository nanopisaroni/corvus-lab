#!/usr/bin/env python3
# Genera cordoba.html: voto de 2025 por localidad (Córdoba) cruzado con cómo votaron
# los diputados cordobeses. Fuentes: 427.Cba (resultados por localidad), HCDN (actas).
import json, os, html
from collections import Counter, defaultdict

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(BASE, "_build", "data", "cordoba-427.json")
MAPA = os.path.join(BASE, "_build", "data", "mapa.json")
FICHAS = os.path.join(BASE, "_build", "data", "fichas.json")
VOTOS = os.path.join(BASE, "_build", "data", "votos.json")
OUT = os.path.join(BASE, "cordoba.html")

d = json.load(open(SRC, encoding="utf-8"))
filas, ids, campos = d["filas"], d["ids"], [c["k"] for c in d["campos"]]
ix = {k: i for i, k in enumerate(campos)}
GRP = {0: "LLA", 1: "PU", 2: "DC", 3: "FP", 4: "PL", 5: "UCR", 6: "FIT"}
NOMBRE = {"LLA": "La Libertad Avanza", "PU": "Provincias Unidas", "DC": "Defendamos Córdoba",
          "FP": "Fuerza Patria", "PL": "Partido Libertario", "UCR": "UCR", "FIT": "FIT – Unidad",
          "OTROS": "Otros partidos"}
orden = ["LLA", "PU", "DC", "FP", "PL", "UCR", "FIT", "OTROS"]
loc = d["elec"]["loc"]["d25"]

LUG = {}
for i, lid in enumerate(ids):
    f = filas[i]
    LUG[lid] = dict(nombre=f[ix["LOCALIDAD"]], tipo=f[ix["TIPO"]], depto=f[ix["DEPARTAMENTO"]],
                    pob=f[ix["Pob. viviendas partic."]] or 0,
                    intendente=f[ix["INTENDENTE / JEFE COMUNAL"]] or "",
                    partido=f[ix["PARTIDO"]] or "")

prov = Counter(); rows = []
for lid, r in loc.items():
    af = r[0]; tot = sum(af) or 1
    g = defaultdict(int)
    for i, v in enumerate(af):
        g[GRP.get(i, "OTROS")] += v
    for k, v in g.items():
        prov[k] += v
    sh = {k: 100 * v / tot for k, v in g.items()}
    gan = max(orden, key=lambda k: sh.get(k, 0))
    m = LUG.get(lid, {})
    rows.append(dict(id=lid, nom=m.get("nombre", lid), dep=m.get("depto", ""), tipo=m.get("tipo", ""),
                     pob=m.get("pob", 0), int_=m.get("intendente", ""), par=m.get("partido", ""),
                     gan=gan, sh={k: round(v, 1) for k, v in sh.items()},
                     af=tot, pad=r[4], par_tot=round(100 * (tot + r[1] + r[2] + r[3]) / r[4], 1) if r[4] else None,
                     blanco=round(100 * r[1] / (tot + r[1] + r[2] + r[3]), 1) if (tot + r[1] + r[2] + r[3]) else None))
rows.sort(key=lambda x: x["nom"])

TOT = sum(prov.values())
PCT = {k: 100 * prov[k] / TOT for k in orden}

# --- diputados cordobeses y disidencia recalculada (mayoría del bloque en cada acta)
v = json.load(open(VOTOS, encoding="utf-8"))
dips, actas = v["dips"], v["actas"]
dis, vot, af_v = Counter(), Counter(), Counter()
for a in actas:
    byb = defaultdict(list)
    for s, c in a["votos"].items():
        if c in ("AF", "NE"):
            byb[dips[s]["b"]].append(c)
    maj = {b: Counter(l).most_common(1)[0][0] for b, l in byb.items()}
    for s, c in a["votos"].items():
        if c not in ("AF", "NE"):
            continue
        vot[s] += 1
        if c == "AF":
            af_v[s] += 1
        if c != maj[dips[s]["b"]]:
            dis[s] += 1

fichas = json.load(open(FICHAS, encoding="utf-8"))["dips"]
cord = [p for p in fichas if (p.get("d") or "").upper() == "CORDOBA"]
BLOC2G = {"LA LIBERTAD AVANZA": "LLA", "PROVINCIAS UNIDAS": "PU", "DEFENDAMOS CÓRDOBA": "DC",
          "UNIÓN POR LA PATRIA": "FP", "UCR - UNIÓN CÍVICA RADICAL": "UCR", "PRO": "OTROS"}
DIP = []
for p in cord:
    s = p["s"]
    e2025 = (p.get("p") or "").startswith("10/12/2025") or (p.get("p") or "").startswith("12/02/2026")
    DIP.append(dict(n=p["n"], s=s, b=p["b"], p=p.get("p", ""), e2025=e2025, g=BLOC2G.get(p["b"], "OTROS"),
                    vot=vot[s], af=af_v[s], dis=dis[s], pdis=round(100 * dis[s] / max(1, vot[s]), 1),
                    x=p.get("x", 0)))
DIP.sort(key=lambda x: (not x["e2025"], -x["vot"], -x["dis"]))
bancas = Counter(x["g"] for x in DIP if x["e2025"])
BANCAS = {k: bancas.get(k, 0) for k in orden}
n_local = Counter(r["gan"] for r in rows)
hab_local = Counter()
for r in rows:
    hab_local[r["gan"]] += r["pob"]
pob_tot = sum(LUG[l]["pob"] for l in LUG)
chicos = [r["sh"].get("LLA", 0) for r in rows if r["pob"] < 5000]
grandes = [r["sh"].get("LLA", 0) for r in rows if r["pob"] >= 5000]
lla_ch = sum(chicos) / max(1, len(chicos))
lla_gr = sum(grandes) / max(1, len(grandes))
sin_banca = sum(prov[k] for k in ["FP","PL","UCR","FIT"])

# --- departamentos
dep = defaultdict(lambda: defaultdict(float))
for r in rows:
    for k, val in r["sh"].items():
        dep[r["dep"]][k] += val * r["af"]
DEP = []
for k, g in dep.items():
    t = sum(g.values()) or 1
    DEP.append((k, 100 * g["LLA"] / t, 100 * g["PU"] / t))
DEP.sort(key=lambda x: -x[1])

def nf(n):
    return f"{n:,}".replace(",", ".")

# --- tabla de fuerzas
FILAS_F = "".join(
    f'<tr><td><span class="dot b{k}"></span>{NOMBRE[k]}</td>'
    f'<td class="num">{nf(prov[k])}</td>'
    f'<td class="num">{PCT[k]:.1f}%</td>'
    f'<td class="num">{BANCAS[k] if BANCAS[k] else "—"}</td>'
    f'<td class="num soft">{nf(round(prov[k]/BANCAS[k])) if BANCAS[k] else "sin banca"}</td></tr>'
    for k in orden)

FILAS_L = "".join(
    f'<tr><td>{html.escape(NOMBRE[k])}</td><td class="num">{n_local.get(k,0)}</td>'
    f'<td class="num">{nf(hab_local.get(k,0))}</td>'
    f'<td class="num">{100*hab_local.get(k,0)/pob_tot:.1f}%</td></tr>'
    for k in orden if n_local.get(k))

FILAS_D = "".join(
    f'<tr class="{"e25" if x["e2025"] else ""}"><td><a href="/diputado/{x["s"]}">{html.escape(x["n"])}</a>'
    f'{" <span class=v2025>2025</span>" if x["e2025"] else ""}</td>'
    f'<td class="soft">{html.escape(x["b"])}</td>'
    f'<td class="num">{x["vot"]}</td><td class="num">{x["dis"]}</td>'
    f'<td class="num {"warn" if x["pdis"] >= 10 else ""}">{x["pdis"]:.1f}%</td>'
    f'<td class="num soft">{x["x"]:+.0f}</td></tr>'
    for x in DIP)

FILAS_LOC = "".join(
    f'<tr data-b="{html.escape((r["nom"]+" "+r["dep"]+" "+r["int_"]).lower())}">'
    f'<td>{html.escape(r["nom"])}</td><td class="soft">{html.escape(r["dep"].title())}</td>'
    f'<td class="num">{nf(r["pob"])}</td>'
    f'<td class="soft">{html.escape(r["int_"])}<em>{html.escape(r["par"])}</em></td>'
    f'<td><span class="tag b{r["gan"]}">{r["gan"]}</span></td>'
    f'<td class="num">{r["sh"].get("LLA",0):.0f}%</td>'
    f'<td class="num">{r["sh"].get("PU",0):.0f}%</td>'
    f'<td class="num">{r["par_tot"] if r["par_tot"] is not None else "—"}%</td></tr>'
    for r in rows)

FILAS_DEP = "".join(f'<tr><td>{html.escape(k.title())}</td><td class="num">{a:.1f}%</td>'
                    f'<td class="num">{b:.1f}%</td></tr>' for k, a, b in DEP[:8])

HTML = f"""<!DOCTYPE html>
<html lang="es-AR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Córdoba · cómo votaron sus diputados y dónde ganó cada fuerza</title>
<meta name="description" content="Los 1.941.359 votos de las generales 2025 en Córdoba, localidad por localidad, cruzados con cómo votaron los 18 diputados cordobeses en el período 144.">
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
.dek {{ font-size:17px; color:var(--muted); max-width:720px; margin:0; }}
.cifras {{ display:grid; grid-template-columns:repeat(4,1fr); gap:1px; background:var(--rule); border-bottom:1px solid var(--rule-strong); }}
.cifra {{ background:var(--paper); padding:24px 28px 22px; }}
.cifra b {{ display:block; font-family:"IBM Plex Mono",monospace; font-size:28px; font-weight:500; letter-spacing:-.02em; margin-bottom:4px; }}
.cifra span {{ font-size:12.5px; color:var(--muted); line-height:1.35; display:block; }}
section {{ padding:44px 0 10px; }}
h2 {{ font-size:22px; font-weight:600; letter-spacing:-.01em; margin:0 0 6px; }}
h2 span {{ font-weight:300; color:var(--soft); font-size:15px; }}
p.intro {{ color:var(--muted); max-width:760px; margin:0 0 24px; font-size:15.5px; }}
table {{ width:100%; border-collapse:collapse; font-size:14.5px; }}
th {{ text-align:left; font-family:"IBM Plex Mono",monospace; font-size:10.5px; letter-spacing:.09em; text-transform:uppercase; color:var(--soft); font-weight:500; padding:0 10px 9px 0; border-bottom:1px solid var(--rule-strong); }}
td {{ padding:9px 10px 9px 0; border-bottom:1px solid var(--rule); vertical-align:baseline; }}
td.num, th.num {{ text-align:right; font-family:"IBM Plex Mono",monospace; font-size:13.5px; padding-right:14px; white-space:nowrap; }}
td.soft {{ color:var(--muted); }}
td.warn {{ color:var(--warn); font-weight:500; }}
td em {{ display:block; font-style:normal; font-size:11.5px; color:var(--soft); }}
td a {{ color:var(--ink); text-decoration:none; border-bottom:1px solid var(--rule-strong); }}
tr.e25 td {{ background:#fffdf7; }}
.v2025 {{ font-family:"IBM Plex Mono",monospace; font-size:10px; letter-spacing:.08em; color:#7a6a3f; border:1px solid #e6dcc0; border-radius:2px; padding:1px 4px; margin-left:6px; }}
.dot {{ display:inline-block; width:9px; height:9px; border-radius:50%; margin-right:8px; vertical-align:1px; }}
.tag {{ font-family:"IBM Plex Mono",monospace; font-size:11px; letter-spacing:.04em; padding:2px 6px; border-radius:2px; background:#efece5; }}
.bLLA {{ background:#6b4fa8; }} .dot.bLLA {{ background:#6b4fa8; }}
.bPU {{ background:#2f6fa8; }} .dot.bPU {{ background:#2f6fa8; }}
.bDC {{ background:#b5442f; }} .dot.bDC {{ background:#b5442f; }}
.bFP {{ background:#3f7d6b; }} .dot.bFP {{ background:#3f7d6b; }}
.bPL {{ background:#b8912a; }} .dot.bPL {{ background:#b8912a; }}
.bUCR {{ background:#8a5a12; }} .dot.bUCR {{ background:#8a5a12; }}
.bFIT {{ background:#8e1b3f; }} .dot.bFIT {{ background:#8e1b3f; }}
.bOTROS {{ background:#7a7386; }} .dot.bOTROS {{ background:#7a7386; }}
.tag.bLLA,.tag.bPU,.tag.bDC,.tag.bFP,.tag.bPL,.tag.bUCR,.tag.bFIT {{ color:#fff; }}
.buscador {{ display:flex; gap:12px; align-items:center; margin:0 0 14px; flex-wrap:wrap; }}
.buscador input {{ flex:1; min-width:220px; font:inherit; font-size:15px; padding:10px 14px; border:1px solid var(--rule-strong); border-radius:2px; background:var(--card); }}
.buscador .cuenta {{ font-family:"IBM Plex Mono",monospace; font-size:12px; color:var(--soft); }}
.scroll {{ max-height:620px; overflow-y:auto; border-bottom:1px solid var(--rule-strong); }}
.tbox {{ overflow-x:auto; -webkit-overflow-scrolling:touch; }}
.scroll thead th {{ position:sticky; top:0; background:var(--paper); z-index:1; }}
.metodo {{ background:var(--card); border:1px solid var(--rule); border-radius:3px; padding:26px 28px; margin:44px 0 10px; }}
.metodo h2 {{ margin-bottom:12px; }}
.metodo p {{ color:var(--muted); font-size:14.5px; margin:0 0 12px; max-width:840px; }}
.metodo p:last-child {{ margin-bottom:0; }}
footer {{ padding:26px 0 60px; color:var(--soft); font-size:12.5px; }}
.nota {{ font-size:13px; color:var(--soft); margin:12px 0 0; }}
@media (max-width:760px) {{
  .cifras {{ grid-template-columns:repeat(2,1fr); }}
  .wrap {{ padding:0 18px; }}
  header.hero {{ padding:38px 0 22px; }}
  table {{ font-size:13px; }}
  th,td {{ padding-right:8px; }}
  td.num,th.num {{ padding-right:8px; font-size:12.5px; }}
  #tf th:nth-child(2), #tf td:nth-child(2), #tf th:nth-child(5), #tf td:nth-child(5) {{ display:none; }}
  #tl th:nth-child(2), #tl td:nth-child(2), #tl th:nth-child(4), #tl td:nth-child(4),
  #tl th:nth-child(7), #tl td:nth-child(7), #tl th:nth-child(8), #tl td:nth-child(8) {{ display:none; }}
  #tl td:first-child {{ max-width:150px; }}
  #td th:nth-child(2), #td td:nth-child(2), #td th:nth-child(6), #td td:nth-child(6) {{ display:none; }}
  .scroll {{ max-height:none; }}
  table {{ font-size:12px; }}
  th {{ font-size:9.5px; letter-spacing:.04em; }}
}}
</style>
</head>
<body>

<nav class="top"><div class="wrap">
  <a class="brand" href="/">Corvus Lab</a>
  <div><a href="/congreso">Congreso</a> · <a href="/mapa">Mapa</a> · <a href="/disidencias">Disidencias</a> · <a href="/afinidad">Afinidad</a> · <a href="/proyectos">Trabajos</a></div>
</div></nav>

<header class="hero"><div class="wrap">
  <div class="kicker">Córdoba · Diputados nacionales 2025 · Período 144</div>
  <h1>Nueve de cada diez cordobeses viven donde ganó La Libertad Avanza</h1>
  <p class="dek">Los {nf(TOT)} votos afirmativos de las generales de 2025, localidad por localidad de las 427 que tiene la provincia, cruzados con la actuación de los 18 diputados que Córdoba tiene en la Cámara.</p>
</div></header>

<div class="cifras">
  <div class="cifra"><b>{nf(TOT)}</b><span>votos afirmativos en las 427 localidades</span></div>
  <div class="cifra"><b>{100*hab_local["LLA"]/pob_tot:.0f}%</b><span>de la población vive en una localidad donde ganó LLA</span></div>
  <div class="cifra"><b>{BANCAS["LLA"]} · {BANCAS["PU"]} · {BANCAS["DC"]}</b><span>bancas de LLA, PU y Defendamos Córdoba en la renovación</span></div>
  <div class="cifra"><b>{100*sin_banca/TOT:.1f}%</b><span>de los votos fue a FP, PL, UCR y FIT: cero bancas</span></div>
</div>

<section><div class="wrap">
  <h2>Voto y bancas <span>· sobre votos afirmativos</span></h2>
  <p class="intro">Córdoba renueva la mitad de sus 18 bancas. El reparto es por sistema D'Hondt sobre una sola circunscripción provincial, así que la relación entre votos y bancas no es lineal: los últimos escalones se pagan caro.</p>
  <div class="tbox"><table id="tf">
    <thead><tr><th>Fuerza</th><th class="num">Votos</th><th class="num">%</th><th class="num">Bancas</th><th class="num">Votos por banca</th></tr></thead>
    <tbody>{FILAS_F}</tbody>
  </table></div>
</div></section>

<section><div class="wrap">
  <h2>Dónde ganó cada fuerza <span>· localidades y habitantes</span></h2>
  <p class="intro">LLA se impuso en {n_local.get("LLA",0)} localidades que reúnen el {100*hab_local.get("LLA",0)/pob_tot:.0f}% de la población. Provincias Unidas ganó en {n_local.get("PU",0)} localidades que reúnen el {100*hab_local.get("PU",0)/pob_tot:.0f}%: son los pueblos chicos. En las de menos de 5.000 habitantes LLA saca {lla_ch:.1f}%; en las de 5.000 o más, {lla_gr:.1f}%.</p>
  <div class="tbox"><table>
    <thead><tr><th>Fuerza</th><th class="num">Localidades ganadas</th><th class="num">Habitantes</th><th class="num">% de la provincia</th></tr></thead>
    <tbody>{FILAS_L}</tbody>
  </table></div>
  <p class="nota">Habitantes según Censo 2022. La localidad ganadora es la que tuvo más votos afirmativos de la fuerza más votada en esa localidad.</p>
</div></section>

<section><div class="wrap">
  <h2>Los diputados de Córdoba <span>· cómo votaron</span></h2>
  <p class="intro">Los 18 diputados que la provincia tiene en la Cámara, ordenados por participación. En <b>2025</b> están los nueve que entraron por la elección de octubre de 2025; el resto viene del turno de 2023. La disidencia es la cantidad de votaciones en que el diputado se apartó de la posición mayoritaria de su propio bloque, sobre las votaciones en que estuvo presente.</p>
  <div class="tbox"><table id="td">
    <thead><tr><th>Diputado</th><th>Bloque</th><th class="num">Votó</th><th class="num">Disidencias</th><th class="num">%</th><th class="num">Eje</th></tr></thead>
    <tbody>{FILAS_D}</tbody>
  </table></div>
  <p class="nota">Eje: posición en el primer componente de las 33 votaciones nominales del período 144 (negativo a la izquierda del gráfico, positivo a la derecha). La disidencia se calcula contra la mayoría del bloque en cada acta, con abstenciones y ausentes fuera de la base. Es un criterio distinto del que usa el mapa de votaciones en su versión actual, que se está corrigiendo.</p>
</div></section>

<section><div class="wrap">
  <h2>Las 427 localidades <span>· quién ganó y con cuánto</span></h2>
  <div class="buscador">
    <input id="q" type="search" placeholder="Buscar localidad, departamento o intendente" autocomplete="off">
    <span class="cuenta" id="cuenta">{len(rows)} localidades</span>
  </div>
  <div class="scroll">
  <table id="tl">
    <thead><tr><th>Localidad</th><th>Departamento</th><th class="num">Hab.</th><th>Intendente</th><th>Ganó</th><th class="num">LLA</th><th class="num">PU</th><th class="num">Partic.</th></tr></thead>
    <tbody>{FILAS_LOC}</tbody>
  </table>
  </div>
  <p class="nota">Participación sobre padrón. Los porcentajes por fuerza son sobre votos afirmativos; blancos, nulos e impugnados no entran.</p>
</div></section>

<section><div class="wrap">
  <h2>Los extremos por departamento <span>· % LLA, ponderado por votos</span></h2>
  <p class="intro">El corte provincial esconde un país distinto en el noroeste. Los ocho departamentos con más voto a LLA y el más favorable a Provincias Unidas.</p>
  <div class="tbox"><table>
    <thead><tr><th>Departamento</th><th class="num">LLA</th><th class="num">PU</th></tr></thead>
    <tbody>{FILAS_DEP}
    <tr><td>{html.escape(DEP[-1][0].title())}</td><td class="num">{DEP[-1][1]:.1f}%</td><td class="num">{DEP[-1][2]:.1f}%</td></tr></tbody>
  </table></div>
</div></section>

<div class="wrap"><div class="metodo">
  <h2>Método y límites</h2>
  <p><b>Qué se cruzó.</b> El resultado de diputados nacionales de 2025 en cada una de las 427 localidades de Córdoba, y la actuación de los 18 diputados cordobeses en las 33 votaciones nominales del período 144 publicadas en los diarios de sesiones.</p>
  <p><b>De dónde salen los datos.</b> Resultados por localidad y población: 427.Cba sobre datos oficiales de la Justicia Electoral y el Censo 2022 del INDEC. Votaciones, bloques, distritos y mandatos: Cámara de Diputados de la Nación. Las 18 listas de la elección se agruparon en ocho fuerzas.</p>
  <p><b>Qué no dice.</b> Que la localidad y el diputado estén relacionados causalmente: la boleta de diputado nacional es la misma en toda la provincia, así que el corte local muestra dónde fue fuerte cada fuerza, no a quién eligió cada pueblo. Un diputado representa a toda la provincia, no a su localidad.</p>
  <p><b>Límite del indicador.</b> La disidencia mide comportamiento legislativo, no convicciones: votar distinto del bloque puede ser convicción, disciplina partidaria quebrada o un acuerdo previo. No dice si el voto fue acertado.</p>
</div></div>

<footer><div class="wrap">Corvus Lab · datos abiertos del Congreso · actualizado el 17 de noviembre de 2026</div></footer>

<script>
const q = document.getElementById('q'), cuenta = document.getElementById('cuenta');
const filas = [...document.querySelectorAll('#tl tbody tr')];
q.addEventListener('input', () => {{
  const t = q.value.trim().toLowerCase();
  let n = 0;
  for (const f of filas) {{
    const ok = !t || f.dataset.b.includes(t);
    f.style.display = ok ? '' : 'none';
    if (ok) n++;
  }}
  cuenta.textContent = t ? n + ' de ' + filas.length : filas.length + ' localidades';
}});
</script>
</body>
</html>"""

open(OUT, "w", encoding="utf-8").write(HTML)
print("escrito", OUT, len(HTML), "bytes |", len(rows), "localidades |", len(DIP), "diputados")
print("bancas:", BANCAS, "| sin banca:", nf(round(sin_banca)), f"({100*sin_banca/TOT:.1f}%)")
print("hab LLA:", round(100*hab_local['LLA']/pob_tot,1), "%")
