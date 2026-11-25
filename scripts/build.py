#!/usr/bin/env python3
"""Genera los SVG del perfil (tema claro y oscuro) en ../assets.

Uso:  python3 scripts/build.py
Requiere: fonttools y brotli (pip install fonttools brotli)

Todo el contenido editable (textos, proyectos, formación) está en la sección DATOS.
Las fuentes Inter y JetBrains Mono (licencia OFL) se incrustan en cada SVG para que
el perfil se vea igual en cualquier sistema.
"""
from __future__ import annotations

import base64
import html
from pathlib import Path

from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent.parent
FONTS = Path(__file__).resolve().parent / "fonts"
OUT = ROOT / "assets"

# =============================================================================
# PALETA — "Espresso & Code"
# =============================================================================
THEMES = {
    "dark": dict(
        bg="#15100D", bg2="#1F1713", surface="#1C1512", surface2="#241B16",
        border="#3A2B23", text="#F4EADF", muted="#B4A293", faint="#7D6B5E",
        copper="#E3894C", gold="#D8B07A", teal="#62B6A4", rose="#DB7F7A",
        sky="#86A9D6", sage="#A3C27F", grid="#2C211B", crema="#C89A6A",
    ),
    "light": dict(
        bg="#FBF6F0", bg2="#F3EADF", surface="#FFFFFF", surface2="#FAF4EC",
        border="#E6D7C6", text="#2A1D16", muted="#6E5C50", faint="#9C8A7C",
        copper="#B5612C", gold="#9A6E33", teal="#2A7E6D", rose="#B44E49",
        sky="#3F6EA8", sage="#5E8436", grid="#EDE1D3", crema="#B07D4A",
    ),
}

# =============================================================================
# DATOS
# =============================================================================
PERFIL = dict(
    nombre="Sebastián Muñoz Rivera",
    prompt="~/sebakine $ whoami",
    titular="Software Engineer · Backend & Datos",
    bajada="Construyo backends con arquitectura en capas, autenticación robusta y pruebas automatizadas.",
    bajada2="Fundador de CoffeeLink: infraestructura y datos para el café de especialidad en LATAM.",
    chips=[("Chile", "faint"), ("Barista de especialidad", "gold"), ("Abierto a oportunidades", "teal")],
)

ABOUT_CODE = [
    [("kw", "const "), ("var", "sebastian"), ("p", " = {")],
    [("prop", "  rol"), ("p", ": "), ("str", '"Software Engineer"'), ("p", ",")],
    [("prop", "  enfoque"), ("p", ": ["), ("str", '"Backend con Node.js"'), ("p", ", "), ("str", '"Datos con Python"'), ("p", "],")],
    [("prop", "  construyendo"), ("p", ": "), ("str", '"CoffeeLink"'), ("p", ","), ("com", "  // POS + plataforma web para cafeterías")],
    [("prop", "  practicas"), ("p", ": ["), ("str", '"arquitectura en capas"'), ("p", ", "), ("str", '"tests"'), ("p", ", "), ("str", '"CI/CD"'), ("p", ", "), ("str", '"seguridad"'), ("p", "],")],
    [("prop", "  aprendiendo"), ("p", ": ["), ("str", '"SQL"'), ("p", ", "), ("str", '"modelado de datos"'), ("p", ", "), ("str", '"pipelines"'), ("p", "],")],
    [("prop", "  ubicacion"), ("p", ": "), ("str", '"Chile"'), ("p", ",")],
    [("prop", "  datoCurioso"), ("p", ": "), ("str", '"barista de especialidad"'), ("p", ",")],
    [("p", "} "), ("kw", "as const"), ("p", ";")],
]

SECCIONES = [
    ("01", "Sobre mí", "// quién soy"),
    ("02", "Stack", "// herramientas con las que trabajo"),
    ("03", "Proyectos destacados", "// lo que mejor me representa"),
    ("04", "Formación", "// de dónde viene la base"),
    ("05", "Actividad", "// contribuciones del último año"),
]

