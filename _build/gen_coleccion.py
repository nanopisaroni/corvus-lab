#!/usr/bin/env python3
"""Genera la colección Corvus Lab: la portada de la colección y una página por libro.

Estética: la de la portada del laboratorio (revista literaria de los años cincuenta:
papel, tinta y un rojo apagado, Libre Bodoni y EB Garamond). La hoja de estilo vive en
_build/estilo_coleccion.css, junto a este script.
"""
import json, os

ROOT = "/home/nanobot/projects/corvus-lab"
OUT_LIBRO = os.path.join(ROOT, "libro")
os.makedirs(OUT_LIBRO, exist_ok=True)
# indices.json vive junto a este script, en _build/
BASE = os.path.dirname(os.path.abspath(__file__))
INDICES = json.load(open(os.path.join(BASE, "indices.json"), encoding="utf-8"))

# ---------------------------------------------------------------- datos
LIBROS = [
 dict(
  slug="panteon", n="01", clase="Canon", t1="PANTEÓN", t2="PERSONAL",
  sub="Un mapa mental de dieciséis pensadores que me formaron",
  paginas="262 páginas", palabras=None, anio="2026",
  tesis="Dieciséis fichas, de Borges a Facundo Cabral: quién fue cada uno, qué ideas lo definen, por qué obra conviene entrar, cómo se vincula con los demás y qué concepto puede llevarse a la práctica.",
  cuerpo=[
   "Cada uno de los dieciséis está en el libro por una razón precisa. No están por prestigio ni por completitud: están porque dejaron una herramienta mental que sigue en uso. Borges enseña a leer las bibliotecas como mapas. Feynman enseña a desconfiar de uno mismo con método. Taleb enseña a mirar el riesgo antes que el promedio.",
   "El libro no propone admiración. Propone uso. Cada capítulo cierra con los conceptos que se pueden aplicar y con las conexiones hacia los demás del panteón, porque el valor de una lista así está en los cruces: Popper con Deutsch, Munger con Kahneman, los estoicos con Watts.",
   "Es el volumen del que salen los otros cuatro. Las referencias que aparecen en el resto de la colección se eligen acá, y ese es el motivo por el que abre la serie.",
  ],
  indice=None,  # se arma con el canon
  canon=[
   ("01","Jorge Luis Borges"),("02","Richard Feynman"),("03","Nassim Nicholas Taleb"),
   ("04","David Deutsch"),("05","Peter Thiel"),("06","Karl Popper"),
   ("07","Charlie Munger"),("08","Daniel Kahneman"),("09","Paul Graham"),
   ("10","Naval Ravikant"),("11","Eliezer Yudkowsky"),("12","Marco Aurelio"),
   ("13","Epicteto (y Séneca)"),("14","Alan Watts"),("15","Jiddu Krishnamurti"),
   ("16","Facundo Cabral"),
  ],
  descargas=[
   ("PDF · castellano 2,1 MB", "https://nanopisaroni.vercel.app/books/panteon-personal.pdf", True),
   ("PDF · English edition", "https://nanopisaroni.vercel.app/books/panteon-en.pdf", False),
  ],
  sitio="https://nanopisaroni.vercel.app/panteon.html", sitioTxt="Leer en el sitio",
 ),
 dict(
  slug="soberania", n="02", clase="Protocolo", t1="SOBERANÍA", t2="COGNITIVA",
  sub="Protocolo para recuperar la atención, el deseo y el tiempo",
  paginas="33 páginas", palabras=None, anio="2026",
  tesis="Un protocolo en cuatro fases para recobrar el gobierno de la propia atención. Empieza por algo tan humilde como el lugar donde se carga el teléfono y concluye en la soberanía de los vínculos y de la comunidad.",
  cuerpo=[
   "El libro arranca donde está el problema y no donde queda más cómodo explicarlo. La primera intervención es el cargador: dónde duerme el teléfono, a qué hora entra a la habitación, qué pasa en los primeros veinte minutos del día. De ahí pasa a la infraestructura propia, después a las relaciones y al final a la comunidad.",
   "Desarrolla el concepto de soberanía cognitiva que formuló Juan Ruocco, lo lleva a la práctica y también lo discute. La advertencia del libro es explícita desde la primera página: esto no es autoayuda. Lo que se disputa acá es diseño, negocio y poder, y por eso se pelea con instrumentos y no con fuerza de voluntad.",
   "Se publica en dominio público y viene con las herramientas sueltas para trabajar: la bitácora de atención, los dos checklist, el test y el manifiesto.",
  ],
  indice=[
   ("∞","Filosofía operativa"),
   ("I","Fundamentos filosóficos: del biopoder a la colonialidad epistémica"),
   ("II","Fase 0 · Diagnóstico (días 1 a 7)"),
   ("III","Fase 1 · Defensa individual (días 8 a 44)"),
   ("IV","Fase 2 · Infraestructura (días 45 a 60)"),
   ("V","Fase 3 · Soberanía relacional y comunitaria (días 61 en adelante)"),
  ],
  canon=None,
  descargas=[
   ("PDF · 0,2 MB", "https://soberaniacognitiva.com.ar/descargas/soberania-cognitiva.pdf", True),
   ("Manifiesto", "https://soberaniacognitiva.com.ar/descargas/manifiesto.pdf", False),
   ("Checklist de diagnóstico", "https://soberaniacognitiva.com.ar/descargas/checklist-diagnostico.pdf", False),
   ("Checklist de instalación", "https://soberaniacognitiva.com.ar/descargas/checklist-instalacion.pdf", False),
   ("Test White Rabbit", "https://soberaniacognitiva.com.ar/descargas/test-white-rabbit.pdf", False),
   ("Bitácora de atención", "https://soberaniacognitiva.com.ar/descargas/bitacora-atencion.pdf", False),
  ],
  sitio="https://soberaniacognitiva.com.ar/", sitioTxt="Leer en el sitio",
 ),
 dict(
  slug="preparacionismo", n="03", clase="Ensayo", t1="PREPARACIONISMO", t2="OPTIMISTA",
  sub="La resiliencia es un bien común",
  paginas="144 páginas", palabras="39.972 palabras", anio="2026",
  tesis="Una advertencia, diez capítulos y un epílogo en torno a una idea que incomoda por igual a los dos bandos: que prepararse no es acumular por miedo.",
  cuerpo=[
   "El libro empieza descartando al prepper que no sirve, el de la imagen de supervivencia individual con el rifle y el sótano. Lo que propone en su lugar es acopiar capacidades portadoras de sentido antes de que la escasez se invierta, y hacerlo con otros.",
   "La tesis central es que la resiliencia se reparte o no existe. Un barrio que sabe reparar lo que se rompe aguanta mejor que un sótano lleno de latas, y el vecino que sabe hacer algo vale más que el inventario. De ahí el subtítulo: un bien común, no una colección privada.",
   "Cierra con los primeros treinta días, una puesta en práctica concreta para quien quiera empezar sin comprar nada.",
  ],
  indice=[(a.split("-")[0] if a.split("-")[0].isdigit() else "", c["titulo"]) for a, c in
          [(c["archivo"], c) for c in INDICES["preparacionismo"]]],
  canon=None,
  descargas=[
   ("PDF · 0,5 MB", "https://preparacionismo.vercel.app/descargas/preparacionismo-en-pantuflas.pdf", True),
   ("EPUB · 0,4 MB", "https://preparacionismo.vercel.app/descargas/preparacionismo-en-pantuflas.epub", False),
  ],
  sitio="https://preparacionismo.vercel.app/", sitioTxt="Leer en el sitio",
 ),
 dict(
  slug="escalon", n="04", clase="Ensayo", t1="EL ÚLTIMO", t2="ESCALÓN",
  sub="Qué guardar de lo humano cuando la IA funciona bien",
  paginas="138 páginas", palabras="36.058 palabras", anio="2026",
  tesis="Acerca del humanismo que se organiza frente a la inteligencia artificial, de la síntesis como obra colectiva y del Optimistic Prep.",
  cuerpo=[
   "El libro no discute si la máquina puede pensar. Discute qué se guarda cuando ya funciona lo bastante bien como para que la pregunta sea otra. Ese es el último escalón del título: el punto donde la comparación deja de servir y hay que decidir qué conservar.",
   "Nombra y critica el humanismo sin nombre, ese que se define por oposición y no por contenido, y propone en su lugar la síntesis como producto del colectivo: lo que un grupo de personas puede producir junto y ninguna por separado.",
   "De ahí sale el Optimistic Prep: acopiar capacidades portadoras de sentido antes de que la escasez se invierta. La mochila y la disciplina son los dos capítulos que lo bajan a la práctica.",
  ],
  indice=[(c["archivo"].split("-")[0] if c["archivo"].split("-")[0].isdigit() else "", c["titulo"]) for c in INDICES["escalon"]],
  canon=None,
  descargas=[
   ("PDF · 0,3 MB", "https://el-ultimo-escalon.vercel.app/descargas/el-ultimo-escalon.pdf", True),
   ("EPUB · 0,7 MB", "https://el-ultimo-escalon.vercel.app/descargas/el-ultimo-escalon.epub", False),
  ],
  sitio="https://el-ultimo-escalon.vercel.app/", sitioTxt="Leer en el sitio",
 ),
 dict(
  slug="tecno", n="05", clase="Ensayo", t1="TECNO", t2="CRISTIANISMO",
  sub="Una tercera posición desde el sur",
  paginas="138 páginas", palabras="38.417 palabras", anio="2026",
  tesis="Diez capítulos, repartidos en cuatro partes, sobre el tecnocristianismo tal como lo formuló Tomás Rebord, puestos en diálogo con la encíclica Magnifica Humanitas de León XIV.",
  cuerpo=[
   "El capítulo décimo va directo al punto: tecnocristianismo, en sus palabras. El libro rastrea de dónde viene el término, hasta la formulación de Tomás Rebord, lo desarrolla y también lo discute. Desarrollar el concepto de otro como propio convertiría el ensayo en otra cosa, y el libro lo dice en el cuerpo y en la nota de fuentes.",
   "El onceavo lee la encíclica Magnifica Humanitas de León XIV con el mismo criterio, citando por párrafo numerado para que se pueda verificar cada referencia.",
   "Las cuatro partes van del paraíso como producto y el futuro administrado, pasando por los señores tecnofeudales y la atención como territorio, hasta una posición política que no es la de la fe contra la técnica ni la de la técnica contra la fe.",
  ],
  indice=[(c["archivo"].split("-")[0] if c["archivo"].split("-")[0].isdigit() else "", c["titulo"]) for c in INDICES["tecno"]],
  canon=None,
  descargas=[
   ("PDF · 0,4 MB", "https://tecnocristianismo.vercel.app/descargas/tecnocristianismo.pdf", True),
   ("EPUB · 0,2 MB", "https://tecnocristianismo.vercel.app/descargas/tecnocristianismo.epub", False),
  ],
  sitio="https://tecnocristianismo.vercel.app/", sitioTxt="Leer en el sitio",
 ),
]

