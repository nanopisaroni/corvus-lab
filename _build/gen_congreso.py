#!/usr/bin/env python3
# Genera congreso.html desde _build/data/diputados.json
# Fuente: Honorable Cámara de Diputados de la Nación.
import json, os, html, math

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(BASE, "_build", "data", "diputados.json")
OUT = os.path.join(BASE, "congreso.html")

d = json.load(open(SRC, encoding="utf-8"))
dips = d["diputados"]

TIPOS = ["LEY", "RESOLUCION", "DECLARACION"]


PARTICULAS = {"de", "del", "la", "las", "los", "por", "para", "y", "el"}


def bloque_txt(b):
    """Mayúsculas del sitio oficial, con partículas en minúscula y siglas intactas."""
    palabras = []
    for i, w in enumerate(b.split()):
        lw = w.lower()
        if lw in ("pro", "ucr", "mid", "pts", "fit", "unidad"):
            palabras.append(w.upper() if len(w) <= 5 else w.capitalize())
        elif lw in PARTICULAS:
            palabras.append(w.capitalize() if i == 0 else lw)
        else:
            palabras.append(w.capitalize())
    return " ".join(palabras)


def perfil(t):
    tot = sum(t.get(k, 0) for k in TIPOS)
    if tot == 0:
        return "sin datos", 0
    ley = t.get("LEY", 0)
    pct = round(100 * ley / tot)
    if pct >= 45:
        return "ley", pct
    if t.get("DECLARACION", 0) >= t.get("RESOLUCION", 0):
        return "declaracion", pct
    return "resolucion", pct


filas = []
for r in dips:
    t = r.get("tipos", {})
    tot_tipos = sum(t.get(k, 0) for k in TIPOS)
    p, pct = perfil(t)
    fv = min(1.0, math.log10(1 + r["total"]) / math.log10(301)) if r["total"] else 0.0
    idx = round(100 * (pct / 100) * (0.45 + 0.55 * fv), 1)
    asis = r.get("asist") or {}
    apct = asis.get("pct")
    idxg = round(idx * (0.6 + 0.4 * (apct / 100)), 1) if (apct is not None) else idx
    filas.append({
        "idx": idx,
        "ig": idxg,
        "as": apct,
        "aus": asis.get("a"),
        "lic": asis.get("l"),
        "re": asis.get("total"),
        "n": r["nombre"],
        "s": r.get("slug", ""),
        "b": r["bloque"],
        "d": r["distrito"],
        "t": r["total"],
        "ley": t.get("LEY", 0),
        "res": t.get("RESOLUCION", 0),
        "dec": t.get("DECLARACION", 0),
        "m": tot_tipos,
        "pct": pct,
        "p": p,
    })

filas.sort(key=lambda x: (-x["t"], x["n"]))
por_indice = sorted(filas, key=lambda x: -x["idx"])[:10]
por_volumen = sorted(filas, key=lambda x: -x["t"])[:10]


def fila_top(i, r, valor, unidad):
    return (f'<li><span class="pos">{i}</span>'
            f'<span class="nm">{html.escape(r["n"])}</span>'
            f'<span class="bl">{html.escape(bloque_txt(r["b"]))}</span>'
            f'<span class="vl">{valor}<em>{unidad}</em></span></li>')


TOP_IDX = "".join(fila_top(i, r, f'{r["idx"]:.0f}', " pts") for i, r in enumerate(por_indice, 1))
TOP_AUS = "".join(
    fila_top(i, r, f'{r["as"]}', "%") for i, r in enumerate(
        sorted([x for x in filas if x["as"] is not None], key=lambda x: (x["as"], -x["t"]))[:10], 1))
TOP_VOL = "".join(fila_top(i, r, f'{r["t"]:,}'.replace(",", "."), "") for i, r in enumerate(por_volumen, 1))
total_proy = sum(f["t"] for f in filas)
suma_ley = sum(f["ley"] for f in filas)
suma_res = sum(f["res"] for f in filas)
suma_dec = sum(f["dec"] for f in filas)
suma_m = suma_ley + suma_res + suma_dec
pct_ley = round(100 * suma_ley / suma_m)
pct_res = round(100 * suma_res / suma_m)
pct_dec = 100 - pct_ley - pct_res