PROYECTOS = [
    dict(slug="entrega-5-backend-2-coderhouse", titulo="Eventos e Inscripciones API",
         categoria="BACKEND · SEGURIDAD", acento="copper",
         desc="API de eventos con JWT en cookie HttpOnly y autorización por roles (user, organizer, admin). Validación con Zod, Helmet, rate limiting, tests y CI.",
         tags=["Node.js", "Express", "MongoDB", "Zod", "GitHub Actions"], curso="Programación Backend II"),
    dict(slug="adoptme-api", titulo="Adoptme API",
         categoria="BACKEND · CALIDAD", acento="teal",
         desc="API de adopciones con datos de prueba (Faker), documentación Swagger, pruebas funcionales con Mocha, Chai y Supertest, y contenedor Docker.",
         tags=["Node.js", "Swagger", "Mocha", "Supertest", "Docker"], curso="Programación Backend III"),
    dict(slug="ecommerce-backend-node", titulo="E-commerce Backend",
         categoria="BACKEND · ARQUITECTURA", acento="gold",
         desc="Backend en capas DAO, Repository y DTO. Passport + JWT, roles, recuperación de contraseña por correo y compra con tickets y control de stock.",
         tags=["Node.js", "Express", "Passport", "Nodemailer", "MongoDB"], curso="Programación Backend II"),
    dict(slug="entrega-final-backend-1-coderhouse", titulo="Turnos y Reservas",
         categoria="BACKEND · EVOLUCIÓN", acento="sky",
         desc="Sistema de turnos construido en 8 etapas: de FileSystem a MongoDB, con arquitectura en capas, Zod, populate, vistas Handlebars y tiempo real con Socket.io.",
         tags=["Express 5", "Mongoose", "Zod", "Socket.io", "Handlebars"], curso="Programación Backend I"),
    dict(slug="CafePrompt", titulo="CafePrompt",
         categoria="IA GENERATIVA · PYTHON", acento="rose",
         desc="Convierte la ficha técnica de un lote de café en un kit de contenido (texto, imagen y audio) con una cadena de prompts y evaluación LLM-as-judge.",
         tags=["Python", "Gemini", "Gradio", "Colab", "gTTS"], curso="IA: Generación de Prompts"),
    dict(slug="coffeelink-store-react", titulo="CoffeeLink Store",
         categoria="FRONTEND · E-COMMERCE", acento="sage",
         desc="SPA de café de especialidad: catálogo desde Firestore, carrito global con Context y checkout que descuenta stock en un lote atómico.",
         tags=["React 19", "Vite", "Tailwind CSS", "Firebase"], curso="React JS"),
]

COFFEELINK = dict(
    titulo="CoffeeLink",
    categoria="PROYECTO PRINCIPAL · EN DESARROLLO",
    desc="Infraestructura financiera y capa de datos para cafeterías y tostadurías de especialidad en Latinoamérica: un POS de escritorio para la operación diaria y una plataforma web con paneles por rol y servicios analíticos en Python.",
    modulos=[("POS", "Electron · React · NestJS · Prisma"), ("Platform Web", "React · Vite · Tailwind · NestJS"), ("Datos", "Servicios analíticos en Python")],
    tags=["TypeScript", "Nx monorepo", "NestJS", "Prisma", "Electron", "Stripe"],
    nota="Código privado",
)

FORMACION = [
    ("Programación Backend I · II · III", "Node.js, Express, MongoDB, arquitectura en capas, testing, Docker", "copper"),
    ("React JS", "SPA con React, Context, Firebase", "sage"),
    ("Python", "Django, CRUD, autenticación", "sky"),
    ("JavaScript y Desarrollo Web", "HTML, Sass, JavaScript, DOM", "gold"),
    ("Ciberseguridad", "Hardening de Linux y Windows, laboratorios aislados", "teal"),
    ("IA: Generación de Prompts", "Prompt engineering, Gemini, evaluación de LLM", "rose"),
]
FORMACION_INSTITUCION = "Coderhouse"