CANON = LIBROS[0]["canon"]

# ---------------------------------------------------------------- css
CSS = open(os.path.join(BASE, "estilo_coleccion.css"), encoding="utf-8").read()

FUENTES = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
 '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
 '<link href="https://fonts.googleapis.com/css2?family=Libre+Bodoni:ital,wght@0,400;0,500;0,700;1,400'
 '&family=EB+Garamond:ital,wght@0,400;0,500;1,400&display=swap" rel="stylesheet">')

def nav():
    return """<nav>
  <a class="marca" href="/">CORVUS <i>Lab</i></a>
  <div class="links">
    <a href="/">Portada</a>
    <a href="/coleccion">Colección</a>
    <a href="/proyectos">Trabajos</a>
  </div>
</nav>"""

def pie():
    return """<footer>
  <span class="inf">&#8734;</span>
  Corvus Lab · Córdoba, Argentina<br>
  Los cinco volúmenes se escribieron con asistencia de máquinas,<br>
  y cada libro lo declara en su advertencia y en su colofón.
</footer>"""

def escala(chars):
    """Baja el titular segun el largo de su palabra mas larga, para que no desborde.

    Archivo Black ocupa unos 0,72 em por caracter. El ancho util es 1080px y, en
    pantallas chicas, alrededor del 88% del viewport (el padding es 6vw por lado).
    """
    k = round(122.2 / chars * 0.95, 1)
    tope = min(132, int(1500 / chars * 0.95))
    return f"font-size:clamp(26px,{k}vw,{tope}px)"


