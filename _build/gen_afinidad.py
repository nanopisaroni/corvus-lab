#!/usr/bin/env python3
# Genera afinidad.html desde _build/data/votos.json
# Fuente: actas de votación nominal de los diarios de sesiones (período 144).
#
# El test embebe los 256 diputados y sus votos en las diez preguntas. El cálculo
# de coincidencia corre en el navegador; no hay fetch ni backend.
import json, os, html

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(BASE, "_build", "data", "votos.json")
OUT = os.path.join(BASE, "afinidad.html")

d = json.load(open(SRC, encoding="utf-8"))
DIPS = d["dips"]
ACTAS = {a["id"]: a for a in d["actas"]}
PREG = d["preguntas"]

# El acta guarda AF / NE / AB. En el test cada posición es un dígito.
CODIGO = {"AF": "1", "NE": "2", "AB": "3"}
SIN_VOTO = "0"

DISTRITOS = {
    "BUENOS AIRES": "Buenos Aires",
    "CATAMARCA": "Catamarca",
    "CHACO": "Chaco",
    "CHUBUT": "Chubut",
    "CIUDAD DE BUENOS AIRES": "Ciudad de Buenos Aires",
    "CORDOBA": "Córdoba",
    "CORRIENTES": "Corrientes",
    "ENTRE RIOS": "Entre Ríos",
    "FORMOSA": "Formosa",
    "JUJUY": "Jujuy",
    "LA PAMPA": "La Pampa",
    "LA RIOJA": "La Rioja",
    "MENDOZA": "Mendoza",
    "MISIONES": "Misiones",
    "NEUQUEN": "Neuquén",
    "RIO NEGRO": "Río Negro",
    "SALTA": "Salta",
    "SAN JUAN": "San Juan",
    "SAN LUIS": "San Luis",
    "SANTA CRUZ": "Santa Cruz",
    "SANTA FE": "Santa Fe",
    "SANTIAGO DEL ESTERO": "Santiago del Estero",
    "TIERRA DEL FUEGO": "Tierra del Fuego",
    "TUCUMAN": "Tucumán",
}

BLOQUES = {
    "LA LIBERTAD AVANZA": "La Libertad Avanza",
    "UNIÓN POR LA PATRIA": "Unión por la Patria",
    "PROVINCIAS UNIDAS": "Provincias Unidas",
    "PRO": "PRO",
    "ARGENTINA FEDERAL": "Argentina Federal",
    "UCR - UNIÓN CÍVICA RADICAL": "UCR - Unión Cívica Radical",
    "INDEPENDENCIA": "Independencia",
    "ELIJO CATAMARCA": "Elijo Catamarca",
    "PRODUCCION Y TRABAJO": "Producción y Trabajo",
    "MID - MOVIMIENTO DE INTEGRACIÓN Y DESARROLLO": "MID - Movimiento de Integración y Desarrollo",
    "PRIMERO SAN LUIS": "Primero San Luis",
    "COALICION CIVICA": "Coalición Cívica",
    "ENCUENTRO FEDERAL": "Encuentro Federal",
    "PTS-FRENTE DE IZQUIERDA Y DE TRABAJADORES UNIDAD": "PTS - Frente de Izquierda y de Trabajadores Unidad",
    "POR SANTA CRUZ": "Por Santa Cruz",
    "IZQUIERDA SOCIALISTA - FRENTE DE IZQUIERDA UNIDAD": "Izquierda Socialista - Frente de Izquierda Unidad",
    "ADELANTE BUENOS AIRES": "Adelante Buenos Aires",
    "LA NEUQUINIDAD": "La Neuquinidad",
    "COHERENCIA": "Coherencia",
    "DEFENDAMOS CÓRDOBA": "Defendamos Córdoba",
}

COLOR = {
    "LA LIBERTAD AVANZA": "#6b4fa8",
    "UNIÓN POR LA PATRIA": "#2f6fa8",
    "PRO": "#b8912a",
    "UCR - UNIÓN CÍVICA RADICAL": "#b5442f",
    "PROVINCIAS UNIDAS": "#3f7d6b",
    "ARGENTINA FEDERAL": "#8a5a12",
    "ELIJO CATAMARCA": "#7a5c9e",
    "INDEPENDENCIA": "#7a5c9e",
}
GRIS = "#b3ab9e"