# =============================================================================
# FUENTES Y MEDICIÓN DE TEXTO
# =============================================================================
FONT_FILES = {
    ("Inter", 400): "inter-400.woff2", ("Inter", 600): "inter-600.woff2",
    ("Inter", 800): "inter-800.woff2", ("JBMono", 400): "mono-400.woff2",
    ("JBMono", 700): "mono-700.woff2",
}
_metrics: dict = {}


def _font(fam, w):
    key = (fam, w)
    if key not in _metrics:
        f = TTFont(FONTS / FONT_FILES[key])
        _metrics[key] = (f.getBestCmap(), f["hmtx"].metrics, f["head"].unitsPerEm)
    return _metrics[key]


def text_width(s: str, size: float, fam="Inter", w=400) -> float:
    cmap, hmtx, upm = _font(fam, w)
    total = 0
    for ch in s:
        g = cmap.get(ord(ch))
        total += hmtx[g][0] if g in hmtx else upm * 0.55
    return total * size / upm


def wrap(s: str, size: float, max_w: float, fam="Inter", w=400) -> list[str]:
    lines, cur = [], ""
    for word in s.split():
        trial = f"{cur} {word}".strip()
        if text_width(trial, size, fam, w) <= max_w:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def font_css(*keys) -> str:
    rules = []
    for fam, w in keys:
        data = base64.b64encode((FONTS / FONT_FILES[(fam, w)]).read_bytes()).decode()
        rules.append(f"@font-face{{font-family:'{fam}';font-weight:{w};src:url(data:font/woff2;base64,{data}) format('woff2');}}")
    return "".join(rules)


SANS = "'Inter','Segoe UI',-apple-system,Helvetica,Arial,sans-serif"
MONO = "'JBMono','JetBrains Mono',Consolas,'SFMono-Regular',Menlo,monospace"
esc = html.escape


def svg(w, h, body, css, title):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{esc(title)}">'
            f"<title>{esc(title)}</title><style>{css}</style>{body}</svg>")


def base_css(c, fonts=(("Inter", 400), ("Inter", 600), ("Inter", 800), ("JBMono", 400), ("JBMono", 700))):
    return font_css(*fonts) + (
        f".sans{{font-family:{SANS}}}.mono{{font-family:{MONO}}}"
        "@media (prefers-reduced-motion: reduce){*{animation:none!important}}"
    )


def pill(x, y, label, color, c, size=13, fam="JBMono", w=500, pad=12, h=28, fill_op=0.12):
    tw = text_width(label, size, "JBMono" if fam == "JBMono" else "Inter", 400 if fam == "JBMono" else 600)
    width = tw + pad * 2
    cls = "mono" if fam == "JBMono" else "sans"
    return (f'<rect x="{x:.1f}" y="{y}" width="{width:.1f}" height="{h}" rx="{h/2}" fill="{color}" fill-opacity="{fill_op}" stroke="{color}" stroke-opacity="0.35"/>'
            f'<text x="{x+pad:.1f}" y="{y+h/2+size*0.36:.1f}" class="{cls}" font-size="{size}" font-weight="{400 if fam=="JBMono" else 600}" fill="{color}">{esc(label)}</text>'), width


def dot_grid(w, h, c, step=26, r=1.1, op=0.9):
    return (f'<defs><pattern id="g" width="{step}" height="{step}" patternUnits="userSpaceOnUse">'
            f'<circle cx="2" cy="2" r="{r}" fill="{c["grid"]}" opacity="{op}"/></pattern></defs>'
            f'<rect width="{w}" height="{h}" fill="url(#g)"/>')


