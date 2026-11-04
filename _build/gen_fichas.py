#!/usr/bin/env python3
# Genera diputado/<slug>.html: una ficha por diputado (período 144).
# Entrada: _build/data/fichas.json. Salida: diputado/*.html
import json, os, html, re, unicodedata

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(BASE, "_build", "data", "fichas.json")
OUTDIR = os.path.join(BASE, "diputado")

D = json.load(open(SRC, encoding="utf-8"))
META, DIPS = D["meta"], D["dips"]
PERIODO = META.get("periodo", 144)
SITIO = "https://corvus-lab.vercel.app"

PARTICULAS = {"de", "del", "la", "las", "los", "por", "para", "y", "el", "e"}
SIGLAS = {"pro", "ucr", "mid", "pts", "fit", "eva", "pst", "cba"}


def titulo(t):
    """Mayúsculas de origen -> capitalización institucional (misma regla que mapa.html)."""
    out = []
    for i, w in enumerate(str(t).split()):
        lw = w.lower()
        if lw in SIGLAS:
            out.append(w.upper())
        elif lw in PARTICULAS:
            out.append(w.capitalize() if i == 0 else lw)
        else:
            out.append(w.capitalize())
    return " ".join(out)


def esc(t):
    return html.escape(str(t), quote=True)


def slugify(t):
    t = unicodedata.normalize("NFD", str(t).lower())
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    t = re.sub(r"[^a-z0-9]+", "-", t).strip("-")
    return t or "diputado"


def num(n):
    """Entero con separador de miles argentino."""
    return f"{n:,}".replace(",", ".")


def dec(v, nd=1):
    """Decimal con coma."""
    return f"{v:.{nd}f}".replace(".", ",")


def pct_txt(v, nd=0):
    return dec(v, nd) + "%"


def plural(n, sing, plur):
    return sing if n == 1 else plur


def num_auto(v, nd=1):
    """Decimal con coma, sin ceros de cola (97,1 / 100 / 0)."""
    s = f"{v:.{nd}f}"
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    return s.replace(".", ",")


def pct_auto(v, nd=1):
    return num_auto(v, nd) + "%"


def resto_txt(res, dec_):
    """Qué queda cuando se descuentan las leyes, según lo que haya en la muestra."""
    if res and dec_:
        return "resoluciones y declaraciones"
    if res:
        return "resoluciones"
    if dec_:
        return "declaraciones"
    return ""


def truncar(s, n=180):
    s = " ".join(str(s).split())
    cortado = len(s) > n
    if cortado:
        s = s[:n]
    # el sumario de origen viene cortado a mitad de palabra: cerrar en palabra completa y marcarlo
    if cortado or (len(s) >= 175 and s[-1] not in ".!?)\"'"):
        if " " in s:
            s = s[: s.rfind(" ")]
        s = s.rstrip(" ,.;:") + "…"
    return s


def bloque_txt(b):
    return titulo(b)