def fecha_txt(dia):
    return f"{dia[6:8]}/{dia[4:6]}/{dia[0:4]}"


def bloque_txt(b):
    return BLOQUES.get(b, b.title())


def distrito_txt(x):
    return DISTRITOS.get(x, x.title())


def color(b):
    return COLOR.get(b, GRIS)


# --- padrón: orden alfabético, índice estable entre Python y el navegador ---
orden = sorted(DIPS.items(), key=lambda kv: kv[1]["n"])
DIPS_JS = [{"n": v["n"], "b": bloque_txt(v["b"]), "d": distrito_txt(v["d"]), "c": color(v["b"])}
           for _, v in orden]

# --- votos por pregunta: una cadena de 256 dígitos por acta ---
VOTOS_JS, SPLIT = [], []
for q in PREG:
    acta = ACTAS[q["id"]]
    fila = "".join(CODIGO.get(acta["votos"].get(slug, ""), SIN_VOTO) for slug, _ in orden)
    assert len(fila) == len(orden), q["id"]
    assert set(fila) <= set("0123"), q["id"]
    VOTOS_JS.append(fila)
    SPLIT.append({
        "af": fila.count("1"), "ne": fila.count("2"), "ab": fila.count("3"),
        "sin": fila.count(SIN_VOTO),
    })

PREG_JS = [{
    "p": q["pregunta"],
    "ac": q["aclaracion"],
    "as": q["asunto"],
    "f": fecha_txt(q["dia"]),
    "a": ACTAS[q["id"]]["acta"],
    "s": SPLIT[i],
} for i, q in enumerate(PREG)]

N_SIN_DATOS = sum(1 for slug, _ in orden
                  if all(slug not in ACTAS[q["id"]]["votos"] for q in PREG))

DATOS = json.dumps({"dips": DIPS_JS, "votos": VOTOS_JS, "preguntas": PREG_JS,
                    "n": len(DIPS_JS)},
                   ensure_ascii=False, separators=(",", ":"))
DATOS = DATOS.replace("</", "<\\/")

# --- tarjetas del test ---
OPCIONES = [("1", "A favor", ""), ("2", "En contra", ""), ("3", "Abstención", ""),
            ("0", "Sin responder", " salta")]


def tarjeta(i, q):
    acta = ACTAS[q["id"]]
    opts = "".join(
        f'<label class="op{suf}"><input type="radio" name="q{i}" value="{val}">'
        f'<span>{txt}</span></label>'
        for val, txt, suf in OPCIONES)
    return f'''<div class="q">
  <div class="qh"><span class="qn mono">{i + 1:02d}</span><p class="qt">{html.escape(q["pregunta"])}</p></div>
  <p class="qa">{html.escape(q["aclaracion"])}</p>
  <p class="qsrc mono">Acta {acta["acta"]} · {fecha_txt(q["dia"])} · {html.escape(q["asunto"])}</p>
  <div class="opts" role="radiogroup" aria-label="Pregunta {i + 1}">{opts}</div>
</div>'''


TARJETAS = "\n".join(tarjeta(i, q) for i, q in enumerate(PREG))

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
nav.top { border-bottom: 1px solid var(--rule); }
nav.top .wrap { display: flex; justify-content: space-between; align-items: baseline; padding: 14px 28px; }
nav.top a { color: var(--muted); text-decoration: none; font-size: 13px; }
nav.top a:hover { color: var(--ink); }
nav.top .brand { font-family: "IBM Plex Mono", monospace; font-size: 12px; letter-spacing: .12em; text-transform: uppercase; color: var(--ink); }
header.hero { padding: 54px 0 30px; border-bottom: 1px solid var(--rule-strong); }
.kicker { font-family: "IBM Plex Mono", monospace; font-size: 11.5px; letter-spacing: .14em;
  text-transform: uppercase; color: var(--soft); margin-bottom: 16px; }
