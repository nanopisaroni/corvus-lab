#!/usr/bin/env python3
"""Genera proyectos.html a partir de proyectos.json.

El JSON es la fuente de verdad. La home y esta página se arman de acá.
Uso: python3 _build/gen_proyectos.py
"""
import json
import os
import html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "proyectos.json")
OUT = os.path.join(ROOT, "proyectos.html")

CLASE_ESTADO = {"Publicado": "", "En curso": "wip", "Archivado": "arch"}


def esc(s):
    return html.escape(str(s), quote=True)


def fila(p, i):
    clase = CLASE_ESTADO.get(p["estado"], "")
    return f"""      <div class="project">
        <span class="p-idx">{i:02d}</span>
        <div>
          <span class="p-name"><a href="{esc(p['url'])}" target="_blank" rel="noopener">{esc(p['nombre'])}</a></span>
          <p class="p-detalle">{esc(p['detalle'])}</p>
        </div>
        <div class="p-desc">{esc(p['descripcion'])}</div>
        <span class="p-status {clase}">{esc(p['estado'])}</span>
      </div>"""


def main():
    d = json.load(open(DATA, encoding="utf-8"))
    proys = d["proyectos"]
    cats = d["categorias"]
    total = len(proys)
    publicados = sum(1 for p in proys if p["estado"] == "Publicado")
    en_curso = sum(1 for p in proys if p["estado"] == "En curso")

    secciones = []
    for c in cats:
        items = [p for p in proys if p["categoria"] == c["id"]]
        if not items:
            continue
        filas = "\n".join(fila(p, i + 1) for i, p in enumerate(items))
        secciones.append(f"""<section class="bloque" id="{esc(c['id'])}">
  <div class="container">
    <div class="sec-head">
      <h2>{esc(c['nombre'])}</h2>
      <span class="num">{len(items):02d}</span>
    </div>
    <p class="bajada">{esc(c['bajada'])}</p>
    <div class="list">
{filas}
    </div>
  </div>
</section>""")

    leyenda = "\n".join(
        f'      <div class="llave"><span class="p-status {CLASE_ESTADO.get(k, "")}">{esc(k)}</span>'
        f'<p>{esc(v)}</p></div>'
        for k, v in d["estados"].items()
    )

    doc = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Proyectos · Corvus Lab</title>