CSS = """
:root {
  --paper: #f8f6f2; --card: #ffffff; --ink: #16130f; --muted: #6d665c;
  --soft: #999083; --rule: #e2dcd1; --rule-strong: #c9c1b3;
}
* { box-sizing: border-box; }
html { -webkit-text-size-adjust: 100%; }
body { margin: 0; background: var(--paper); color: var(--ink);
  font-family: "Public Sans", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  font-size: 16px; line-height: 1.55; -webkit-font-smoothing: antialiased; }
.wrap { max-width: 1080px; margin: 0 auto; padding: 0 28px; }
.mono { font-family: "IBM Plex Mono", monospace; }
a { color: var(--ink); }
nav.top { border-bottom: 1px solid var(--rule); }
nav.top .wrap { display: flex; justify-content: space-between; align-items: baseline; padding: 14px 28px; }
nav.top a { color: var(--muted); text-decoration: none; font-size: 13px; }
nav.top a:hover { color: var(--ink); }
nav.top .brand { font-family: "IBM Plex Mono", monospace; font-size: 12px; letter-spacing: .12em;
  text-transform: uppercase; color: var(--ink); }
nav.top .links a { margin-left: 20px; }
header.hero { padding: 48px 0 26px; border-bottom: 1px solid var(--rule-strong); }
.kicker { font-family: "IBM Plex Mono", monospace; font-size: 11.5px; letter-spacing: .14em;
  text-transform: uppercase; color: var(--soft); margin-bottom: 14px; }
h1 { font-size: clamp(28px, 4.4vw, 42px); line-height: 1.08; letter-spacing: -.02em;
  font-weight: 600; margin: 0 0 14px; }
.filiacion { font-family: "IBM Plex Mono", monospace; font-size: 13px; color: var(--muted);
  margin: 0; letter-spacing: .01em; }
.filiacion .sep { color: var(--rule-strong); padding: 0 8px; }
.cifras { display: grid; grid-template-columns: repeat(5, 1fr); gap: 1px; background: var(--rule);
  border-bottom: 1px solid var(--rule-strong); }
.hero-cifras { padding-top: 0; }
.cifra { background: var(--paper); padding: 22px 20px 20px; }
.cifra b { display: block; font-family: "IBM Plex Mono", monospace; font-size: 27px; font-weight: 500;
  letter-spacing: -.02em; margin-bottom: 6px; font-variant-numeric: tabular-nums; }
.cifra span { font-size: 12px; color: var(--muted); line-height: 1.4; display: block; }
.lectura { padding: 34px 0 8px; }
.lectura p { font-size: 17px; line-height: 1.62; max-width: 790px; margin: 0; }
section { padding: 34px 0 10px; }
h2 { font-size: 20px; font-weight: 600; letter-spacing: -.01em; margin: 0 0 18px; }
h2 span { font-weight: 300; color: var(--soft); font-size: 14px; }
.tabla { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; font-size: 14px; min-width: 640px; }
th { text-align: left; font-family: "IBM Plex Mono", monospace; font-size: 10.5px; letter-spacing: .1em;
  text-transform: uppercase; color: var(--soft); font-weight: 500; padding: 0 10px 10px;
  border-bottom: 1px solid var(--rule-strong); }
td { padding: 10px; border-bottom: 1px solid var(--rule); vertical-align: top; }
td.mono { white-space: nowrap; }
th:first-child, td:first-child { padding-left: 0; }
th:last-child, td:last-child { padding-right: 0; }
td .tipo { font-family: "IBM Plex Mono", monospace; font-size: 11px; letter-spacing: .06em; color: var(--muted); }
.sumario { color: var(--ink); }
.oficial { padding: 30px 0 0; }
.oficial a { font-family: "IBM Plex Mono", monospace; font-size: 13px; color: var(--ink);
  text-decoration: none; border-bottom: 1px solid var(--rule-strong); padding-bottom: 2px; }
.oficial a:hover { border-bottom-color: var(--ink); }
footer { border-top: 1px solid var(--rule); margin-top: 44px; padding: 22px 0 44px;
  color: var(--soft); font-size: 12.5px; }
@media (max-width: 900px) {
  .cifras { grid-template-columns: repeat(3, 1fr); }
}
@media (max-width: 760px) {
  .cifras { grid-template-columns: repeat(2, 1fr); }
  .cifra { padding: 18px 16px; }
  .cifra b { font-size: 24px; }
  header.hero { padding-top: 36px; }
}
"""


def cifras(p):
    ley, res, dec_ = p.get("ley") or 0, p.get("res") or 0, p.get("dec") or 0
    k = ley + res + dec_
    pct_ley = (ley * 100.0 / k) if k else None
    as_ = p.get("as")
    dis, vot = p.get("dis"), p.get("vot")
    x = p.get("x")

    c1 = (num(p.get("t") or 0), "proyectos presentados")
    c2 = (pct_txt(pct_ley) if pct_ley is not None else "-",
          f"{ley} de {k} {plural(k, 'proyecto', 'proyectos')} de la muestra")
    c3 = (pct_txt(as_) if as_ is not None else "-",
          f"ausencias: {p.get('aus') or 0} · licencias: {p.get('lic') or 0}")
    if dis is not None and vot:
        c4 = (pct_auto(dis * 100.0 / vot), f"{dis} de {vot} votaciones computadas")
    else:
        c4 = ("-", "sin votaciones computadas")
    if x is not None:
        c5 = (("+" if x > 0 else "") + num_auto(x), "eje de votaciones, de -100 a 100")
    else:
        c5 = ("-", "sin posición calculada")
    out = []
    for val, lab in (c1, c2, c3, c4, c5):
        out.append(f'<div class="cifra"><b>{esc(val)}</b><span>{esc(lab)}</span></div>')
    return "\n      ".join(out), pct_ley