h1 { font-size: clamp(30px, 5vw, 46px); line-height: 1.08; letter-spacing: -.02em; font-weight: 600; margin: 0 0 18px; }
.dek { font-size: 17.5px; color: var(--muted); max-width: 720px; margin: 0; }
.cifras { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1px; background: var(--rule);
  border-bottom: 1px solid var(--rule-strong); }
.cifra { background: var(--paper); padding: 24px 28px 22px; }
.cifra b { display: block; font-family: "IBM Plex Mono", monospace; font-size: 30px; font-weight: 500;
  letter-spacing: -.02em; margin-bottom: 4px; }
.cifra span { font-size: 12.5px; color: var(--muted); line-height: 1.35; display: block; }
section { padding: 46px 0 12px; }
h2 { font-size: 22px; font-weight: 600; letter-spacing: -.01em; margin: 0 0 6px; }
h2 span { font-weight: 300; color: var(--soft); font-size: 15px; }
p.intro { color: var(--muted); max-width: 760px; margin: 0 0 26px; font-size: 15.5px; }
table { width: 100%; border-collapse: collapse; font-size: 14.5px; }
th { text-align: left; font-family: "IBM Plex Mono", monospace; font-size: 11px; letter-spacing: .1em;
  text-transform: uppercase; color: var(--soft); font-weight: 500; padding: 0 8px 10px; border-bottom: 1px solid var(--rule-strong); }
td { padding: 9px 8px; border-bottom: 1px solid var(--rule); vertical-align: middle; }
td.num, th.num { text-align: right; font-family: "IBM Plex Mono", monospace; font-variant-numeric: tabular-nums; }
td.bar, th.bar { width: 24%; }
td.bar span { display: block; height: 7px; border-radius: 1px; opacity: .75; }
.dot { display: inline-block; width: 9px; height: 9px; border-radius: 50%; margin-right: 9px; vertical-align: middle; }
ol.rank { list-style: none; padding: 0; margin: 0; }
ol.rank li { display: flex; align-items: baseline; gap: 10px; padding: 9px 0; border-bottom: 1px solid var(--rule); }
ol.rank .pos { color: var(--soft); font-family: "IBM Plex Mono", monospace; font-size: 12px; width: 20px; }
ol.rank .nm { flex: 1; }
ol.rank .bl { color: var(--soft); font-size: 12.5px; }
ol.rank .vl { font-family: "IBM Plex Mono", monospace; font-variant-numeric: tabular-nums; min-width: 44px; text-align: right; }
ol.rank .vl em { font-style: normal; color: var(--soft); font-size: 11px; }
.metodo { border-top: 1px solid var(--rule-strong); margin-top: 46px; padding: 34px 0 60px; }
.metodo h2 { font-size: 16px; }
.metodo p { color: var(--muted); font-size: 14.5px; max-width: 760px; margin: 0 0 12px; }
footer { border-top: 1px solid var(--rule); padding: 22px 0 40px; color: var(--soft); font-size: 12.5px; }
footer a { color: var(--muted); text-decoration: none; }
footer a:hover { color: var(--ink); }

/* --- test --- */
.q { background: var(--card); border: 1px solid var(--rule); border-left: 3px solid var(--rule);
  border-radius: 3px; padding: 20px 22px 18px; margin-bottom: 12px; }
.q.contestada { border-left-color: var(--ink); }
.qh { display: flex; gap: 14px; align-items: baseline; }
.qn { font-size: 12px; color: var(--soft); letter-spacing: .08em; padding-top: 3px; }
.qt { font-size: 17px; font-weight: 500; line-height: 1.4; margin: 0; letter-spacing: -.005em; }
.qa { color: var(--muted); font-size: 13.5px; margin: 6px 0 0 34px; max-width: 760px; }
.qsrc { color: var(--muted); font-size: 11px; letter-spacing: .03em; margin: 6px 0 14px 34px; text-transform: uppercase; }
.opts { display: flex; flex-wrap: wrap; gap: 7px; margin-left: 34px; }
.opts label { position: relative; display: inline-block; }
.opts input { position: absolute; opacity: 0; width: 1px; height: 1px; margin: 0; }
.opts span { display: inline-block; border: 1px solid var(--rule-strong); border-radius: 2px;
  padding: 6px 14px; font-size: 13.5px; color: var(--muted); background: var(--card);
  cursor: pointer; transition: background .12s, color .12s, border-color .12s; }