# =============================================================================
# COMPONENTES
# =============================================================================
def header(c):
    W, H = 1200, 400
    css = base_css(c) + (
        "@keyframes steam{0%{transform:translateY(8px);opacity:0}30%{opacity:.85}100%{transform:translateY(-26px);opacity:0}}"
        ".s1,.s2,.s3{animation:steam 3.6s ease-in-out infinite}.s2{animation-delay:1.2s}.s3{animation-delay:2.4s}"
        "@keyframes blink{0%,49%{opacity:1}50%,100%{opacity:0}}.cur{animation:blink 1.1s step-end infinite}"
        "@keyframes pulse{0%{r:4;opacity:1}100%{r:11;opacity:0}}.pl{animation:pulse 2s ease-out infinite}"
        "@keyframes rise{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}"
        ".r1{animation:rise .7s ease-out both}.r2{animation:rise .7s .15s ease-out both}.r3{animation:rise .7s .3s ease-out both}.r4{animation:rise .7s .45s ease-out both}"
    )
    b = [
        f'<defs><linearGradient id="bgg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{c["bg"]}"/><stop offset="1" stop-color="{c["bg2"]}"/></linearGradient>'
        f'<radialGradient id="glow" cx="0.82" cy="0.45" r="0.45"><stop offset="0" stop-color="{c["copper"]}" stop-opacity="0.18"/><stop offset="1" stop-color="{c["copper"]}" stop-opacity="0"/></radialGradient>'
        f'<clipPath id="clip"><rect width="{W}" height="{H}" rx="24"/></clipPath></defs>',
        f'<g clip-path="url(#clip)"><rect width="{W}" height="{H}" fill="url(#bgg)"/>',
        dot_grid(W, H, c),
        f'<rect width="{W}" height="{H}" fill="url(#glow)"/>',
        f'<rect x="0" y="0" width="{W}" height="5" fill="{c["copper"]}"/></g>',
        f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="23.5" fill="none" stroke="{c["border"]}"/>',
    ]
    x = 64
    pw = text_width(PERFIL["prompt"], 17, "JBMono", 400)
    b.append(f'<g class="r1"><text x="{x}" y="92" class="mono" font-size="17" fill="{c["muted"]}"><tspan fill="{c["teal"]}">~/sebakine</tspan> <tspan fill="{c["copper"]}">$</tspan> whoami</text>'
             f'<rect class="cur" x="{x+pw+8:.1f}" y="77" width="10" height="19" fill="{c["copper"]}"/></g>')
    b.append(f'<text class="sans r2" x="{x}" y="160" font-size="58" font-weight="800" fill="{c["text"]}" letter-spacing="-1.2">{esc(PERFIL["nombre"])}</text>')
    b.append(f'<text class="sans r3" x="{x}" y="206" font-size="25" font-weight="600" fill="{c["gold"]}">{esc(PERFIL["titular"])}</text>')
    b.append(f'<g class="r3"><text class="sans" x="{x}" y="246" font-size="17" fill="{c["muted"]}">{esc(PERFIL["bajada"])}</text>'
             f'<text class="sans" x="{x}" y="272" font-size="17" fill="{c["muted"]}">{esc(PERFIL["bajada2"])}</text></g>')
    cx, parts = x, []
    for label, col in PERFIL["chips"]:
        color = c[col]
        if col == "teal":
            tw = text_width(label, 14, "Inter", 600)
            wdt = tw + 44
            parts.append(f'<rect x="{cx}" y="310" width="{wdt:.1f}" height="34" rx="17" fill="{color}" fill-opacity="0.12" stroke="{color}" stroke-opacity="0.4"/>'
                         f'<circle cx="{cx+17}" cy="327" r="4" fill="{color}"/><circle class="pl" cx="{cx+17}" cy="327" r="4" fill="none" stroke="{color}" stroke-width="1.5"/>'
                         f'<text x="{cx+30}" y="332" class="sans" font-size="14" font-weight="600" fill="{color}">{esc(label)}</text>')
        else:
            p, wdt = pill(cx, 310, label, color, c, size=14, fam="Inter", h=34, pad=16)
            parts.append(p)
        cx += wdt + 10
    b.append(f'<g class="r4">{"".join(parts)}</g>')

    # Ilustración original: taza con arte latte en forma de </>
    ox, oy = 1008, 208
    cu, cr, cg = c["copper"], c["crema"], c["gold"]
    b.append(f'<g transform="translate({ox},{oy}) scale(0.92)">'
             f'<ellipse cx="0" cy="118" rx="150" ry="22" fill="{cu}" fill-opacity="0.10" stroke="{cu}" stroke-opacity="0.55" stroke-width="2"/>'
             f'<ellipse cx="0" cy="112" rx="104" ry="13" fill="none" stroke="{cu}" stroke-opacity="0.35" stroke-width="1.5"/>'
             f'<path d="M-98,-10 L-84,86 Q-80,108 -56,110 L56,110 Q80,108 84,86 L98,-10 Z" fill="{c["surface2"]}" stroke="{cu}" stroke-width="3" stroke-linejoin="round"/>'
             f'<path d="M96,10 Q150,8 146,46 Q142,84 86,80" fill="none" stroke="{cu}" stroke-width="3" stroke-linecap="round"/>'
             f'<path d="M96,22 Q130,22 128,46 Q126,68 89,68" fill="none" stroke="{cu}" stroke-opacity="0.4" stroke-width="2" stroke-linecap="round"/>'
             f'<ellipse cx="0" cy="-10" rx="98" ry="20" fill="{cr}" fill-opacity="0.9" stroke="{cu}" stroke-width="3"/>'
             f'<ellipse cx="0" cy="-10" rx="80" ry="14" fill="{c["bg"]}" fill-opacity="0.55"/>'
             f'<text x="0" y="-3" text-anchor="middle" class="mono" font-size="22" font-weight="700" fill="{cr}">&lt;/&gt;</text>'
             f'<g fill="none" stroke="{cg}" stroke-width="3" stroke-linecap="round" opacity="0.9">'
             f'<path class="s1" d="M-40,-48 q-12,-16 0,-32 q12,-16 0,-32"/>'
             f'<path class="s2" d="M0,-52 q-12,-16 0,-32 q12,-16 0,-32"/>'
             f'<path class="s3" d="M40,-48 q-12,-16 0,-32 q12,-16 0,-32"/></g>'
             f'<text x="-170" y="-108" class="mono" font-size="16" fill="{c["faint"]}">{{ }}</text>'
             f'<text x="118" y="-118" class="mono" font-size="16" fill="{c["faint"]}">=&gt;</text>'
             f'<text x="108" y="-62" class="mono" font-size="14" fill="{c["faint"]}">200 OK</text>'
             "</g>")
    return svg(W, H, "".join(b), css, f"{PERFIL['nombre']} — {PERFIL['titular']}")