def lectura(p, pct_ley):
    t = p.get("t") or 0
    ley, res, dec_ = p.get("ley") or 0, p.get("res") or 0, p.get("dec") or 0
    k = ley + res + dec_
    as_, dis, vot, x = p.get("as"), p.get("dis"), p.get("vot"), p.get("x")
    frases = []

    if t == 0 and k == 0:
        frases.append("No registra proyectos presentados en el período.")
    elif t == 0:
        frases.append("No registra proyectos presentados en el total del período.")
    elif t == 1:
        frases.append("Presentó 1 proyecto en el período.")
    else:
        frases.append(f"Presentó {num(t)} proyectos en el período.")

    if k:
        partes = []
        if ley:
            partes.append(f"{ley} {plural(ley, 'ley', 'leyes')}")
        if res:
            partes.append(f"{res} {plural(res, 'resolución', 'resoluciones')}")
        if dec_:
            partes.append(f"{dec_} {plural(dec_, 'declaración', 'declaraciones')}")
        if len(partes) > 1:
            detalle = ", ".join(partes[:-1]) + " y " + partes[-1]
        else:
            detalle = partes[0]
        if t == 0:
            frases.append(f"La muestra tiene {k} {plural(k, 'proyecto clasificado', 'proyectos clasificados')}: {detalle}.")
        else:
            frases.append(
                f"En la muestra de {k} {plural(k, 'proyecto clasificado', 'proyectos clasificados')}: {detalle}."
            )
        if pct_ley is not None:
            resto = resto_txt(res, dec_)
            if ley == 0:
                frases.append(f"No hay proyectos de ley en la muestra. Lo clasificado son {resto}.")
            elif pct_ley < 25:
                frases.append(f"La mayoría de lo que presenta son {resto}.")
            elif pct_ley < 35:
                frases.append(f"Las leyes son cerca de un tercio de la muestra. El resto son {resto}.")
            elif pct_ley < 50:
                frases.append(f"Las leyes ocupan entre un tercio y la mitad de la muestra. El resto son {resto}.")
            elif pct_ley == 50:
                frases.append(f"La mitad de la muestra son proyectos de ley. El resto son {resto}.")
            else:
                frases.append("La mayoría de la muestra son proyectos de ley.")

    if as_ is None:
        frases.append("No hay datos de asistencia para el período.")
    elif as_ < 80:
        frases.append(f"La asistencia a las votaciones es de {pct_txt(as_)}, por debajo del 80%.")
    elif as_ < 100:
        frases.append(f"Asistió al {pct_txt(as_)} de las votaciones del período.")
    else:
        frases.append("Asistió a todas las votaciones del período.")

    if dis is None or not vot:
        frases.append("No tiene votaciones computadas para medir su distancia con el bloque.")
    else:
        pdis = dis * 100.0 / vot
        if dis == 0:
            frases.append(
                "No registra votos contra su bloque en "
                + ("la única votación computada." if vot == 1 else f"las {vot} votaciones computadas.")
            )
        elif pdis > 15:
            frases.append(f"Votó contra su bloque en {dis} de {vot} votaciones computadas ({pct_auto(pdis)}).")
        else:
            frase_vot = "la única votación computada" if vot == 1 else f"{vot} votaciones computadas"
            frases.append(f"Votó contra su bloque en {dis} de {frase_vot} ({pct_auto(pdis)}).")

    if x is None:
        frases.append("No tiene posición calculada en el eje de votaciones.")
    else:
        frases.append(f"En el eje de votaciones, que va de -100 a 100, se ubica en {('+' if x > 0 else '')}{num_auto(x)}.")

    return " ".join(frases)