<meta name="description" content="Los proyectos de la línea pública de Corvus Lab: Estado, información pública, ciudadanía, investigación y participación.">
<meta property="og:title" content="Proyectos · Corvus Lab">
<meta property="og:description" content="{total} proyectos abiertos sobre lo que es de todos.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,300;9..144,400;9..144,500;9..144,600&family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
:root{{
  --bg:#070e18; --panel:#0c1626; --line:rgba(88,198,208,0.14);
  --text:#e8e4dc; --muted:#7d8a99; --soft:#55626f;
  --teal:#58C6D0; --warm:#D9A066;
  --sans:'Inter',system-ui,sans-serif; --serif:'Fraunces',Georgia,serif; --mono:'JetBrains Mono',monospace;
}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:var(--sans);background:var(--bg);color:var(--text);line-height:1.65;-webkit-font-smoothing:antialiased;overflow-x:hidden}}
.container{{max-width:960px;margin:0 auto;padding:0 32px}}
a{{color:var(--teal);text-decoration:none;border-bottom:1px solid rgba(88,198,208,0.25);transition:border-color .2s,color .2s}}
a:hover{{color:#8fdfe6;border-color:#8fdfe6}}
.grain{{position:fixed;inset:0;pointer-events:none;z-index:0;opacity:.025;background-image:radial-gradient(circle at 20% 20%,rgba(255,255,255,.4) .4px,transparent .6px);background-size:14px 14px}}
.grid-lines{{position:fixed;inset:0;pointer-events:none;z-index:0;opacity:.5;background-image:linear-gradient(var(--line) 1px,transparent 1px),linear-gradient(90deg,var(--line) 1px,transparent 1px);background-size:96px 96px;mask-image:radial-gradient(ellipse 90% 70% at 50% 20%,#000 0%,transparent 75%)}}
.eyebrow{{font-family:var(--mono);font-size:11px;letter-spacing:.28em;text-transform:uppercase;color:var(--teal)}}
nav{{position:fixed;top:0;left:0;right:0;z-index:100;padding:22px 0;background:linear-gradient(180deg,rgba(7,14,24,.92),rgba(7,14,24,0))}}
nav .container{{display:flex;justify-content:space-between;align-items:center}}
.brand{{font-family:var(--serif);font-weight:500;font-size:17px;color:var(--text);border:0}}
.brand em{{font-style:italic;color:var(--teal)}}
.nav-links{{display:flex;gap:28px}}
.nav-links a{{border:0;color:var(--muted);font-family:var(--mono);font-size:11px;letter-spacing:.14em;text-transform:uppercase}}
.nav-links a:hover{{color:var(--text)}}
header.hero{{padding:170px 0 80px;position:relative;z-index:1}}
.hero h1{{font-family:var(--serif);font-weight:400;font-size:clamp(44px,7vw,76px);line-height:1.02;letter-spacing:-.02em;margin:18px 0 30px}}
.hero h1 .n{{font-style:italic;color:var(--teal)}}
.hero .def{{font-size:clamp(17px,2.2vw,20px);font-weight:300;color:var(--muted);max-width:680px;line-height:1.6}}
.hero .cuentas{{display:flex;gap:38px;margin-top:44px;flex-wrap:wrap}}
.hero .cuenta .v{{font-family:var(--serif);font-size:30px;color:var(--text);line-height:1}}
.hero .cuenta .l{{font-family:var(--mono);font-size:10px;letter-spacing:.2em;text-transform:uppercase;color:var(--soft);margin-top:8px;display:block}}
.llaves{{border-top:1px solid var(--line);border-bottom:1px solid var(--line);padding:30px 0;position:relative;z-index:1;background:var(--panel)}}
.llaves .container{{display:grid;grid-template-columns:repeat(3,1fr);gap:32px}}
.llave .p-status{{display:inline-block;margin-bottom:10px}}
.llave p{{font-size:13px;color:var(--muted);line-height:1.55}}
section.bloque{{position:relative;z-index:1;padding:74px 0;border-top:1px solid var(--line)}}
section.bloque:first-of-type{{border-top:0}}
.sec-head{{display:flex;align-items:baseline;justify-content:space-between;margin-bottom:14px;gap:24px}}
.sec-head h2{{font-family:var(--serif);font-weight:400;font-size:clamp(27px,3.8vw,38px);letter-spacing:-.01em}}
.sec-head .num{{font-family:var(--mono);font-size:12px;color:var(--soft)}}
.bajada{{font-size:15px;color:var(--muted);max-width:600px;margin-bottom:38px}}
.list{{border-top:1px solid var(--line)}}
.project{{display:grid;grid-template-columns:44px 1.25fr 1fr auto;gap:26px;padding:32px 4px;border-bottom:1px solid var(--line);align-items:start;transition:background .2s}}
.project:hover{{background:rgba(88,198,208,.03)}}
.p-idx{{font-family:var(--mono);font-size:12px;color:var(--warm);padding-top:5px}}
.p-name{{font-family:var(--serif);font-weight:500;font-size:20px;line-height:1.25}}
.p-name a{{border:0;color:var(--text)}}
.p-name a:hover{{color:var(--teal)}}
.p-detalle{{font-size:13px;color:var(--soft);line-height:1.55;margin-top:9px;font-weight:300}}
.p-desc{{font-size:13.5px;color:var(--muted);line-height:1.55;font-style:italic;font-family:var(--serif);font-weight:300;padding-top:3px}}
.p-status{{font-family:var(--mono);font-size:9.5px;letter-spacing:.16em;text-transform:uppercase;color:var(--teal);border:1px solid rgba(88,198,208,.35);padding:4px 8px;white-space:nowrap;margin-top:2px}}
.p-status.wip{{color:var(--warm);border-color:rgba(217,160,102,.4)}}
.p-status.arch{{color:var(--soft);border-color:rgba(85,98,111,.4)}}
footer{{border-top:1px solid var(--line);padding:52px 0 44px;position:relative;z-index:1}}
footer .container{{display:flex;justify-content:space-between;align-items:flex-end;gap:24px;flex-wrap:wrap}}
.f-brand{{font-family:var(--serif);font-size:18px}}
.f-brand em{{font-style:italic;color:var(--teal)}}
.f-mantra{{font-family:var(--mono);font-size:11px;letter-spacing:.2em;text-transform:uppercase;color:var(--soft)}}
.f-copy{{font-family:var(--mono);font-size:10px;color:var(--soft);letter-spacing:.1em;width:100%;margin-top:26px}}
@media(max-width:820px){{
  .llaves .container{{grid-template-columns:1fr;gap:22px}}
  .project{{grid-template-columns:1fr;gap:10px}}
  .p-status{{justify-self:start}}
  .nav-links{{display:none}}
  header.hero{{padding:130px 0 60px}}
}}
</style>
</head>
<body>
<div class="grain"></div>
<div class="grid-lines"></div>

<nav>
  <div class="container">
    <a href="/" class="brand">Corvus<em> Lab</em></a>
    <div class="nav-links">
      <a href="/">Inicio</a>
      <a href="/coleccion">Colección</a>
      <a href="/dashboard">Dashboard</a>
    </div>
  </div>
</nav>

<header class="hero">
  <div class="container">
    <p class="eyebrow">{esc(d['linea'])}</p>
    <h1>Once proyectos<br>sobre lo que <span class="n">es de todos</span></h1>
    <p class="def">{esc(d['definicion'])}</p>
    <div class="cuentas">
      <div class="cuenta"><span class="v">{total}</span><span class="l">Proyectos</span></div>
      <div class="cuenta"><span class="v">{publicados}</span><span class="l">Publicados</span></div>
      <div class="cuenta"><span class="v">{en_curso}</span><span class="l">En curso</span></div>
    </div>
  </div>
</header>

<div class="llaves">
  <div class="container">
{leyenda}
  </div>
</div>

{chr(10).join(secciones)}

<footer>
  <div class="container">
    <div>
      <div class="f-brand">Corvus<em> Lab</em></div>
      <p style="font-family:var(--mono);font-size:10px;letter-spacing:.12em;text-transform:uppercase;color:var(--soft);margin-top:10px">
        <a href="https://corvus-lab.vercel.app/dashboard" style="border:0;color:var(--soft)">Estado interno del Lab → dashboard</a>
      </p>
      <div class="f-mantra" style="margin-top:8px">Encontrar · Construir · Publicar · Repetir</div>
    </div>
    <div class="f-copy">Actualizado {esc(d['actualizado'])} · Corvus Lab, Argentina</div>
  </div>
</footer>
</body>
</html>
"""
    open(OUT, "w", encoding="utf-8").write(doc)
    print(f"escrito {OUT} · {total} proyectos · {len(secciones)} categorías · {len(doc)} bytes")


if __name__ == "__main__":
    main()
