#!/usr/bin/env python3
"""Genera proyectos.html a partir de proyectos.json.

Toma la hoja de estilo de index.html para que las dos páginas no se separen.
Uso: python3 _build/gen_proyectos.py  (desde la raíz del sitio)
"""
import html, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROMANOS = ["i", "ii", "iii", "iv", "v", "vi", "vii", "viii", "ix", "x"]
ESTADO_CLASE = {"Publicado": "", "En curso": "wip", "Archivado": "arch"}

EXTRA_CSS = """
.cuentas{display:flex;justify-content:center;gap:48px;margin:36px 0 0;flex-wrap:wrap}
.cuenta{text-align:center}
.cuenta .v{display:block;font-family:var(--display);font-size:44px;line-height:1}
.cuenta .l{font-variant:small-caps;text-transform:lowercase;letter-spacing:.14em;color:var(--gris);font-size:16px}
.llaves{margin:44px 0 0;border-top:1px solid var(--filete);border-bottom:1px solid var(--filete);padding:18px 0}
.llave{display:grid;grid-template-columns:110px 1fr;gap:14px;padding:5px 0;font-size:17px}
.llave .e{font-variant:small-caps;text-transform:lowercase;letter-spacing:.1em;color:var(--sangre)}
.llave p{color:var(--gris);font-style:italic}
.trabajo .detalle{font-size:17.5px;color:var(--gris);margin-top:8px}
.trabajo h3 .estado.wip{color:var(--sangre)}
"""


def esc(s):
    return html.escape(s, quote=True)


def main():
    d = json.load(open(os.path.join(ROOT, "proyectos.json"), encoding="utf-8"))
    index = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
    css = re.search(r"<style>(.*?)</style>", index, re.S).group(1) + EXTRA_CSS
    fuentes = re.search(r'(<link href="https://fonts.googleapis.com/css2[^>]+>)', index).group(1)

    proyectos = d["proyectos"]
    total = len(proyectos)
    publicados = sum(p["estado"] == "Publicado" for p in proyectos)
    en_curso = sum(p["estado"] == "En curso" for p in proyectos)

    secciones = []
    for i, c in enumerate(d["categorias"]):
        items = [p for p in proyectos if p["categoria"] == c["id"]]
        if not items:
            continue
        filas = []
        for j, p in enumerate(items, 1):
            externo = ' target="_blank" rel="noopener"' if p["url"].startswith("http") and "corvus-lab.vercel.app" not in p["url"] else ""
            url = p["url"].replace("https://corvus-lab.vercel.app", "") or "/"
            filas.append(f"""      <div class="trabajo">
        <span class="num">{j}</span>
        <h3><a href="{esc(url)}"{externo}>{esc(p["nombre"])}</a><span class="estado {ESTADO_CLASE.get(p["estado"], "")}">{esc(p["estado"].lower())}</span></h3>
        <p>{esc(p["descripcion"])}</p>
        <p class="detalle">{esc(p["detalle"])}</p>
      </div>""")
        secciones.append(f"""  <p class="ornamento" aria-hidden="true">✶ ✶ ✶</p>

  <section id="{c["id"]}">
    <div class="titulo-sec">
      <span class="rubro">{ROMANOS[i]}</span>
      <h2>{esc(c["nombre"])}</h2>
      <p class="bajada">{esc(c["bajada"])}</p>
    </div>
    <div class="trabajos">
{chr(10).join(filas)}
    </div>
  </section>
""")

    llaves = "\n".join(
        f'      <div class="llave"><span class="e">{esc(k.lower())}</span><p>{esc(v)}</p></div>'
        for k, v in d["estados"].items())

    sumario = "\n".join(
        f'      <li><span class="t"><a href="#{c["id"]}">{esc(c["nombre"])}</a></span><span class="relleno"></span><span class="n">{ROMANOS[i]}</span></li>'
        for i, c in enumerate(d["categorias"]))

    out = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Trabajos · Corvus Lab</title>
<meta name="description" content="{esc(d["definicion"])}">
<meta property="og:title" content="Trabajos · Corvus Lab">
<meta property="og:description" content="{esc(d["definicion"])}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
{fuentes}
<style>{css}</style>
</head>
<body>

<header class="cabecera">
  <div class="pliego">
    <div class="linea-sup"><span>Córdoba</span><span class="versalitas">{esc(d["linea"])}</span><span>MMXXVI</span></div>
    <h1 style="margin-top:56px;font-size:clamp(52px,12vw,104px)"><a href="/" style="border:0">CORVUS</a></h1>
    <p class="subtitulo">Trabajos sobre lo que es de todos</p>
    <div class="doble"></div>
    <nav>
      <a href="/">Portada</a>
      <a href="/coleccion">Colección</a>
      <a href="/#notas">Notas</a>
      <a href="/#correspondencia">Correspondencia</a>
    </nav>
  </div>
</header>

<div class="pliego">

  <section style="padding-bottom:24px">
    <div class="prosa"><p class="capitular">{esc(d["definicion"])}</p></div>
    <div class="cuentas">
      <div class="cuenta"><span class="v">{total}</span><span class="l">trabajos</span></div>
      <div class="cuenta"><span class="v">{publicados}</span><span class="l">publicados</span></div>
      <div class="cuenta"><span class="v">{en_curso}</span><span class="l">en curso</span></div>
    </div>
    <div class="llaves">
{llaves}
    </div>
  </section>

  <div class="sumario" style="padding-top:24px">
    <h2><span class="rubro">Sumario</span></h2>
    <ol>
{sumario}
    </ol>
  </div>

{"".join(secciones)}
</div>

<footer>
  <div class="pliego">
    <div class="marca">CORVUS LAB</div>
    <p>Índice puesto al día el {esc(d["actualizado"])}. Quien quiera ver el estado de las máquinas que sostienen estos trabajos puede consultar el <a href="/dashboard">tablero interno</a>.</p>
  </div>
</footer>

</body>
</html>
"""
    open(os.path.join(ROOT, "proyectos.html"), "w", encoding="utf-8").write(out)
    print(f"proyectos.html: {total} trabajos en {len(secciones)} secciones")


if __name__ == "__main__":
    main()