def section(c, num, title, comment):
    W, H = 1200, 76
    tw = text_width(title, 30, "Inter", 800)
    nw = text_width(num, 18, "JBMono", 700)
    x2 = 0 + nw + 18 + tw + 24
    cw = text_width(comment, 15, "JBMono", 400)
    body = (f'<text x="0" y="48" class="mono" font-size="18" font-weight="700" fill="{c["copper"]}">{num}</text>'
            f'<text x="{nw+18:.1f}" y="50" class="sans" font-size="30" font-weight="800" fill="{c["text"]}" letter-spacing="-0.4">{esc(title)}</text>'
            f'<defs><linearGradient id="ln" x1="0" x2="1"><stop offset="0" stop-color="{c["copper"]}" stop-opacity="0.8"/><stop offset="1" stop-color="{c["border"]}" stop-opacity="0.4"/></linearGradient></defs>'
            f'<rect x="{x2:.1f}" y="40" width="{max(40, W - x2 - cw - 24):.1f}" height="2" rx="1" fill="url(#ln)"/>'
            f'<text x="{W}" y="47" text-anchor="end" class="mono" font-size="15" fill="{c["faint"]}">{esc(comment)}</text>')
    return svg(W, H, body, base_css(c, (("Inter", 800), ("JBMono", 400), ("JBMono", 700))), f"{num} {title}")