def head(titulo, desc):
    return (f'<!DOCTYPE html>\n<html lang="es"><head><meta charset="UTF-8">'
            f'<meta name="viewport" content="width=device-width, initial-scale=1.0">'
            f'<title>{titulo}</title><meta name="description" content="{desc}">'
            f'<meta property="og:title" content="{titulo}">'
            f'<meta property="og:description" content="{desc}">'
            f'{FUENTES}<style>{CSS}</style></head><body>')

# ---------------------------------------------------------------- portada de la coleccion
def build_coleccion():
    estante = "".join(f"""<a class="vol-card" href="/libro/{L['slug']}">
      <div class="marco"><img src="/coleccion/{L['slug']}.webp" alt="{L['t1']} {L['t2']}"
        width="760" height="1078" loading="lazy"></div>
      <p class="pie"><b>{L['t1'].title()} {L['t2'].title()}</b>{L['clase']} · volumen {L['n']}</p>
    </a>""" for L in LIBROS)

    canon = "".join(f'<div><span class="nn">{n}</span><span class="nm">{nombre}</span></div>'
                    for n, nombre in CANON)

    volumenes = []
    for i, L in enumerate(LIBROS):
        papel = " papel" if i % 2 else ""
        d = "".join(f'<a href="{u}"><span class="fl">&#8595;</span>{t}</a>' for t, u, _ in L["descargas"][:2])
        volumenes.append(f"""<section class="banda{papel}">
  <div class="max vol-fila">
    <a class="tapa" href="/libro/{L['slug']}"><img src="/coleccion/{L['slug']}.webp"
      alt="{L['t1']} {L['t2']}" width="760" height="1078" loading="lazy"></a>
    <div>
      <span class="num">Volumen {L['n']} · {L['clase']}</span>
      <h2>{L['t1'].title()} {L['t2'].title()}</h2>
      <p class="sub">{L['sub']}</p>
      <p class="grande">{L['tesis']}</p>
      <p class="ficha"><span>{L['paginas']}</span>{'<span>' + L['palabras'] + '</span>' if L['palabras'] else ''}<span>2026</span></p>
      <div class="descargas">{d}</div>
      <div class="lista-cta"><a class="btn" href="/libro/{L['slug']}">Ver el volumen</a></div>
    </div>
  </div>
</section>""")

    return "\n".join([
      head("Colección · Corvus Lab", "Cinco volúmenes sobre lo que sostiene a una persona y se pierde por goteo. Escritos desde Córdoba."),
      nav(),
      f"""<section class="banda">
  <div class="max">
    <p class="kicker">Corvus Lab · Colección · 2026</p>
    <h1 style="font-size:clamp(44px,9vw,96px)"><span class="r1">CINCO</span><span class="r2">volúmenes</span><span class="r3">Y UNA PÉRDIDA</span></h1>
    <p class="bajada">Lo que sostiene a una persona ha ido dejando de pertenecerle sin que nadie firmara nada. Sobre esa pérdida trabajan estos cinco libros, y ninguno aconseja enfrentarla a solas.</p>
    <div class="lista-cta">
      <a class="btn fuerte" href="#volumenes">Los cinco volúmenes</a>
      <a class="btn" href="#sintesis">Advertencia al lector</a>
    </div>
  </div>
</section>""",
      f"""<section class="banda papel" id="sintesis">
  <div class="max">
    <div class="regla"></div>
    <p class="kicker">Advertencia al lector</p>
    <h2 class="negro">Nada se pierde de golpe</h2>
    <p class="grande">Lo que sostiene a una persona no se pierde de una vez, sino por goteo, y cada
    gota, tomada por separado, parecía razonable. Las ideas propias llegan ahora recomendadas; la
    atención se remata al mejor postor; la casa y el trabajo se alquilan, y aquello que uno sabía
    hacer empieza a hacerlo una máquina.</p>
    <p>Los cinco volúmenes se ocupan de ese goteo, cada uno desde una pieza distinta. Ninguno
    pretende bastar por sí solo, ninguno predica la retirada, y ninguno está escrito desde el
    centro: se escribieron en Córdoba, adonde las cosas llegan más tarde y pueden mirarse, por
    eso mismo, sin fascinación.</p>
    <p>Son breves a propósito. Admiten cualquier orden de lectura, y cada uno se sostiene sin los demás.</p>
  </div>
</section>""",
      f"""<section class="banda tinta2" id="volumenes">
  <div class="max">
    <p class="kicker">Los cinco volúmenes</p>
    <h2>El estante</h2>
    <div class="estante">{estante}</div>
  </div>
</section>""",
      f"""<section class="banda papel" id="canon">
  <div class="max">
    <div class="regla"></div>
    <p class="kicker">El canon</p>
    <h2 class="negro">Los dieciséis del panteón</h2>
    <p>El primer volumen fija las fuentes de todo lo demás. He aquí los dieciséis, en el orden
    en que aparecen, de Borges a Facundo Cabral.</p>
    <div class="canon">{canon}</div>
    <p style="margin-top:26px">Ninguno figura por afán de completar la lista; cada uno dejó una herramienta del
    pensamiento que todavía se usa. El panteón queda abierto, y el libro lo declara.</p>
  </div>
</section>""",
      "\n".join(volumenes),
      pie(),
      "</body></html>"])