bloques = sorted({f["b"] for f in filas if f["b"]})
distritos = sorted({f["d"] for f in filas if f["d"]})

DATA_JS = json.dumps(filas, ensure_ascii=False, separators=(",", ":"))
TOTAL_ES = f"{total_proy:,}".replace(",", ".")

HTML = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Los que legislan · Corvus Lab</title>
<meta name="description" content="Los 256 diputados de la Nación y qué presentan: cuántos proyectos, cuántos son ley y cuántos son declaraciones simbólicas. Datos de la Cámara de Diputados.">
<meta property="og:title" content="Los que legislan · Corvus Lab">
<meta property="og:description" content="256 diputados, {TOTAL_ES} proyectos: la mitad de lo que se presenta no es ley.">
<meta property="og:type" content="article">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Public+Sans:wght@300;400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
:root {{
  --paper: #f8f6f2;
  --card: #ffffff;
  --ink: #16130f;
  --muted: #6d665c;
  --soft: #999083;
  --rule: #e2dcd1;
  --rule-strong: #c9c1b3;
  --ley: #1f5c3d;
  --res: #8a5a12;
  --dec: #7a2f24;
  --accent: #16130f;
}}
* {{ box-sizing: border-box; }}
html {{ -webkit-text-size-adjust: 100%; }}
body {{
  margin: 0; background: var(--paper); color: var(--ink);
  font-family: "Public Sans", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  font-size: 16px; line-height: 1.55; font-weight: 400;
  -webkit-font-smoothing: antialiased;
}}
.wrap {{ max-width: 1080px; margin: 0 auto; padding: 0 28px; }}
.mono {{ font-family: "IBM Plex Mono", ui-monospace, SFMono-Regular, Menlo, monospace; }}

nav.top {{ border-bottom: 1px solid var(--rule); background: var(--paper); }}
nav.top .wrap {{ display: flex; align-items: baseline; justify-content: space-between; height: 56px; }}
nav.top a {{ color: var(--ink); text-decoration: none; }}
.brand {{ font-weight: 600; letter-spacing: -.01em; font-size: 15px; }}
.brand em {{ font-style: normal; color: var(--soft); font-weight: 400; }}
nav.top ul {{ list-style: none; display: flex; gap: 22px; margin: 0; padding: 0; font-size: 13.5px; color: var(--muted); }}
nav.top ul a {{ color: var(--muted); }}
nav.top ul a:hover {{ color: var(--ink); }}

header.hero {{ padding: 64px 0 40px; border-bottom: 1px solid var(--rule); }}
.kicker {{ font-family: "IBM Plex Mono", monospace; font-size: 11.5px; letter-spacing: .14em;
  text-transform: uppercase; color: var(--soft); margin-bottom: 22px; }}
h1 {{ font-size: clamp(38px, 6vw, 62px); line-height: 1.02; letter-spacing: -.035em;
  font-weight: 600; margin: 0 0 22px; max-width: 15ch; }}
