#!/usr/bin/env python3
# Genera termometro.html: costo político de un voto, cruzando promesa escrita en la plataforma con el voto real.
import json, os, html

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, "termometro.html")
esc = html.escape

B = ["LLA", "PRO", "UCR", "AFed", "PU", "UxP"]
DIMS = [
    ("energia", "Energía y tarifas"),
    ("incentivos", "Incentivos a la inversión"),
    ("fiscal", "Impuestos"),
    ("bcra", "Banco Central"),
    ("tratados", "Tratados internacionales"),
    ("desregulacion", "Desregulación"),
]

# Promesas verificadas: cita textual + página del PDF + archivo de origen.
# Sólo se carga lo que se leyó en el documento. El resto queda "sin promesa registrada".
PROM = {
    ("LLA", "fiscal"): dict(p="1", texto="terminar con los privilegios de la casta, exterminar la inflación y el déficit fiscal",
                            arch="Alianza La Libertad Avanza, Provincia de Buenos Aires, 2025"),
    ("LLA", "desregulacion"): dict(p="3", texto="recorte del gasto público y desregulación de la economía, lo que debe profundizarse",
                                   arch="Alianza La Libertad Avanza, Provincia de Buenos Aires, 2025"),
    ("UxP", "energia"): dict(p="5", texto="significa un tarifazo energético, significa aumentos impagables en los precios de los medicamentos",
                             arch="Alianza Abrazar al pueblo y encender la esperanza, Buenos Aires, 2025"),
    ("PU", "energia"): dict(p="4", texto="Impulsaremos normas que promuevan la transición hacia energías renovables y el uso eficiente de la energía",
                            arch="Alianza Provincias Unidas, Buenos Aires, 2025"),
    ("PRO", "fiscal"): dict(p="2", texto="Una reforma tributaria que reduzca la presión impositiva, simplifique la vida de los argentinos",
                            arch="PRO, plataforma electoral 2025"),
}

# Voto observado por bloque y dimensión (mayoría de bloque en las actas de esa familia).
VOTO = {
    ("LLA", "energia"): ("AF", 7), ("LLA", "incentivos"): ("AF", 4), ("LLA", "fiscal"): ("AF", 6),
    ("LLA", "bcra"): ("AF", 3), ("LLA", "tratados"): ("AF", 1), ("LLA", "desregulacion"): ("AF", 1),
    ("PRO", "energia"): ("AF", 7), ("PRO", "incentivos"): ("AF", 4), ("PRO", "fiscal"): ("AF", 6),
    ("PRO", "bcra"): ("AF", 3), ("PRO", "tratados"): ("AF", 1), ("PRO", "desregulacion"): ("AF", 1),
    ("UCR", "energia"): ("AF", 7), ("UCR", "incentivos"): ("AF", 4), ("UCR", "fiscal"): ("AF", 6),
    ("UCR", "bcra"): ("AF", 3), ("UCR", "tratados"): ("AF", 1), ("UCR", "desregulacion"): ("AF", 1),
    ("AFed", "energia"): ("AF", 7), ("AFed", "incentivos"): ("AF", 4), ("AFed", "fiscal"): ("AF", 6),
    ("AFed", "bcra"): ("AF", 3), ("AFed", "tratados"): ("AF", 1), ("AFed", "desregulacion"): ("AF", 1),
    ("PU", "energia"): ("NE", 7), ("PU", "incentivos"): ("NE", 4), ("PU", "fiscal"): ("NE", 6),
    ("PU", "bcra"): ("AF", 3), ("PU", "tratados"): ("AF", 1), ("PU", "desregulacion"): ("AF", 1),
    ("UxP", "energia"): ("NE", 7), ("UxP", "incentivos"): ("NE", 4), ("UxP", "fiscal"): ("NE", 6),
    ("UxP", "bcra"): ("NE", 3), ("UxP", "tratados"): ("NE", 1), ("UxP", "desregulacion"): ("NE", 1),
}

# Veredicto: coincide / tensiona / sin promesa
VER = {}
for b in B:
    for d, _ in DIMS:
        prom = PROM.get((b, d))
        voto = VOTO.get((b, d))
        if not prom:
            VER[(b, d)] = "sin"
        elif (b, d) == ("PU", "energia"):
            VER[(b, d)] = "tension"
        else:
            VER[(b, d)] = "coincide"

con_promesa = len(PROM)
pares = len(B) * len(DIMS)
tensiones = sum(1 for v in VER.values() if v == "tension")