.opts span:hover { border-color: var(--ink); color: var(--ink); }
.opts input:checked + span { background: var(--ink); border-color: var(--ink); color: var(--paper); }
.opts input:focus-visible + span { outline: 2px solid #6b4fa8; outline-offset: 2px; }
.opts .salta span { border-style: dashed; color: var(--soft); }
.opts .salta input:checked + span { background: transparent; border-color: var(--rule-strong); color: var(--muted); }
.acciones { display: flex; flex-wrap: wrap; align-items: center; gap: 14px; padding: 22px 0 6px;
  border-top: 1px solid var(--rule); margin-top: 26px; }
.btn { font: inherit; font-size: 14.5px; font-weight: 500; background: var(--ink); color: var(--paper);
  border: 1px solid var(--ink); border-radius: 2px; padding: 10px 22px; cursor: pointer; }
.btn:hover:not(:disabled) { background: #2c261e; }
.btn:disabled { opacity: .38; cursor: not-allowed; }
.btn.ghost { background: transparent; color: var(--muted); border-color: var(--rule-strong); }
.btn.ghost:hover { color: var(--ink); border-color: var(--ink); background: transparent; }
.btn:focus-visible { outline: 2px solid #6b4fa8; outline-offset: 2px; }
.prog { color: var(--soft); font-size: 12px; letter-spacing: .06em; text-transform: uppercase; }
.stale { color: #8a5a12; font-size: 13px; margin: 10px 0 0; }

/* --- resultados --- */
#res { padding-top: 40px; }
.resnota { color: var(--muted); font-size: 14px; max-width: 760px; margin: 4px 0 24px; }
.resumen { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1px; background: var(--rule);
  border-top: 1px solid var(--rule-strong); border-bottom: 1px solid var(--rule-strong); margin-bottom: 8px; }
.resumen .cifra b.txt { font-family: "Public Sans", sans-serif; font-size: 17px; font-weight: 600;
  line-height: 1.25; letter-spacing: -.01em; padding-top: 8px; }
h3.sub { font-family: "IBM Plex Mono", monospace; font-size: 11.5px; letter-spacing: .13em;
  text-transform: uppercase; color: var(--muted); font-weight: 500; margin: 38px 0 12px; }
.pie { color: var(--muted); font-size: 12.5px; margin: 10px 0 0; }
ol.rank li.primero .nm b { font-weight: 600; }
ol.rank .nm b { font-weight: 500; display: block; }
ol.rank .nm .sub2 { display: flex; align-items: center; color: var(--soft); font-size: 12.5px; margin-top: 1px; }
ol.rank li { align-items: flex-start; }
ol.rank .pos { padding-top: 2px; }
.barra { display: block; height: 3px; background: var(--rule); margin-top: 7px; border-radius: 1px; }
.barra i { display: block; height: 100%; border-radius: 1px; opacity: .8; }
.vl b { font-weight: 500; }
.frac { font-size: 11.5px; color: var(--muted); min-width: 36px; text-align: right; padding-top: 2px; }
.vl em { font-style: normal; color: var(--soft); font-size: 11px; }
td .de { color: var(--soft); }
td.tuvoto { font-weight: 500; }
td.tuvoto.vacio { color: var(--soft); font-weight: 400; }
details.todos { margin-top: 38px; border-top: 1px solid var(--rule-strong); }
details.todos summary { cursor: pointer; padding: 16px 0; font-family: "IBM Plex Mono", monospace;
  font-size: 11.5px; letter-spacing: .13em; text-transform: uppercase; color: var(--muted); }
details.todos summary:hover { color: var(--ink); }
details.todos table { margin-bottom: 20px; }
details.todos td { padding: 7px 8px; font-size: 13.5px; }
.tabla-scroll { overflow-x: auto; }

@media (max-width: 760px) {
  .cifras, .resumen { grid-template-columns: 1fr 1fr; }
  .cifra { padding: 18px 20px; }
  td.bar, th.bar { display: none; }
  .opts, .qa, .qsrc { margin-left: 0; }
  .qh { gap: 10px; }
  .q { padding: 18px 16px; }
  .dist, th.dist { display: none; }
}
@media (max-width: 560px) {
  .bl-col, th.bl-col { display: none; }
}
"""

JS = r"""
(function () {
  var D = JSON.parse(document.getElementById('datos').textContent);
  var NQ = D.preguntas.length;
  var VOTO = { '1': 'A favor', '2': 'En contra', '3': 'Abstención' };
  var btn = document.getElementById('calc');
  var rst = document.getElementById('reset');
  var prog = document.getElementById('prog');
  var res = document.getElementById('res');
  var stale = document.getElementById('stale');
  var ultimo = null;

  function esc(s) {
    return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;')
      .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  function respuestas() {
    var a = [];
    for (var i = 0; i < NQ; i++) {
      var el = document.querySelector('input[name="q' + i + '"]:checked');
      a.push(el && el.value !== '0' ? el.value : null);
    }
    return a;
  }

  function refrescar() {
    var a = respuestas(), n = 0, cards = document.querySelectorAll('.q');
    for (var i = 0; i < NQ; i++) {
      if (a[i]) n++;
      cards[i].classList.toggle('contestada', !!a[i]);
    }
    prog.textContent = n + ' de ' + NQ + ' respondidas';
    btn.disabled = n === 0;
    stale.hidden = !(ultimo !== null && a.join('|') !== ultimo && !res.hidden);
  }

  function comparar(a) {
    var resp = a.filter(Boolean).length;
    var minComp = resp <= 3 ? Math.max(resp, 1) : Math.max(3, Math.ceil(resp * 0.6));
    var filas = [];
    for (var i = 0; i < D.dips.length; i++) {
      var hit = 0, comp = 0;
      for (var q = 0; q < NQ; q++) {
        if (!a[q]) continue;
        var v = D.votos[q].charAt(i);
        if (v === '0') continue;
        comp++;
        if (v === a[q]) hit++;
      }
      filas.push({ i: i, hit: hit, comp: comp, pct: comp ? hit / comp : 0 });
    }
    function ord(x, y) {
      if (y.pct !== x.pct) return y.pct - x.pct;
      if (y.hit !== x.hit) return y.hit - x.hit;
      if (y.comp !== x.comp) return y.comp - x.comp;
      return D.dips[x.i].n.localeCompare(D.dips[y.i].n, 'es');
    }
    var dentro = filas.filter(function (f) { return f.comp >= minComp; }).sort(ord);
    var fuera = filas.filter(function (f) { return f.comp < minComp; }).sort(ord);
    return { dentro: dentro, fuera: fuera, resp: resp, minComp: minComp };
  }

  function filaTop(f) {
    var d = D.dips[f.i];
    return '<li class="' + (f.pos === 1 ? 'primero' : '') + '">' +
      '<span class="pos">' + f.pos + '</span>' +
      '<span class="nm"><b>' + esc(d.n) + '</b>' +
      '<span class="sub2"><i class="dot" style="background:' + d.c + '"></i>' + esc(d.b) + ' · ' + esc(d.d) + '</span>' +
      '<span class="barra"><i style="width:' + (f.pct * 100).toFixed(1) + '%;background:' + d.c + '"></i></span></span>' +
      '<span class="frac mono">' + f.hit + '/' + f.comp + '</span>' +
      '<span class="vl"><b>' + Math.round(f.pct * 100) + '</b><em>%</em></span></li>';
  }

  function filaTabla(f, rankeado) {
    var d = D.dips[f.i];
    var pos = rankeado ? f.pos : 's/d';
    var val = f.comp
      ? '<b>' + Math.round(f.pct * 100) + '%</b><span class="de"> · ' + f.hit + '/' + f.comp + '</span>'
      : '<span class="de">sin votos en común</span>';
    return '<tr>' +
      '<td class="num">' + pos + '</td>' +
      '<td>' + esc(d.n) + '</td>' +
      '<td class="bl-col">' + esc(d.b) + '</td>' +
      '<td class="dist">' + esc(d.d) + '</td>' +
      '<td class="num">' + val + '</td>' +
      '<td class="bar">' + (rankeado && f.comp ? '<span style="width:' + (f.pct * 100).toFixed(1) + '%;background:' + d.c + '"></span>' : '') + '</td>' +
      '</tr>';
  }

  function pintar(a) {
    var r = comparar(a);
    var dentro = r.dentro, fuera = r.fuera, resp = r.resp;
    var pos = 0, prev = null;
    dentro.forEach(function (f, k) {
      var key = Math.round(f.pct * 1000);
      if (key !== prev) { pos = k + 1; prev = key; }
      f.pos = pos;
    });

    var primeros = dentro.filter(function (f) { return f.pos === 1; });
    var media = dentro.length ? dentro.reduce(function (s, f) { return s + f.pct; }, 0) / dentro.length : 0;

    // bloque más frecuente en el primer puesto
    var cuenta = {};
    primeros.forEach(function (f) { var b = D.dips[f.i].b; cuenta[b] = (cuenta[b] || 0) + 1; });
    var moda = Object.keys(cuenta).sort(function (x, y) { return cuenta[y] - cuenta[x]; })[0] || '';

    document.getElementById('resumen').innerHTML =
      '<div class="cifra"><b>' + Math.round(dentro[0].pct * 100) + '%</b><span>coincidencia más alta' +
        (dentro[0].comp !== resp ? ' · ' + dentro[0].hit + ' de ' + dentro[0].comp + ' votaciones' : '') + '</span></div>' +
      '<div class="cifra"><b>' + primeros.length + '</b><span>diputados en el primer puesto</span></div>' +
      '<div class="cifra"><b class="txt">' + esc(moda) + '</b><span>bloque más frecuente entre los primeros</span></div>' +
      '<div class="cifra"><b>' + Math.round(media * 100) + '%</b><span>coincidencia media de los comparados</span></div>';

    document.getElementById('resnota').innerHTML =
      'Respondiste ' + resp + ' de ' + NQ + ' preguntas. Se compararon ' + dentro.length +
      ' diputados con al menos ' + (r.minComp === 1 ? 'una votación' : r.minComp + ' votaciones') +
      ' en común contigo; ' + fuera.length +
      ' quedan al final de la lista por falta de registro suficiente.' +
      (resp < 5 ? ' Con ' + resp + ' respuesta' + (resp === 1 ? '' : 's') + ' el resultado se apoya en muy pocas votaciones.' : '');

    document.getElementById('top').innerHTML = dentro.slice(0, 15).map(filaTop).join('');

    // por bloque
    var bl = {};
    dentro.forEach(function (f) {
      var b = D.dips[f.i].b, c = D.dips[f.i].c;
      if (!bl[b]) bl[b] = { n: 0, s: 0, c: c };
      bl[b].n++; bl[b].s += f.pct;
    });
    var filas = Object.keys(bl).map(function (b) {
      return { b: b, n: bl[b].n, m: bl[b].s / bl[b].n, c: bl[b].c };
    }).sort(function (x, y) { return y.m - x.m; });
    var grandes = filas.filter(function (r) { return r.n >= 2; });
    var chicos = filas.filter(function (r) { return r.n < 2; });
    var htmlBl = grandes.slice(0, 12).map(function (r) {
      return '<tr><td><span class="dot" style="background:' + r.c + '"></span>' + esc(r.b) + '</td>' +
        '<td class="num">' + r.n + '</td><td class="num">' + Math.round(r.m * 100) + '%</td>' +
        '<td class="bar"><span style="width:' + (r.m * 100).toFixed(1) + '%;background:' + r.c + '"></span></td></tr>';
    }).join('');
    if (chicos.length) {
      var sn = chicos.reduce(function (s, r) { return s + r.n; }, 0);
      var sm = chicos.reduce(function (s, r) { return s + r.m * r.n; }, 0) / sn;
      htmlBl += '<tr><td><span class="dot" style="background:#b3ab9e"></span>Bloques con un solo diputado (' + chicos.length + ')</td>' +
        '<td class="num">' + sn + '</td><td class="num">' + Math.round(sm * 100) + '%</td>' +
        '<td class="bar"><span style="width:' + (sm * 100).toFixed(1) + '%;background:#b3ab9e"></span></td></tr>';
    }
    document.getElementById('bloques').innerHTML = htmlBl;

    // respuestas una por una
    var acuerdos = 0;
    document.getElementById('detalle').innerHTML = D.preguntas.map(function (q, i) {
      var y = a[i];
      var top = Math.max(q.s.af, q.s.ne, q.s.ab);
      var mayoria = q.s.af === top ? '1' : (q.s.ne === top ? '2' : '3');
      if (y && y === mayoria) acuerdos++;
      return '<tr><td><b class="mono" style="font-size:11.5px;color:#999083">' + (i + 1 < 10 ? '0' : '') + (i + 1) + '</b> ' +
        esc(q.as) + '</td>' +
        '<td class="tuvoto' + (y ? '' : ' vacio') + '">' + (y ? VOTO[y] : 'Sin responder') + '</td>' +
        '<td class="num">' + q.s.af + '</td><td class="num">' + q.s.ne + '</td><td class="num">' + q.s.ab + '</td></tr>';
    }).join('');

    document.getElementById('mayoria').textContent = resp
      ? 'En ' + acuerdos + ' de las ' + resp + ' votaciones respondidas tu posición coincide con la más votada de la Cámara.'
      : '';

    // lista completa
    document.getElementById('todo').innerHTML =
      dentro.map(function (f) { return filaTabla(f, true); }).join('') +
      fuera.map(function (f) { return filaTabla(f, false); }).join('');
    document.getElementById('cuenta-tabla').textContent = D.dips.length + ' diputados';

    res.hidden = false;
    ultimo = a.join('|');
    stale.hidden = true;
  }

  document.getElementById('test').addEventListener('change', refrescar);
  btn.addEventListener('click', function () {
    var a = respuestas();
    if (!a.filter(Boolean).length) return;
    pintar(a);
    res.scrollIntoView({ behavior: 'smooth', block: 'start' });
  });
  rst.addEventListener('click', function () {
    document.querySelectorAll('input[type=radio]').forEach(function (el) { el.checked = false; });
    res.hidden = true;
    ultimo = null;
    stale.hidden = true;
    refrescar();
    document.getElementById('test').scrollIntoView({ behavior: 'smooth', block: 'start' });
  });
  refrescar();
})();
"""

HTML = f"""<!DOCTYPE html>
<html lang="es-AR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Votá como tu diputado · Cámara de Diputados</title>
<meta name="description" content="Diez votaciones nominales del período 144. Respondé cada una y compará tu posición con el voto registrado de los 256 diputados.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Public+Sans:wght@300;400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>{CSS}</style>
</head>
<body>

<nav class="top"><div class="wrap">
  <a class="brand" href="/">Corvus Lab</a>
  <div><a href="/congreso">Congreso</a> · <a href="/mapa">Mapa</a> · <a href="/proyectos">Trabajos</a></div>
</div></nav>

<header class="hero"><div class="wrap">
  <div class="kicker">Cámara de Diputados · Período 144 · 2026</div>
  <h1>Votá como tu diputado</h1>
  <p class="dek">Diez votaciones nominales del período, cada una con la fecha y el número de acta. Elegís una posición en cada pregunta y la página compara tus respuestas con el voto registrado de los {len(DIPS_JS)} diputados.</p>
</div></header>

<div class="cifras">
  <div class="cifra"><b>10</b><span>votaciones en el test</span></div>
  <div class="cifra"><b>{len(DIPS_JS)}</b><span>diputados en el padrón del período</span></div>
  <div class="cifra"><b>{len(ACTAS)}</b><span>votaciones nominales en las actas</span></div>
  <div class="cifra"><b>3</b><span>posiciones por acta: a favor, en contra, abstención</span></div>
</div>

<section><div class="wrap">
  <h2>Las diez votaciones <span>· una respuesta por pregunta</span></h2>
  <p class="intro">Podés dejar preguntas sin responder: esas no suman ni restan en el cálculo. La aclaración indica qué parte del proyecto se votó.</p>

  <div id="test">
{TARJETAS}
    <div class="acciones">
      <button id="calc" class="btn" type="button" disabled>Calcular coincidencia</button>
      <button id="reset" class="btn ghost" type="button">Reiniciar</button>
      <span id="prog" class="prog mono">0 de 10 respondidas</span>
    </div>
    <p id="stale" class="stale" hidden>Cambiaste respuestas. Volvé a calcular para actualizar el ranking.</p>
  </div>
</div></section>

<section id="res" hidden><div class="wrap">
  <h2>Coincidencia <span>· tus respuestas contra el registro de cada diputado</span></h2>
  <p class="resnota" id="resnota" aria-live="polite"></p>
  <div class="resumen" id="resumen"></div>

  <h3 class="sub">Los quince más cerca</h3>
  <ol class="rank" id="top"></ol>
  <p class="pie">La fracción son las coincidencias sobre las votaciones comparables. Los que empatan comparten posición y aparecen por orden alfabético. La lista completa está al final de la página.</p>

  <h3 class="sub">Coincidencia por bloque</h3>
  <table>
    <thead><tr><th>Bloque</th><th class="num">Diputados</th><th class="num">Media</th><th class="bar"></th></tr></thead>
    <tbody id="bloques"></tbody>
  </table>

  <h3 class="sub">Tus respuestas, una por una</h3>
  <p class="pie" id="mayoria"></p>
  <div class="tabla-scroll">
    <table style="margin-top:10px">
      <thead><tr><th>Votación</th><th>Tu voto</th><th class="num">A favor</th><th class="num">En contra</th><th class="num">Abstención</th></tr></thead>
      <tbody id="detalle"></tbody>
    </table>
  </div>

  <details class="todos">
    <summary>Lista completa · <span id="cuenta-tabla"></span></summary>
    <div class="tabla-scroll">
      <table>
        <thead><tr><th class="num">Pos.</th><th>Diputado</th><th class="bl-col">Bloque</th><th class="dist">Distrito</th><th class="num">Coincidencia</th><th class="bar"></th></tr></thead>
        <tbody id="todo"></tbody>
      </table>
    </div>
  </details>
</div></section>

<div class="metodo"><div class="wrap">
  <h2>Método</h2>
  <p>Las diez preguntas corresponden a diez votaciones nominales del período 144. Cada tarjeta indica la fecha, el número de acta y el asunto tal como figura en el registro.</p>
  <p>Cada respuesta se compara con el voto que quedó en el acta para cada diputado: a favor, en contra o abstención. La coincidencia es la cantidad de respuestas iguales sobre la cantidad de votaciones donde hubo respuesta tuya y voto registrado del diputado.</p>
  <p>Las preguntas que dejaste sin responder se descartan del cálculo, para tu respuesta y para todos los diputados por igual. Un diputado sin voto registrado en una votación tampoco entra en esa pregunta, por ausencia o por licencia. Hay {N_SIN_DATOS} diputados sin ningún voto registrado en estas diez votaciones, así que quedan siempre al final de la lista.</p>
  <p>Para entrar al ranking hacen falta al menos seis votaciones comparables cuando respondiste las diez, y el 60% de tus respuestas cuando respondiste menos. Los que quedan por debajo aparecen al final, marcados sin datos suficientes.</p>
  <p>Con diez preguntas hay once resultados posibles, así que muchos diputados empatan y comparten puesto. Dentro de un empate ordena la cantidad de votaciones comparables y después el orden alfabético.</p>
  <p>La abstención se compara como cualquier otra posición. En dos de las diez votaciones no hubo votos en contra en el registro, así que una respuesta en contra no coincide con nadie en esas dos preguntas.</p>
  <p>El resultado mide coincidencia en votos registrados. No mide afinidad política, intención de voto ni comportamiento futuro, y no dice si un voto fue acertado.</p>
  <p>Fuente: Honorable Cámara de Diputados de la Nación, actas de votación nominal, período 144.</p>
</div></div>

<footer><div class="wrap">Corvus Lab · datos abiertos del Congreso · <a href="/mapa">Mapa de votaciones</a> · <a href="/congreso">Los que legislan</a></div></footer>

<script id="datos" type="application/json">{DATOS}</script>
<script>{JS}</script>
</body>
</html>
"""

with open(OUT, "w", encoding="utf-8") as fh:
    fh.write(HTML)
print(f"{OUT}: {len(HTML)} bytes, {len(DIPS_JS)} diputados, {len(PREG_JS)} preguntas")