def about(c):
    W = 1200
    lh, top = 34, 92
    H = top + lh * (len(ABOUT_CODE) - 1) + 38
    col = dict(kw=c["copper"], var=c["gold"], prop=c["text"], str=c["teal"], p=c["muted"], com=c["faint"])
    css = base_css(c, (("JBMono", 400), ("JBMono", 700))) + (
        "@keyframes ln{from{opacity:0;transform:translateX(-6px)}to{opacity:1;transform:none}}"
        + "".join(f".l{i}{{animation:ln .45s {0.12*i:.2f}s ease-out both}}" for i in range(len(ABOUT_CODE)))
    )
    b = [f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="18" fill="{c["surface"]}" stroke="{c["border"]}"/>',
         f'<path d="M0.5,52 H{W-0.5}" stroke="{c["border"]}"/>',
         f'<path d="M18.5,0.5 H{W-18.5} A18,18 0 0 1 {W-0.5},18.5 V52 H0.5 V18.5 A18,18 0 0 1 18.5,0.5 Z" fill="{c["surface2"]}"/>',
         f'<path d="M0.5,52 H{W-0.5}" stroke="{c["border"]}"/>']
    for i, k in enumerate(["copper", "gold", "teal"]):
        b.append(f'<circle cx="{28+i*22}" cy="26" r="6.5" fill="{c[k]}"/>')
    b.append(f'<rect x="110" y="12" width="150" height="40" rx="8" fill="{c["surface"]}"/><text x="128" y="37" class="mono" font-size="14" fill="{c["text"]}">sebastian.ts</text>'
             f'<text x="{W-24}" y="32" text-anchor="end" class="mono" font-size="13" fill="{c["faint"]}">TypeScript · UTF-8</text>')
    for i, line in enumerate(ABOUT_CODE):
        y = top + i * lh
        spans = "".join(f'<tspan fill="{col[k]}"{" font-style=\"italic\"" if k=="com" else ""}>{esc(t)}</tspan>' for k, t in line)
        b.append(f'<g class="l{i}"><text x="40" y="{y}" text-anchor="end" class="mono" font-size="15" fill="{c["faint"]}" opacity="0.7">{i+1}</text>'
                 f'<text x="64" y="{y}" class="mono" font-size="17" xml:space="preserve">{spans}</text></g>')
    return svg(W, H, "".join(b), css, "Sobre mí: Software Engineer, backend con Node.js y datos con Python; construyendo CoffeeLink; Chile.")


def project_card(c, p):
    W, H = 590, 300
    a = c[p["acento"]]
    css = base_css(c, (("Inter", 400), ("Inter", 800), ("JBMono", 400), ("JBMono", 700)))
    b = [f'<defs><linearGradient id="cg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{a}" stop-opacity="0.10"/><stop offset="0.55" stop-color="{a}" stop-opacity="0"/></linearGradient></defs>',
         f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="18" fill="{c["surface"]}" stroke="{c["border"]}"/>',
         f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="18" fill="url(#cg)"/>',
         f'<rect x="28" y="0.5" width="64" height="4" rx="2" fill="{a}"/>',
         f'<text x="28" y="44" class="mono" font-size="12.5" font-weight="700" fill="{a}" letter-spacing="1.2">{esc(p["categoria"])}</text>',
         f'<text x="28" y="84" class="sans" font-size="27" font-weight="800" fill="{c["text"]}" letter-spacing="-0.4">{esc(p["titulo"])}</text>',
         f'<text x="28" y="110" class="mono" font-size="13" fill="{c["faint"]}">sebakine/{esc(p["slug"])}</text>']
    for i, line in enumerate(wrap(p["desc"], 15.5, W - 56)[:3]):
        b.append(f'<text x="28" y="{146 + i*24}" class="sans" font-size="15.5" fill="{c["muted"]}">{esc(line)}</text>')
    x = 28
    for t in p["tags"]:
        s, wdt = pill(x, 222, t, a, c, size=12.5, h=26, pad=10)
        if x + wdt > W - 28:
            break
        b.append(s)
        x += wdt + 8
    b.append(f'<path d="M28,{H-34} H{W-28}" stroke="{c["border"]}" stroke-dasharray="3 5"/>'
             f'<text x="28" y="{H-12}" class="mono" font-size="12.5" fill="{c["faint"]}">{esc(p["curso"])} · Coderhouse</text>'
             f'<text x="{W-28}" y="{H-12}" text-anchor="end" class="mono" font-size="13" font-weight="700" fill="{a}">ver repositorio →</text>')
    return svg(W, H, "".join(b), css, f'{p["titulo"]}: {p["desc"]}')


