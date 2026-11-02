#!/usr/bin/env python3
"""Genera las cinco tapas de la colección y las renderiza a webp.

Receta (tomada de la referencia fs.blog/tgmm):
  fondo solido, tinta oscura para todo el texto y para la ilustracion,
  titulo en mayusculas al centro arriba, subtitulo abajo, ilustracion
  de linea conceptual al medio, sello del sello editorial al pie.
"""
import os, subprocess

CH = "/home/nanobot/.cache/ms-playwright/chromium-1248/chrome-linux64/chrome"
OUT = "/home/nanobot/projects/corvus-lab/coleccion"
TMP = "/tmp/tapas-tgmm"
W, H = 760, 1078
os.makedirs(OUT, exist_ok=True)
os.makedirs(TMP, exist_ok=True)

TINTA = "#141821"

# ---------------------------------------------------------------- ilustraciones
# Todas comparten el mismo idioma: trazo de tinta, sin relleno salvo algun
# acento, remates redondeados, y unas imperfecciones minimas para que no se
# lean como un clip-art geometrico.

ILUS = {}

# 1. Pantheon: una columnata de dieciseis columnas bajo un fronton.
ILUS["panteon"] = """
<g fill="none" stroke="{t}" stroke-width="4.6" stroke-linecap="round" stroke-linejoin="round">
  <path d="M28 176 L216 74 L404 176"/>
  <path d="M20 176 H412"/>
  <path d="M40 196 H392"/>
  <!-- columnas: dieciseis -->
  {cols}
  <path d="M30 306 H402"/>
</g>
<g fill="{t}">
  <circle cx="96" cy="30" r="5"/>
  <circle cx="216" cy="10" r="4"/>
  <circle cx="336" cy="34" r="4.4"/>
  <path d="M216 44 l4.6 9.6 10 1.3 -7.4 7 2 10.2 -9.2 -5 -9.2 5 2 -10.2 -7.4 -7 10 -1.3z" opacity=".5"/>
</g>
"""

def columnas(n=16, x0=44, ancho=356, alto=104):
    paso = ancho / (n - 1)
    p = []
    for i in range(n):
        x = x0 + i * paso
        p.append(f'<path d="M{x:.1f} 200 V{200+alto}"/>')
        p.append(f'<path d="M{x-9:.1f} 200 H{x+9:.1f}"/>')
        p.append(f'<path d="M{x-9:.1f} {200+alto} H{x+9:.1f}"/>')
    return "".join(p)

# 2. Soberania cognitiva: el cargador que sale del tomacorriente.
ILUS["soberania"] = """
<g fill="none" stroke="{t}" stroke-width="4.6" stroke-linecap="round" stroke-linejoin="round">
  <!-- tomacorriente -->
  <rect x="278" y="108" width="140" height="176" rx="18"/>
  <path d="M310 152 V186"/>
  <path d="M386 152 V186"/>
  <circle cx="348" cy="238" r="12"/>
  <!-- enchufe saliendo, corrido a la izquierda -->
  <rect x="176" y="128" width="104" height="136" rx="14"/>
  <path d="M280 158 h34"/>
  <path d="M280 234 h34"/>
  <path d="M176 164 q-52 -30 -84 6"/>
  <path d="M92 170 q-34 22 -22 62 t-40 54" stroke-width="6"/>
  <!-- chispa entre las dos piezas -->
  <path d="M258 148 l-16 -16"/>
  <path d="M266 196 l-22 4"/>
  <path d="M258 246 l-16 18"/>
</g>
<g fill="{t}">
  <path d="M300 62 l7 15 16 2 -12 11 3 16 -14 -8 -14 8 3 -16 -12 -11 16 -2z"/>
</g>
"""