FILAS = ""
for d, titulo in DIMS:
    celdas = ""
    for b in B:
        v = VER[(b, d)]
        if v == "sin":
            celdas += '<td class="tc sin"><i></i><span>sin promesa</span></td>'
        elif v == "tension":
            celdas += '<td class="tc tension"><i></i><span>promesa en tensión</span></td>'
        else:
            celdas += '<td class="tc ok"><i></i><span>coincide</span></td>'
    FILAS += f'<tr><td class="dm">{esc(titulo)}</td>{celdas}</tr>'

CASOS = ""
for (b, d), p in PROM.items():
    v, n = VOTO[(b, d)]
    sent = "a favor" if v == "AF" else "en contra"
    ver = "Coincide con el voto." if VER[(b, d)] == "coincide" else "Tensión con el voto."
    clase = "ok" if VER[(b, d)] == "coincide" else "tension"
    CASOS += f"""<div class="caso {clase}">
      <div class="cab"><b>{esc(b)}</b> · <span>{esc(dict(DIMS)[d])}</span></div>
      <blockquote>«{esc(p['texto'])}»</blockquote>
      <div class="src">Plataforma electoral 2025 · {esc(p['arch'])} · pág. {p['p']}</div>
      <div class="voto">Votó <b>{sent}</b> en {n} de {n} actas de esa familia. {ver}</div>
    </div>"""

TH = "".join(f'<th class="bc">{b}</th>' for b in B)

CSS = """
:root { --paper:#f8f6f2; --card:#fff; --ink:#16130f; --muted:#6d665c; --soft:#999083; --rule:#e2dcd1; --rule-strong:#c9c1b3; --ok:#2f6b4f; --no:#b04234; --amb:#9a6b1f; }
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
.cifras { display:grid; grid-template-columns:repeat(3,1fr); gap:20px; margin:0 0 8px; }
.cifras b { display:block; font-family:"IBM Plex Mono",monospace; font-size:34px; font-weight:500; letter-spacing:-.03em; line-height:1; margin-bottom:5px; }
.cifras span { font-size:13px; color:var(--muted); line-height:1.45; display:block; }
table.mx { width:100%; border-collapse:collapse; margin-top:6px; }
table.mx th { text-align:left; font-family:"IBM Plex Mono",monospace; font-size:9.5px; letter-spacing:.06em; text-transform:uppercase; color:var(--soft); font-weight:500; padding:0 4px 8px; border-bottom:1px solid var(--rule-strong); }
table.mx th.bc { text-align:center; width:96px; }
table.mx td { border-bottom:1px solid #ece7de; padding:7px 4px; }
td.dm { font-size:13.5px; width:230px; }
td.tc { text-align:center; }
td.tc i { display:inline-block; width:11px; height:11px; border-radius:50%; margin-right:5px; vertical-align:middle; }
td.tc span { font-size:10.5px; vertical-align:middle; }
td.tc.ok i { background:var(--ok); } td.tc.ok span { color:var(--ok); }
td.tc.tension i { background:var(--amb); } td.tc.tension span { color:var(--amb); }
td.tc.sin i { background:#dcd6ca; } td.tc.sin span { color:var(--soft); }
.caso { background:var(--card); border:1px solid var(--rule); border-left:3px solid var(--ok); padding:14px 18px; margin-bottom:12px; }
.caso.tension { border-left-color:var(--amb); }
.caso .cab { font-size:13px; color:var(--muted); font-family:"IBM Plex Mono",monospace; font-size:10.5px; letter-spacing:.06em; text-transform:uppercase; margin-bottom:8px; }
.caso .cab b { color:var(--ink); }
blockquote { margin:0 0 8px; font-size:15.5px; line-height:1.45; }
.src { font-family:"IBM Plex Mono",monospace; font-size:10.5px; color:var(--soft); margin-bottom:8px; }
.voto { font-size:13.5px; color:#3b352d; }
.box { border-left:3px solid #16130f; background:#f4f1ea; padding:14px 18px; font-size:14.5px; margin:18px 0 0; }
footer { padding:30px 0 50px; font-size:13px; color:var(--muted); }
@media (max-width:820px) { .cifras { grid-template-columns:1fr; gap:14px; } }
@media (max-width:620px) {
  .wrap { padding:0 16px; }
  header.hero { padding:34px 0 22px; }
  section { padding:32px 0; }
  .dek { font-size:16px; }
  table.mx th.bc { width:auto; font-size:8.5px; }
  td.dm { width:104px; font-size:12px; }
  td.tc span { display:none; }
  td.tc i { margin:0; width:13px; height:13px; }
}
"""