def coffeelink_card(c):
    W, H = 1200, 290
    d = COFFEELINK
    css = base_css(c, (("Inter", 400), ("Inter", 600), ("Inter", 800), ("JBMono", 400), ("JBMono", 700))) + (
        "@keyframes pulse{0%{r:4;opacity:1}100%{r:11;opacity:0}}.pl{animation:pulse 2s ease-out infinite}")
    b = [f'<defs><linearGradient id="cl" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{c["copper"]}" stop-opacity="0.16"/><stop offset="0.6" stop-color="{c["gold"]}" stop-opacity="0.04"/><stop offset="1" stop-color="{c["teal"]}" stop-opacity="0.10"/></linearGradient>'
         f'<clipPath id="cc"><rect width="{W}" height="{H}" rx="20"/></clipPath></defs>',
         f'<g clip-path="url(#cc)"><rect width="{W}" height="{H}" fill="{c["surface"]}"/><rect width="{W}" height="{H}" fill="url(#cl)"/>'
         f'<rect width="6" height="{H}" fill="{c["copper"]}"/></g>',
         f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="19.5" fill="none" stroke="{c["border"]}"/>',
         f'<circle cx="44" cy="40" r="4" fill="{c["teal"]}"/><circle class="pl" cx="44" cy="40" r="4" fill="none" stroke="{c["teal"]}" stroke-width="1.5"/>',
         f'<text x="58" y="45" class="mono" font-size="13" font-weight="700" fill="{c["teal"]}" letter-spacing="1.2">{esc(d["categoria"])}</text>',
         f'<text x="38" y="96" class="sans" font-size="40" font-weight="800" fill="{c["text"]}" letter-spacing="-0.8">{esc(d["titulo"])}</text>']
    for i, line in enumerate(wrap(d["desc"], 16, 600)):
        b.append(f'<text x="38" y="{132 + i*25}" class="sans" font-size="16" fill="{c["muted"]}">{esc(line)}</text>')
    x = 38
    for t in d["tags"]:
        s, wdt = pill(x, 232, t, c["copper"], c, size=12.5, h=26, pad=10)
        b.append(s)
        x += wdt + 8
    mx, my = 720, 34
    for i, (name, stack) in enumerate(d["modulos"]):
        y = my + i * 74
        b.append(f'<rect x="{mx}" y="{y}" width="440" height="62" rx="12" fill="{c["surface2"]}" stroke="{c["border"]}"/>'
                 f'<rect x="{mx}" y="{y+14}" width="3" height="34" rx="1.5" fill="{[c["copper"], c["gold"], c["teal"]][i]}"/>'
                 f'<text x="{mx+22}" y="{y+27}" class="sans" font-size="17" font-weight="600" fill="{c["text"]}">{esc(name)}</text>'
                 f'<text x="{mx+22}" y="{y+48}" class="mono" font-size="13" fill="{c["faint"]}">{esc(stack)}</text>')
    b.append(f'<text x="{W-40}" y="{H-24}" text-anchor="end" class="mono" font-size="12.5" fill="{c["faint"]}">{esc(d["nota"])}</text>')
    return svg(W, H, "".join(b), css, f'{d["titulo"]}: {d["desc"]}')