# 3. Preparacionismo: el mate que pasa de mano en mano.
ILUS["preparacionismo"] = """
<g fill="none" stroke="{t}" stroke-width="4.6" stroke-linecap="round" stroke-linejoin="round">
  <!-- termo, a la izquierda -->
  <path d="M74 96 L68 288 Q68 300 80 300 L124 300 Q136 300 136 288 L130 96"/>
  <path d="M70 96 H134"/>
  <path d="M78 66 H126 V96 H78 Z"/>
  <path d="M92 66 V52 Q102 42 112 52 V66"/>
  <path d="M74 210 H130" opacity=".4"/>
  <!-- el mate, a la derecha -->
  <path d="M212 150 Q262 128 312 150" stroke-width="5.5"/>
  <path d="M216 152 Q200 246 234 268 Q262 282 290 268 Q324 246 308 152" stroke-width="5.5"/>
  <path d="M212 150 Q262 172 312 150" opacity=".55"/>
  <!-- la bombilla -->
  <path d="M262 158 Q300 118 292 76" stroke-width="5.5"/>
  <path d="M288 76 Q286 62 296 60" stroke-width="5"/>
  <circle cx="300" cy="56" r="9"/>
  <!-- vapor sobre el mate -->
  <path d="M238 118 Q248 102 236 88 Q226 76 238 62" opacity=".4"/>
  <path d="M266 108 Q276 94 264 80" opacity=".28"/>
</g>
<g fill="{t}">
  <circle cx="252" cy="206" r="4.2" opacity=".45"/>
  <circle cx="272" cy="226" r="3.6" opacity=".32"/>
  <circle cx="286" cy="200" r="3" opacity=".26"/>
</g>
"""

# 4. El ultimo escalon: la escalera cuyo ultimo escalon se vuelve chispa.
ILUS["escalon"] = """
<g fill="none" stroke="{t}" stroke-width="4.6" stroke-linecap="round" stroke-linejoin="round">
  <!-- escalones -->
  <path d="M24 300 H120 V254 H206 V208 H292 V162 H350"/>
  <path d="M24 300 V254 H120 V208 H206 V162 H292 V116"/>
  <path d="M350 162 V116"/>
  <!-- el ultimo escalon se abre -->
  <path d="M292 116 q30 -22 58 -22"/>
  <path d="M350 116 q-8 -30 4 -52" opacity=".5"/>
  <!-- peldaños insinuados -->
  <path d="M120 300 V332" opacity=".35"/>
  <path d="M206 254 V286" opacity=".35"/>
  <path d="M292 208 V240" opacity=".35"/>
</g>
<g fill="{t}">
  <path d="M356 26 l9 26 26 9 -26 9 -9 26 -9 -26 -26 -9 26 -9z"/>
  <circle cx="404" cy="76" r="5" opacity=".6"/>
  <circle cx="330" cy="52" r="3.6" opacity=".45"/>
  <circle cx="418" cy="122" r="3.2" opacity=".35"/>
</g>
"""

# 5. Tecnocristianismo: la cruz hecha de pistas de circuito.
ILUS["tecno"] = """
<g fill="none" stroke="{t}" stroke-width="4.6" stroke-linecap="round" stroke-linejoin="round">
  <!-- cruz de circuito -->
  <path d="M216 30 V300"/>
  <path d="M116 130 H316"/>
  <!-- terminales -->
  <circle cx="216" cy="30" r="9"/>
  <circle cx="116" cy="130" r="9"/>
  <circle cx="316" cy="130" r="9"/>
  <circle cx="216" cy="300" r="9"/>
  <!-- pistas que entran -->
  <path d="M216 76 H286 V46"/>
  <path d="M216 196 H146 V246"/>
  <path d="M166 130 V76"/>
  <path d="M266 130 V190"/>
  <path d="M116 130 H56 V96"/>
  <path d="M316 130 H376 V180"/>
  <!-- nodos -->
  <circle cx="286" cy="46" r="5"/>
  <circle cx="146" cy="246" r="5"/>
  <circle cx="56" cy="96" r="5"/>
  <circle cx="376" cy="180" r="5"/>
</g>
<g fill="{t}">
  <path d="M216 128 l6 22 22 6 -22 6 -6 22 -6 -22 -22 -6 22 -6z" opacity=".9"/>
</g>
"""

# ---------------------------------------------------------------- tapas
LIBROS = [
 dict(slug="panteon", bg="#d9c7a1", n="01", vol="VOLUMEN UNO",
      t1="PANTEÓN", t2="PERSONAL", sub="Un mapa mental de dieciséis pensadores que me formaron",
      sello="CORVUS LAB"),
 dict(slug="soberania", bg="#d9705c", n="02", vol="VOLUMEN DOS",
      t1="SOBERANÍA", t2="COGNITIVA", sub="Protocolo para recuperar la atención, el deseo y el tiempo",
      sello="CORVUS LAB"),
 dict(slug="preparacionismo", bg="#e0b84e", n="03", vol="VOLUMEN TRES",
      t1="PREPARACIONISMO", t2="OPTIMISTA", sub="La resiliencia es un bien común",
      sello="CORVUS LAB"),
 dict(slug="escalon", bg="#8dbcba", n="04", vol="VOLUMEN CUATRO",
      t1="EL ÚLTIMO", t2="ESCALÓN", sub="Qué guardar de lo humano cuando la IA funciona bien",
      sello="CORVUS LAB"),
 dict(slug="tecno", bg="#b3a2cf", n="05", vol="VOLUMEN CINCO",
      t1="TECNO", t2="CRISTIANISMO", sub="Una tercera posición desde el sur",
      sello="CORVUS LAB"),
]