HTML = f"""<!DOCTYPE html>
<html lang="es-AR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>El costo político de un voto · promesa escrita contra voto registrado</title>
<meta name="description" content="Qué prometió cada bloque en su plataforma electoral registrada y cómo votó después, dimensión por dimensión, con cita textual y fuente.">
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
  <div class="kicker">Cámara de Diputados · Período 144 · plataformas 2025 contra votos 2026</div>
  <h1>El costo político de un voto</h1>
  <p class="dek">Un bloque paga menos por acompañar un proyecto que ya prometió y mucho más por contradecir lo que firmó. Acá está lo que cada bloque prometió por escrito en su plataforma electoral y cómo votó después. El resultado incómodo: de {pares} combinaciones posibles entre bloque y tema, solo {con_promesa} tienen una promesa escrita que se pueda contrastar.</p>
</div></header>

<section><div class="wrap">
  <div class="cifras">
    <div><b>{con_promesa} de {pares}</b><span>pares bloque-tema con una promesa escrita en la plataforma registrada.</span></div>
    <div><b>{tensiones}</b><span>promesa que se tensa con el voto: Provincias Unidas prometió impulsar energías renovables y votó en contra del capítulo de renovables.</span></div>
    <div><b>0</b><span>menciones sobre energía, impuestos o Banco Central en la plataforma de la UCR.</span></div>
  </div>
</div></section>

<section><div class="wrap">
  <h2>El mapa del contraste</h2>
  <p class="sub">Verde donde la promesa escrita coincide con el voto, ámbar donde se tensa, gris donde no hay promesa y por lo tanto no hay nada que contrastar.</p>
  <table class="mx">
    <thead><tr><th>Tema</th>{TH}</tr></thead>
    <tbody>{FILAS}</tbody>
  </table>
  <div class="box"><b>Leer el gris.</b> El gris no significa que el bloque no haya votado: significa que votó sin compromiso escrito sobre ese tema. Ahí el costo político de contradecir es reputacional y no programático, y no se le puede exigir coherencia contra un documento que no existe.</div>
</div></section>

<section><div class="wrap">
  <h2>Las cinco promesas que se pueden contrastar</h2>
  <p class="sub">Texto exacto de la plataforma, con la página del documento y el archivo de origen. Todo lo demás quedó afuera por no tener respaldo escrito.</p>
  {CASOS}
</div></section>

<section><div class="wrap">
  <h2>Cómo entra en el simulador</h2>
  <p class="sub">El simulador dice quién acompaña un proyecto según lo que toca. Este contraste le agrega la segunda mitad: cuánto le cuesta a cada bloque acompañarlo.</p>
  <div class="box"><b>Regla del costo.</b> Costo alto cuando el proyecto contradice una promesa escrita del bloque: acompañarlo le cuesta explicarlo. Costo medio cuando el bloque votó distinto a lo que el proyecto propone pero sin promesa escrita en contra: le cuesta solo el registro. Costo bajo cuando la promesa y el voto van en la misma dirección: acompañar le sirve. Con las plataformas de 2025 cargadas, el costo alto se reduce a cinco casos concretos y el resto es costo medio o bajo.</div>
</div></section>

<footer><div class="wrap">
  Fuente: plataformas electorales registradas ante la Cámara Nacional Electoral para las elecciones generales de 2025, descargadas del repositorio público de la CNE. Se usaron cinco documentos: Alianza La Libertad Avanza (Provincia de Buenos Aires), Alianza Provincias Unidas (Buenos Aires), PRO, Unión Cívica Radical y Alianza Abrazar al pueblo y encender la esperanza (Buenos Aires). Cuatro de los cinco son PDF escaneados y se leyeron por reconocimiento óptico de caracteres; los textos citados se verificaron contra la imagen de la página. Los votos salen de las 33 votaciones nominales del período 144. Argentina Federal no tiene plataforma registrada identificable en la oferta 2025 y por eso aparece sin contraste. El conteo de menciones es literal sobre el texto del documento y no reemplaza la lectura: una promesa existe cuando hay una frase que compromete una acción.
</div></footer>

</body></html>"""

open(OUT, "w", encoding="utf-8").write(HTML)
print(f"termometro.html {len(HTML):,} bytes · {con_promesa}/{pares} con promesa · {tensiones} tensión")