def education(c):
    W = 1200
    cols, cw, ch, gap = 3, 376, 100, 16
    rows = (len(FORMACION) + cols - 1) // cols
    top = 54
    H = top + rows * ch + (rows - 1) * gap + 4
    css = base_css(c, (("Inter", 400), ("Inter", 600), ("Inter", 800), ("JBMono", 400), ("JBMono", 700)))
    b = [f'<text x="0" y="24" class="mono" font-size="14" fill="{c["faint"]}">Institución</text>'
         f'<text x="104" y="24" class="sans" font-size="18" font-weight="800" fill="{c["text"]}">{esc(FORMACION_INSTITUCION)}</text>']
    for i, (curso, detalle, k) in enumerate(FORMACION):
        r, q = divmod(i, cols)
        x, y = q * (cw + 36), top + r * (ch + gap)
        a = c[k]
        b.append(f'<rect x="{x+0.5}" y="{y+0.5}" width="{cw}" height="{ch}" rx="14" fill="{c["surface"]}" stroke="{c["border"]}"/>'
                 f'<rect x="{x+20}" y="{y+22}" width="10" height="10" rx="2.5" fill="{a}"/>'
                 f'<text x="{x+42}" y="{y+32}" class="sans" font-size="16.5" font-weight="600" fill="{c["text"]}">{esc(curso)}</text>')
        for j, line in enumerate(wrap(detalle, 14, cw - 62)[:2]):
            b.append(f'<text x="{x+42}" y="{y+60+j*21}" class="sans" font-size="14" fill="{c["muted"]}">{esc(line)}</text>')
    alt = "Formación en Coderhouse: " + "; ".join(f for f, _, _ in FORMACION)
    return svg(W, H, "".join(b), css, alt)


def footer(c):
    W, H = 1200, 120
    css = base_css(c, (("JBMono", 400),)) + "@keyframes dash{to{stroke-dashoffset:-40}}.w{animation:dash 6s linear infinite}"
    path = "M0,60 " + " ".join(f"Q{x+37.5},{40 if (x//75)%2==0 else 80} {x+75},60" for x in range(0, W, 75))
    body = (f'<defs><clipPath id="fc"><rect x="0" y="0" width="{W/2-250}" height="{H}"/><rect x="{W/2+250}" y="0" width="{W/2-250}" height="{H}"/></clipPath></defs>'
            f'<path class="w" clip-path="url(#fc)" d="{path}" fill="none" stroke="{c["copper"]}" stroke-opacity="0.5" stroke-width="2" stroke-dasharray="8 12"/>'
            f'<text x="{W/2}" y="66" text-anchor="middle" class="mono" font-size="15" fill="{c["muted"]}">hecho con código y café de especialidad</text>')
    return svg(W, H, body, css, "Hecho con código y café de especialidad")


# =============================================================================
def main():
    OUT.mkdir(exist_ok=True)
    (OUT / "projects").mkdir(exist_ok=True)
    (OUT / "sections").mkdir(exist_ok=True)
    for name, c in THEMES.items():
        (OUT / f"header-{name}.svg").write_text(header(c), encoding="utf-8")
        (OUT / f"about-{name}.svg").write_text(about(c), encoding="utf-8")
        (OUT / f"coffeelink-{name}.svg").write_text(coffeelink_card(c), encoding="utf-8")
        (OUT / f"education-{name}.svg").write_text(education(c), encoding="utf-8")
        (OUT / f"footer-{name}.svg").write_text(footer(c), encoding="utf-8")
        for num, title, comment in SECCIONES:
            (OUT / "sections" / f"{num}-{name}.svg").write_text(section(c, num, title, comment), encoding="utf-8")
        for p in PROYECTOS:
            (OUT / "projects" / f"{p['slug'].lower()}-{name}.svg").write_text(project_card(c, p), encoding="utf-8")
    print("SVG generados en", OUT)


if __name__ == "__main__":
    main()