TPL = """<!DOCTYPE html>
<html lang="es"><head><meta charset="utf-8"><style>
@page {{ size: {w}px {h}px; margin: 0 }}
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:{w}px;height:{h}px;overflow:hidden}}
body{{background:{bg};color:{tinta};position:relative;
  font-family:"Archivo",Helvetica,Arial,sans-serif;
  display:flex;flex-direction:column;align-items:center}}
.titulo{{text-align:center;margin-top:82px;line-height:.94}}
.titulo .l1{{display:block;font-family:"Archivo Black",Archivo,sans-serif;font-weight:{g1};
  font-size:{f1}px;letter-spacing:-.01em}}
.titulo .l2{{display:block;font-family:"Archivo Black",Archivo,sans-serif;font-weight:{g2};
  font-size:{f2}px;letter-spacing:-.01em}}
.sub{{margin-top:26px;text-align:center;font-size:22px;font-weight:500;
  line-height:1.35;max-width:560px;opacity:.82}}
.ilus{{margin-top:44px;width:{iw}px}}
.ilus svg{{width:100%;height:auto;display:block}}
.pie{{position:absolute;bottom:64px;left:0;right:0;display:flex;flex-direction:column;
  align-items:center;gap:22px}}
.sello{{font-family:"Archivo Black",Archivo,sans-serif;font-size:26px;letter-spacing:.16em}}
.caja{{display:flex;align-items:center;gap:12px}}
.num{{background:{tinta};color:{bg};font-family:"IBM Plex Mono",monospace;font-size:15px;
  letter-spacing:.14em;padding:9px 16px;border:2px solid {tinta}}}
.vol{{font-family:"IBM Plex Mono",monospace;font-size:13px;letter-spacing:.22em;
  text-transform:uppercase;opacity:.7}}
</style>
<link href="https://fonts.googleapis.com/css2?family=Archivo+Black&family=Archivo:wght@500;700&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
</head><body>
  <div class="titulo"><span class="l1">{t1}</span><span class="l2">{t2}</span></div>
  <p class="sub">{sub}</p>
  <div class="ilus"><svg viewBox="0 0 432 340" xmlns="http://www.w3.org/2000/svg">{ilus}</svg></div>
  <div class="pie">
    <span class="sello">{sello}</span>
    <div class="caja"><span class="num">{n}</span><span class="vol">{vol}</span></div>
  </div>
</body></html>
"""

def medir(texto, base):
    """Baja el cuerpo si el titulo es largo, para que no se salga del ancho."""
    largo = len(texto)
    if largo <= 8:  return base
    if largo <= 11: return int(base * 0.88)
    if largo <= 14: return int(base * 0.76)
    return int(base * 0.64)

for L in LIBROS:
    ilus = ILUS[L["slug"]].format(t=TINTA, cols=columnas())
    f1 = medir(L["t1"], 78); f2 = medir(L["t2"], 78)
    html = TPL.format(w=W, h=H, bg=L["bg"], tinta=TINTA, ilus=ilus,
                      g1=700, g2=700, f1=f1, f2=f2, iw=430,
                      **{k: L[k] for k in ("n","vol","t1","t2","sub","sello")})
    src = f"{TMP}/{L['slug']}.html"
    png = f"{TMP}/{L['slug']}.png"
    open(src, "w", encoding="utf-8").write(html)
    r = subprocess.run([CH, "--headless", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
                        "--force-device-scale-factor=2", f"--window-size={W},{H}",
                        f"--screenshot={png}", "--virtual-time-budget=6000", "file://" + src],
                       capture_output=True, text=True, timeout=150)
    if not os.path.exists(png):
        print(f"  {L['slug']}: FALLO  {r.stderr[-200:]}")
        continue
    from PIL import Image
    im = Image.open(png).convert("RGB").resize((W, H), Image.LANCZOS)
    dst = f"{OUT}/{L['slug']}.webp"
    im.save(dst, "WEBP", quality=86, method=6)
    print(f"  {L['slug']:<18} {im.size[0]}x{im.size[1]}  {os.path.getsize(dst)//1024} KB  f1={f1} f2={f2}")

print("\nlisto")