.lede {{ font-size: 19px; line-height: 1.5; color: #3d382f; max-width: 62ch; margin: 0; }}
.lede strong {{ font-weight: 600; color: var(--ink); }}

.cifras {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 1px; background: var(--rule);
  border-top: 1px solid var(--rule); border-bottom: 1px solid var(--rule); }}
.cifra {{ background: var(--paper); padding: 24px 22px 22px; }}
.cifra .num {{ font-size: 32px; letter-spacing: -.03em; font-weight: 500; line-height: 1;
  font-family: "IBM Plex Mono", monospace; }}
.cifra .lbl {{ font-size: 12.5px; color: var(--muted); margin-top: 9px; line-height: 1.35; }}

section {{ padding: 52px 0; border-bottom: 1px solid var(--rule); }}
h2 {{ font-size: 13px; letter-spacing: .12em; text-transform: uppercase; font-weight: 600;
  color: var(--muted); margin: 0 0 26px; font-family: "IBM Plex Mono", monospace; }}
h2 span {{ color: var(--soft); font-weight: 400; letter-spacing: .06em; }}

.barra {{ display: flex; height: 46px; border-radius: 2px; overflow: hidden; margin-bottom: 18px;
  border: 1px solid var(--rule-strong); }}
.barra div {{ display: flex; align-items: center; justify-content: center; color: #fff;
  font-size: 12.5px; font-weight: 500; letter-spacing: .02em; }}
.b-ley {{ background: var(--ley); }}
.b-res {{ background: var(--res); }}
.b-dec {{ background: var(--dec); }}
.leyenda {{ display: flex; gap: 26px; flex-wrap: wrap; font-size: 13.5px; color: var(--muted); }}
.leyenda i {{ display: inline-block; width: 9px; height: 9px; border-radius: 1px; margin-right: 7px; }}

.controles {{ display: grid; grid-template-columns: 1.6fr 1fr 1fr 1fr; gap: 12px; margin-bottom: 18px; }}
.controles input, .controles select {{
  width: 100%; padding: 10px 12px; border: 1px solid var(--rule-strong); background: var(--card);
  font-family: inherit; font-size: 14px; color: var(--ink); border-radius: 2px; appearance: none;
}}
.controles input:focus, .controles select:focus {{ outline: 2px solid var(--ink); outline-offset: -1px; }}
.resumen {{ font-size: 13px; color: var(--muted); margin-bottom: 14px; font-family: "IBM Plex Mono", monospace; }}

table {{ width: 100%; border-collapse: collapse; font-size: 14.5px; }}
thead th {{ position: sticky; top: 0; background: var(--paper); text-align: left; font-weight: 500;
  font-size: 11.5px; letter-spacing: .09em; text-transform: uppercase; color: var(--muted);
  border-bottom: 1px solid var(--rule-strong); padding: 10px 8px; z-index: 2; }}
tbody td {{ padding: 11px 8px; border-bottom: 1px solid var(--rule); vertical-align: middle; }}
tbody tr:hover {{ background: #f1eee7; }}
td.num, th.num {{ text-align: right; font-family: "IBM Plex Mono", monospace; font-variant-numeric: tabular-nums; }}
td.nombre {{ font-weight: 500; }}
td.nombre a {{ color: inherit; text-decoration: none; border-bottom: 1px solid transparent; }}
td.nombre a:hover {{ border-bottom-color: var(--rule-strong); }}
td.bloque, td.dist {{ color: var(--muted); font-size: 13px; }}
.tag {{ display: inline-block; padding: 2px 8px; border-radius: 2px; font-size: 11px;
  letter-spacing: .05em; text-transform: uppercase; font-family: "IBM Plex Mono", monospace; }}
.t-ley {{ background: #e3efe7; color: var(--ley); }}
.t-res {{ background: #f6ecd9; color: var(--res); }}
.t-dec {{ background: #f6e6e3; color: var(--dec); }}
.mini {{ display: inline-flex; height: 6px; width: 74px; border-radius: 1px; overflow: hidden;
  background: var(--rule); vertical-align: middle; }}
.mini i {{ display: block; height: 100%; }}

.nota {{ font-size: 15px; color: #464036; max-width: 72ch; margin: 0 0 28px; line-height: 1.6; }}
.nota strong {{ font-weight: 600; color: var(--ink); }}
.nota.pie {{ margin: 26px 0 0; font-size: 13.5px; color: var(--muted); }}
.dos {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 34px; }}
.dos h3 {{ font-size: 12px; letter-spacing: .1em; text-transform: uppercase; font-weight: 600;
  color: var(--muted); margin: 0 0 14px; font-family: "IBM Plex Mono", monospace; }}
ol.rank {{ list-style: none; margin: 0; padding: 0; border-top: 1px solid var(--rule-strong); }}
ol.rank li {{ display: grid; grid-template-columns: 26px 1fr auto auto; gap: 10px; align-items: baseline;
  padding: 9px 0; border-bottom: 1px solid var(--rule); font-size: 14.5px; }}
ol.rank .pos {{ color: var(--soft); font-family: "IBM Plex Mono", monospace; font-size: 12px; }}
ol.rank .nm {{ font-weight: 500; }}
ol.rank .bl {{ color: var(--soft); font-size: 11.5px; max-width: 13ch; overflow: hidden;
  text-overflow: ellipsis; white-space: nowrap; }}
ol.rank .vl {{ font-family: "IBM Plex Mono", monospace; font-variant-numeric: tabular-nums; }}
ol.rank .vl em {{ font-style: normal; color: var(--soft); font-size: 11px; }}
@media (max-width: 980px) {{ .dos {{ grid-template-columns: 1fr; gap: 34px; }} }}
.metodo {{ font-size: 14px; color: var(--muted); max-width: 74ch; }}
.metodo p {{ margin: 0 0 14px; }}
.metodo a {{ color: var(--ink); text-underline-offset: 3px; }}
footer {{ padding: 40px 0 64px; font-size: 13px; color: var(--soft); }}
footer a {{ color: var(--muted); }}

@media (max-width: 860px) {{
  .cifras {{ grid-template-columns: repeat(2, 1fr); }}
  .controles {{ grid-template-columns: 1fr 1fr; }}
  .oculto-movil {{ display: none; }}
  header.hero {{ padding: 44px 0 32px; }}
  .wrap {{ padding: 0 18px; }}
}}
@media (max-width: 520px) {{
  .controles {{ grid-template-columns: 1fr; }}
  .cifra .num {{ font-size: 26px; }}
}}
</style>
</head>
<body>

<nav class="top">
  <div class="wrap">
    <a class="brand" href="/">Corvus Lab <em>· trabajos</em></a>
    <ul>
      <li><a href="/proyectos">Trabajos</a></li>
      <li><a href="/coleccion">Colección</a></li>
    </ul>
  </div>
</nav>

<header class="hero">
  <div class="wrap">
    <div class="kicker">Cámara de Diputados de la Nación · período 2023–2027</div>
    <h1>Los que legislan</h1>
    <p class="lede">Cada diputado presenta proyectos. Algunos son leyes que cambian algo. Muchos son
      declaraciones que felicitan a un pueblo por su aniversario. Esta página cuenta qué presenta
      cada uno de los <strong>256 diputados</strong> en ejercicio, con los datos de la propia Cámara.</p>
  </div>
</header>

<div class="cifras">
  <div class="cifra"><div class="num">256</div><div class="lbl">diputados en ejercicio</div></div>
  <div class="cifra"><div class="num">{TOTAL_ES}</div><div class="lbl">proyectos presentados en el período</div></div>
  <div class="cifra"><div class="num">{pct_res}%</div><div class="lbl">son resoluciones, en su mayoría simbólicas</div></div>
  <div class="cifra"><div class="num">{pct_ley}%</div><div class="lbl">son proyectos de ley</div></div>
</div>

<section>
  <div class="wrap">
    <h2>De qué está hecha la producción <span>· últimos 20 proyectos de cada diputado</span></h2>
    <div class="barra">
      <div class="b-ley" style="width:{pct_ley}%">{pct_ley}% ley</div>
      <div class="b-res" style="width:{pct_res}%">{pct_res}% resolución</div>
      <div class="b-dec" style="width:{pct_dec}%">{pct_dec}% declaración</div>
    </div>
    <div class="leyenda">
      <span><i class="b-ley"></i>Proyecto de ley: crea, modifica o deroga una norma</span>
      <span><i class="b-res"></i>Resolución: expresa una posición o pide algo al Ejecutivo</span>
      <span><i class="b-dec"></i>Declaración: reconoce o celebra, sin efecto jurídico</span>
    </div>
  </div>
</section>

<section>
  <div class="wrap">
    <h2>Dos rankings que casi no se tocan <span>· volumen y sustancia</span></h2>
    <p class="nota">Presentar más proyectos no guarda relación con presentar mejores proyectos. La correlación entre
      cantidad y proporción de leyes, entre los 256 diputados, es de <strong>−0,02</strong>: prácticamente cero.
      Por eso van los dos por separado y no uno solo.</p>
    <div class="dos">
      <div>
        <h3>Quiénes más presentan</h3>
        <ol class="rank">{TOP_VOL}</ol>
      </div>
      <div>
        <h3>Quiénes más legislan</h3>
        <ol class="rank">{TOP_IDX}</ol>
      </div>
      <div>
        <h3>Quiénes menos van</h3>
        <ol class="rank">{TOP_AUS}</ol>
      </div>
    </div>
    <p class="nota pie">La asistencia sale del registro oficial del período 144: ocho reuniones entre el 1 de marzo
      y el 21 de octubre de 2026, contando asamblea legislativa, sesiones especiales e informativa. El promedio del
      cuerpo es 94,5% y 170 diputados no faltaron a ninguna. Las licencias y misiones oficiales no cuentan como
      ausencia, pero sí bajan el porcentaje.</p>
    <p class="nota pie">El índice combina la proporción de proyectos de ley con el volumen, que entra con rendimiento
      decreciente: satura a los 300 proyectos. Va de 0 a 100 y es una convención, no una verdad. Cambiar los pesos
      mueve el orden de la mitad de la tabla, así que conviene leerlo como una forma de mirar, no como un veredicto.</p>
  </div>
</section>

<section>
  <div class="wrap">
    <h2>Todos los diputados <span>· ordenados por cantidad de proyectos</span></h2>
    <div class="controles">
      <input id="q" type="search" placeholder="Buscar por nombre, bloque o distrito" autocomplete="off">
      <select id="fb"><option value="">Todos los bloques</option>{''.join(f'<option value="{html.escape(b)}">{html.escape(bloque_txt(b))}</option>' for b in bloques)}</select>
      <select id="fd"><option value="">Todos los distritos</option>{''.join(f'<option value="{html.escape(x)}">{html.escape(x.title())}</option>' for x in distritos)}</select>
      <select id="fo">
        <option value="total">Más proyectos</option>
        <option value="indice">Mayor índice</option>
        <option value="asis">Menor asistencia</option>
        <option value="asis_desc">Mayor asistencia</option>
        <option value="ley">Más proyectos de ley</option>
        <option value="pct">Mayor proporción de ley</option>
        <option value="menos">Menos proyectos</option>
        <option value="nombre">Nombre A–Z</option>
      </select>
    </div>
    <div class="resumen" id="resumen"></div>
    <table>
      <thead><tr>
        <th class="num" style="width:44px">#</th>
        <th>Diputado</th>
        <th class="oculto-movil">Bloque</th>
        <th class="oculto-movil">Distrito</th>
        <th class="num">Proyectos</th>
        <th class="num">Ley</th>
        <th class="num oculto-movil">Resol.</th>
        <th class="num oculto-movil">Decl.</th>
        <th class="num">Asist.</th>
        <th class="num">Índice</th>
        <th>Perfil</th>
      </tr></thead>
      <tbody id="tb"></tbody>
    </table>
  </div>
</section>

<section>
  <div class="wrap">
    <h2>Cómo se hizo</h2>
    <div class="metodo">
      <p>Los datos salen del sitio oficial de la <a href="https://www.hcdn.gob.ar/diputados/" target="_blank" rel="noopener">Honorable Cámara de Diputados de la Nación</a>. Para cada diputado se toma el total de proyectos que informa su ficha y la composición de sus últimos veinte, que es la única página del listado que se lee de forma pareja para todos.</p>
      <p>El total incluye los proyectos que el diputado firma como autor y también los que solo cofirma. Es la cifra que publica la Cámara en su ficha, pero conviene leerla como participación en proyectos y no como autoría exclusiva. Un número alto puede significar mucha iniciativa propia o mucha firma al pie de proyectos ajenos, y esta página no distingue entre las dos.</p>
      <p>Las tres columnas de tipo —ley, resolución, declaración— suman veinte por diputado, salvo para quienes presentaron menos. El porcentaje de ley se calcula sobre ese conjunto, así que mide el perfil reciente y no la carrera completa. El total de la izquierda sí es el del período completo.</p>
      <p>El índice se calcula así: proporción de proyectos de ley en la muestra, multiplicada por un factor de volumen que crece con el total presentado y satura a los 300 proyectos, para que una sola ley entre veinte proyectos no encabece la tabla. La fórmula completa está en el generador. No mide calidad, ni resultado, ni si el proyecto era bueno: mide qué proporción de lo que presenta cada diputado es una norma y no un gesto.</p>
      <p>La asistencia se informa aparte y no entra en el índice, porque mide otra cosa: estar no dice nada sobre qué se presenta, y presentar mucho no dice nada sobre estar. Se muestran separadas para que cada una se juzgue por su cuenta.</p>
      <p>Un proyecto de ley puede ser declarativo y una resolución puede tener efecto real. La clasificación describe la forma del instrumento, no su importancia. Cada fila enlaza a la ficha oficial, donde está el detalle.</p>
      <p>Extracción: {d['extraido']}. Los datos cambian cuando la Cámara actualiza sus listados.</p>
    </div>
  </div>
</section>

<footer>
  <div class="wrap">
    Corvus Lab · <a href="/proyectos">otros trabajos</a>
  </div>
</footer>

<script>
const DATA = {DATA_JS};
const T = {{"ley":"t-ley","resolucion":"t-res","declaracion":"t-dec"}};
const LBL = {{"ley":"Ley","resolucion":"Resolución","declaracion":"Declaración"}};
const q = document.getElementById('q'), fb = document.getElementById('fb'),
      fd = document.getElementById('fd'), fo = document.getElementById('fo'),
      tb = document.getElementById('tb'), resumen = document.getElementById('resumen');

function pct(a,b) {{ return b ? Math.round(100*a/b) : 0; }}

function render() {{
  const term = q.value.trim().toLowerCase();
  let rows = DATA.filter(r => {{
    if (fb.value && r.b !== fb.value) return false;
    if (fd.value && r.d !== fd.value) return false;
    if (term) {{
      const s = (r.n + ' ' + r.b + ' ' + r.d).toLowerCase();
      if (!s.includes(term)) return false;
    }}
    return true;
  }});
  const ord = fo.value;
  rows.sort((a,b) => {{
    if (ord === 'total') return b.t - a.t || a.n.localeCompare(b.n);
    if (ord === 'menos') return a.t - b.t || a.n.localeCompare(b.n);
    if (ord === 'ley') return b.ley - a.ley || b.t - a.t;
    if (ord === 'indice') return b.idx - a.idx || b.t - a.t;
    if (ord === 'asis') return (a.as ?? 999) - (b.as ?? 999) || b.t - a.t;
    if (ord === 'asis_desc') return (b.as ?? -1) - (a.as ?? -1) || b.t - a.t;
    if (ord === 'pct') return (b.m?b.pct:-1) - (a.m?a.pct:-1) || b.ley - a.ley;
    return a.n.localeCompare(b.n);
  }});
  tb.innerHTML = rows.map((r,i) => {{
    const pl = pct(r.ley, r.m), pr = pct(r.res, r.m), pd = 100 - pl - pr;
    return `<tr>
      <td class="num" style="color:var(--soft)">${{i+1}}</td>
      <td class="nombre">${{r.s ? `<a href="https://www.hcdn.gob.ar/diputados/${{r.s}}/" target="_blank" rel="noopener">${{esc(r.n)}}</a>` : esc(r.n)}}</td>
      <td class="bloque oculto-movil">${{esc(r.b)}}</td>
      <td class="dist oculto-movil">${{esc(r.d)}}</td>
      <td class="num">${{r.t.toLocaleString('es-AR')}}</td>
      <td class="num">${{r.ley}}</td>
      <td class="num oculto-movil">${{r.res}}</td>
      <td class="num oculto-movil">${{r.dec}}</td>
      <td class="num">${{r.as === null ? '—' : r.as + '%'}}</td>
      <td class="num">${{Math.round(r.idx)}}</td>
      <td><span class="tag ${{T[r.p]||''}}">${{LBL[r.p]||'—'}}</span>
        <span class="mini" title="ley ${{pl}}% · resolución ${{pr}}% · declaración ${{pd}}%">
          <i style="width:${{pl}}%;background:var(--ley)"></i><i style="width:${{pr}}%;background:var(--res)"></i><i style="width:${{pd}}%;background:var(--dec)"></i>
        </span></td>
    </tr>`;
  }}).join('');
  const tp = rows.reduce((s,r)=>s+r.t,0);
  resumen.textContent = `${{rows.length}} diputados · ${{tp.toLocaleString('es-AR')}} proyectos`;
}}
function esc(s) {{ return String(s).replace(/[&<>"]/g, c => ({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}})[c]); }}
[q,fb,fd,fo].forEach(el => el.addEventListener('input', render));
render();
</script>
</body>
</html>
"""

open(OUT, "w", encoding="utf-8").write(HTML)
print(f"OK congreso.html · {len(HTML):,} bytes · {len(filas)} diputados · {total_proy:,} proyectos")