# ---------------------------------------------------------------- pagina de cada libro
def build_libro(L):
    ficha = [L["paginas"]]
    if L["palabras"]: ficha.append(L["palabras"])
    ficha.append(L["anio"])
    if L["slug"] == "panteon": ficha.append("Castellano · English edition")
    if L["slug"] == "soberania": ficha.append("Dominio público")
    ficha = "".join(f"<span>{x}</span>" for x in ficha)

    desc = "".join(f'<a href="{u}"><span class="fl">&#8595;</span>{t}</a>' for t, u, _ in L["descargas"])

    # indice
    if L["slug"] == "panteon":
        bloques = "".join(f'<div><span class="nn">{n}</span><span class="nm">{nom}</span></div>'
                          for n, nom in L["canon"])
        tituloIndice = "Los dieciséis"
    else:
        bloques = "".join(f'<div><span class="nn">{n or "·"}</span><span class="nm">{t}</span></div>'
                          for n, t in L["indice"])
        tituloIndice = "Índice"

    cuerpo = "".join(('<p class="grande">' if i == 0 else '<p>') + p + '</p>'
                     for i, p in enumerate(L["cuerpo"]))

    return "\n".join([
      head(f"{L['t1'].title()} {L['t2'].title()} · Corvus Lab", L["sub"]),
      nav(),
      f"""<section class="banda">
  <div class="max">
    <p class="kicker">Colección Corvus Lab · Volumen {L['n']} · {L['clase']}</p>
    <h1 style="{escala(max(len(L['t1']), len(L['t2'])))}"><span class="r1">{L['t1']}</span><span class="r3">{L['t2']}</span></h1>
    <p class="bajada">{L['sub']}</p>
  </div>
</section>""",
      f"""<section class="banda papel">
  <div class="max vol-fila">
    <div class="tapa"><img src="/coleccion/{L['slug']}.webp" alt="{L['t1']} {L['t2']}"
      width="760" height="1078"></div>
    <div>
      <p class="kicker">Descargar y leer</p>
      <h2 class="negro">De qué trata</h2>
      {cuerpo}
      <p class="ficha">{ficha}</p>
      <div class="descargas">{desc}</div>
      <div class="lista-cta">
        <a class="btn fuerte" href="{L['sitio']}">{L['sitioTxt']}</a>
        <a class="btn" href="/coleccion">Volver a la colección</a>
      </div>
    </div>
  </div>
</section>""",
      f"""<section class="banda">
  <div class="max">
    <p class="kicker">{tituloIndice}</p>
    <h2>Lo que hay adentro</h2>
    <div class="{'canon' if L['slug'] == 'panteon' else 'indice'}">{bloques}</div>
  </div>
</section>""",
      pie(),
      "</body></html>"])

coleccion = build_coleccion()
open(os.path.join(ROOT, "coleccion.html"), "w", encoding="utf-8").write(coleccion)
print(f"coleccion.html: {len(coleccion)} bytes")
for L in LIBROS:
    html = build_libro(L)
    p = os.path.join(OUT_LIBRO, f"{L['slug']}.html")
    open(p, "w", encoding="utf-8").write(html)
    print(f"  libro/{L['slug']}.html: {len(html)} bytes")
print("\nlisto")