def fila(r):
    tipo = (r.get("t") or "").strip()
    return (
        "<tr>"
        f'<td><span class="tipo">{esc(tipo)}</span></td>'
        f'<td class="mono">{esc(r.get("exp") or "-")}</td>'
        f'<td class="mono">{esc(r.get("f") or "-")}</td>'
        f'<td class="sumario">{esc(truncar(r.get("s") or ""))}</td>'
        "</tr>"
    )


def pagina(p):
    nombre = p["n"]
    slug = p.get("s") or slugify(nombre)
    bloque = bloque_txt(p.get("b") or "")
    distrito = titulo(p.get("d") or "")
    periodo = p.get("p") or ""
    cifs, pct_ley = cifras(p)
    parrafo = lectura(p, pct_ley)
    recs = p.get("rec") or []
    filas = "\n        ".join(fila(r) for r in recs)
    desc = f"{nombre}, diputado por {distrito} en el bloque {bloque}. Proyectos, asistencia y votaciones en el período {PERIODO}."
    oficial = ""
    if p.get("s"):
        url = f"https://www.hcdn.gob.ar/diputados/{p['s']}/listado-proyectos.html"
        oficial = (
            '<div class="oficial">\n'
            f'      <a href="{esc(url)}" rel="noopener">Ficha oficial en HCDN &#8599;</a>\n'
            "    </div>"
        )

    tabla = ""
    if recs:
        tabla = f"""
    <section>
      <h2>Proyectos recientes <span>últimos {len(recs)} de la muestra</span></h2>
      <div class="tabla">
        <table>
          <thead><tr><th>Tipo</th><th>Expediente</th><th>Fecha</th><th>Sumario</th></tr></thead>
          <tbody>
        {filas}
          </tbody>
        </table>
      </div>
    </section>"""

    return f"""<!DOCTYPE html>
<html lang="es-AR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(nombre)} · Corvus Lab</title>
<meta name="description" content="{esc(desc)}">
<meta property="og:type" content="article">
<meta property="og:title" content="{esc(nombre)} · Corvus Lab">
<meta property="og:description" content="{esc(desc)}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Public+Sans:wght@300;400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>{CSS}</style>
</head>
<body>
<nav class="top">
  <div class="wrap">
    <a class="brand" href="/">Corvus Lab</a>
    <span class="links"><a href="/congreso">Congreso</a><a href="/mapa">Mapa</a></span>
  </div>
</nav>
<header class="hero">
  <div class="wrap">
    <div class="kicker">Cámara de Diputados · Período {PERIODO}</div>
    <h1>{esc(nombre)}</h1>
    <p class="filiacion">{esc(bloque)}<span class="sep">·</span>{esc(distrito)}<span class="sep">·</span>{esc(periodo)}</p>
  </div>
</header>
<div class="wrap hero-cifras">
  <div class="cifras">
      {cifs}
  </div>
</div>
<div class="lectura">
  <div class="wrap">
    <p>{esc(parrafo)}</p>
  </div>
</div>
<div class="wrap">{tabla}
    {oficial}
</div>
<footer>
  <div class="wrap">Corvus Lab · datos abiertos del Congreso</div>
</footer>
</body>
</html>
"""


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    # limpia sólo los html del directorio de salida para no dejar fichas viejas
    for f in os.listdir(OUTDIR):
        if f.endswith(".html"):
            os.remove(os.path.join(OUTDIR, f))
    vistos = {}
    for p in DIPS:
        slug = p.get("s") or slugify(p["n"])
        if slug in vistos:
            slug = f"{slugify(p['n'])}-2"
        vistos[slug] = True
        with open(os.path.join(OUTDIR, slug + ".html"), "w", encoding="utf-8") as fh:
            fh.write(pagina(p))
    print(f"{len(vistos)} fichas en {OUTDIR}")


if __name__ == "__main__":
    main()
