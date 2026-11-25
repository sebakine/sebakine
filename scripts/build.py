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
    titular="Fullstack Developer · Node.js · Python · Datos e IA",
    bajada="Construyo APIs y aplicaciones web con arquitectura en capas, autenticación robusta y pruebas.",
    bajada2="Enfoco mi crecimiento en ingeniería de datos e IA con Python. Fundador de CoffeeLink.",
    chips=[("Chile", "faint"), ("Inglés C1", "gold"), ("Remoto · híbrido · presencial", "faint"), ("Disponibilidad inmediata", "teal")],
)

ABOUT_CODE = [
    [("kw", "const "), ("var", "sebastian"), ("p", " = {")],
    [("prop", "  rol"), ("p", ": "), ("str", '"Fullstack Developer"'), ("p", ",")],
    [("prop", "  stack"), ("p", ": ["), ("str", '"Node.js"'), ("p", ", "), ("str", '"Express"'), ("p", ", "), ("str", '"MongoDB"'), ("p", ", "), ("str", '"React"'), ("p", ", "), ("str", '"Python"'), ("p", "],")],
    [("prop", "  enfoque"), ("p", ": ["), ("str", '"Ingeniería de datos"'), ("p", ", "), ("str", '"AI Engineering"'), ("p", "],")],
    [("prop", "  construyendo"), ("p", ": "), ("str", '"CoffeeLink"'), ("p", ","), ("com", "  // POS + plataforma para cafeterías de especialidad")],
    [("prop", "  practicas"), ("p", ": ["), ("str", '"arquitectura en capas"'), ("p", ", "), ("str", '"testing"'), ("p", ", "), ("str", '"CI/CD"'), ("p", ", "), ("str", '"seguridad"'), ("p", "],")],
    [("prop", "  idiomas"), ("p", ": ["), ("str", '"Español nativo"'), ("p", ", "), ("str", '"Inglés C1"'), ("p", "],")],
    [("prop", "  disponibilidad"), ("p", ": "), ("str", '"inmediata"'), ("p", ","), ("com", "  // remoto, híbrido o presencial")],
    [("prop", "  datoCurioso"), ("p", ": "), ("str", '"barista de especialidad"'), ("p", ",")],
    [("p", "} "), ("kw", "as const"), ("p", ";")],
]

SECCIONES = [
    ("01", "Sobre mí", "// quién soy"),
    ("02", "Competencias", "// lo que sé hacer, con evidencia"),
    ("03", "Tecnologías", "// lo que más uso"),
    ("04", "Proyectos destacados", "// lo que mejor me representa"),
    ("05", "Trayectoria", "// cómo llegué hasta aquí"),
    ("06", "Formación y certificaciones", "// la base"),
    ("07", "Actividad", "// contribuciones del último año"),
]

COMPETENCIAS = [
    ("APIs REST y arquitectura en capas", "copper", "Router, controller, service, repository y DAO; DTO, factory de persistencia, paginación y manejo de errores.", "API de Eventos · E-commerce Backend · Turnos y Reservas"),
    ("Autenticación y autorización", "gold", "JWT en cookie HttpOnly, Passport, bcrypt, autorización por roles, propiedad de recursos y recuperación de contraseña.", "API de Eventos · E-commerce Backend · Adoptme API"),
    ("Bases de datos", "teal", "MongoDB y Mongoose: modelado, populate, consultas avanzadas, agregaciones y paginación. SQL y PostgreSQL.", "13 repositorios con MongoDB · Turnos y Reservas"),
    ("Calidad y testing", "sage", "Tests de integración con Supertest, Mocha y Chai sobre Mongo en memoria; ESLint, Prettier y CI.", "API de Eventos · Adoptme API · E-commerce Backend"),
    ("Frontend", "sky", "React 19 con Context y React Router, Vite, Tailwind CSS, Firebase; vistas server-side con Handlebars; Sass.", "CoffeeLink Store · Turnos y Reservas · Milodón"),
    ("Datos e IA con Python", "rose", "Python, Pandas y Django; prompt engineering, Gemini API, cadenas de prompts y evaluación LLM-as-judge.", "CafePrompt · Django Blog Playground"),
    ("DevOps y seguridad", "copper", "Docker y docker-compose, GitHub Actions, Swagger/OpenAPI, Helmet, rate limiting y hardening de Linux.", "Adoptme API · API de Eventos · Lab de hardening"),
    ("Metodologías ágiles", "gold", "Scrum, Lean y gestión ágil de proyectos; trabajo por entregas incrementales con control de versiones.", "17 cursos certificados en LinkedIn Learning"),
]

TECH_USO = [  # repositorios públicos donde aparece cada tecnología (noviembre 2026)
    ("Node.js", 20), ("Express", 17), ("HTML y CSS", 14), ("MongoDB y Mongoose", 13),
    ("Tests de integración", 10), ("JWT y bcrypt", 7), ("Socket.io", 5), ("Handlebars", 5),
    ("Passport", 4), ("Python", 4), ("Zod", 3), ("Supertest", 3),
]
ENFOQUE = ["Python", "Pandas", "SQL", "Pipelines de datos", "LLMs", "Prompt engineering"]
TAMBIEN = ["TypeScript", "NestJS", "Prisma", "Electron", "React", "Docker", "SQL", "PostgreSQL",
           "MySQL", "AWS", "Azure", "Power BI", "Excel", "Postman", "Jira", "Linux", "Git", "GitHub Actions"]

TRAYECTORIA = [
    ("2019", "Gestión ágil de proyectos", "LinkedIn Learning: Scrum, Lean, Six Sigma. Google Actívate: Marketing Digital", "gold"),
    ("2023", "Primeros pasos en programación", "Formación autodidacta y bootcamps", "faint"),
    ("2025", "Desarrollo Web", "Coderhouse: HTML, Sass, accesibilidad y SEO", "sky"),
    ("2026", "Carrera Fullstack", "Coderhouse: JavaScript, React, Python y Backend I a III", "copper"),
    ("2026", "IA y ciberseguridad", "Prompt engineering, Gemini, hardening de sistemas", "rose"),
    ("2026", "CoffeeLink", "Fundador: POS y plataforma para cafeterías", "teal"),
]

PROYECTOS = [
    dict(slug="entrega-5-backend-2-coderhouse", titulo="API de Eventos e Inscripciones",
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

ACADEMICA = [
    ("Ingeniería Informática", "Universidad de Playa Ancha · Valparaíso", "Estudios universitarios", "sky"),
    ("Carrera Desarrollo Full Stack", "Coderhouse", "Carrera completa", "copper"),
    ("Diplomado en Desarrollo Full Stack", "Coderhouse", "Diplomado", "gold"),
]
CERT_CODER = [("BE I", "Programación Backend I"), ("BE II", "Programación Backend II"), ("BE III", "Programación Backend III"),
              ("JS", "JavaScript"), ("React", "React JS"), ("Py", "Python"), ("Web", "Desarrollo Web"),
              ("Sec", "Ciberseguridad"), ("IA", "IA: Generación de Prompts")]
CERT_OTRAS = [
    ("LinkedIn Learning", "2019", "17 cursos con certificado: Scrum, Lean, Six Sigma Green Belt (fundamentos), gestión ágil de proyectos, Design Thinking y Microsoft Project.", "sky"),
    ("Google Actívate", "2019", "Fundamentos de Marketing Digital. Certificación avalada por IAB Europe y The Open University.", "sage"),
]
IDIOMAS = [("Español", "Nativo"), ("Inglés", "C1 · avanzado")]

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
    css = base_css(c, (("JBMono", 400), ("JBMono", 700)))
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
        b.append(f'<g><text x="40" y="{y}" text-anchor="end" class="mono" font-size="15" fill="{c["faint"]}" opacity="0.7">{i+1}</text>'
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



def competencias(c):
    W, cols, cw, ch, gx, gy = 1200, 2, 590, 150, 20, 16
    rows = (len(COMPETENCIAS) + 1) // 2
    H = rows * ch + (rows - 1) * gy + 2
    css = base_css(c, (("Inter", 400), ("Inter", 800), ("JBMono", 400), ("JBMono", 700)))
    b = []
    for i, (t, k, d, ev) in enumerate(COMPETENCIAS):
        r, q = divmod(i, cols)
        x, y = q * (cw + gx) + 0.5, r * (ch + gy) + 0.5
        a = c[k]
        b.append(f'<rect x="{x}" y="{y}" width="{cw-1}" height="{ch-1}" rx="14" fill="{c["surface"]}" stroke="{c["border"]}"/>'
                 f'<rect x="{x}" y="{y+22}" width="4" height="34" fill="{a}"/>'
                 f'<text x="{x+26}" y="{y+45}" class="sans" font-size="19" font-weight="800" fill="{c["text"]}">{esc(t)}</text>'
                 f'<text x="{x+cw-26}" y="{y+44}" text-anchor="end" class="mono" font-size="12" font-weight="700" fill="{a}">{i+1:02d}</text>')
        for j, line in enumerate(wrap(d, 14.5, cw - 52)[:2]):
            b.append(f'<text x="{x+26}" y="{y+76+j*21}" class="sans" font-size="14.5" fill="{c["muted"]}">{esc(line)}</text>')
        b.append(f'<text x="{x+26}" y="{y+ch-20}" class="mono" font-size="12" fill="{c["faint"]}"><tspan fill="{a}" font-weight="700">evidencia</tspan>  {esc(ev)}</text>')
    alt = "Competencias: " + "; ".join(f"{t}: {d}" for t, _, d, _ in COMPETENCIAS)
    return svg(W, H, "".join(b), css, alt)


def tech_chart(c):
    W, top, bh, gap = 1200, 70, 22, 12
    n = len(TECH_USO)
    H = top + n * (bh + gap) + 30
    lx, bx, bw = 24, 250, 410
    mx = max(v for _, v in TECH_USO)
    css = base_css(c, (("Inter", 400), ("Inter", 600), ("Inter", 800), ("JBMono", 400), ("JBMono", 700)))
    b = [f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="18" fill="{c["surface"]}" stroke="{c["border"]}"/>',
         f'<defs><linearGradient id="bar" x1="0" x2="1"><stop offset="0" stop-color="{c["copper"]}"/><stop offset="1" stop-color="{c["gold"]}"/></linearGradient></defs>',
         f'<text x="{lx}" y="40" class="sans" font-size="18" font-weight="800" fill="{c["text"]}">Más usadas</text>',
         f'<text x="{lx}" y="58" class="mono" font-size="12" fill="{c["faint"]}">repositorios públicos donde aparece cada una</text>']
    for i, (name, v) in enumerate(TECH_USO):
        y = top + 10 + i * (bh + gap)
        w = bw * v / mx
        b.append(f'<text x="{bx-14}" y="{y+bh*0.72:.1f}" text-anchor="end" class="sans" font-size="14.5" fill="{c["text"]}">{esc(name)}</text>'
                 f'<rect x="{bx}" y="{y}" width="{bw}" height="{bh}" rx="6" fill="{c["surface2"]}"/>'
                 f'<rect x="{bx}" y="{y}" width="{w:.1f}" height="{bh}" rx="6" fill="url(#bar)"/>'
                 f'<text x="{bx+w+10:.1f}" y="{y+bh*0.72:.1f}" class="mono" font-size="13" font-weight="700" fill="{c["muted"]}">{v}</text>')
    px0 = 760
    b.append(f'<path d="M{px0-40},28 V{H-28}" stroke="{c["border"]}" stroke-dasharray="3 5"/>'
             f'<text x="{px0}" y="40" class="sans" font-size="18" font-weight="800" fill="{c["text"]}">También trabajo con</text>'
             f'<text x="{px0}" y="58" class="mono" font-size="12" fill="{c["faint"]}">proyectos privados, CoffeeLink y formación</text>')
    x, y = px0, 84
    for t in TAMBIEN:
        tw = text_width(t, 13, "JBMono", 400) + 24
        if x + tw > W - 24:
            x, y = px0, y + 40
        s_, _ = pill(x, y, t, c["teal"], c, size=13, h=30, pad=12)
        b.append(s_)
        x += tw + 8
    y += 72
    b.append(f'<text x="{px0}" y="{y}" class="sans" font-size="18" font-weight="800" fill="{c["text"]}">Enfoque actual</text>'
             f'<text x="{px0}" y="{y+18}" class="mono" font-size="12" fill="{c["faint"]}">ingeniería de datos e IA con Python</text>')
    x, y = px0, y + 42
    for t in ENFOQUE:
        tw = text_width(t, 13, "JBMono", 400) + 24
        if x + tw > W - 24:
            x, y = px0, y + 40
        s_, _ = pill(x, y, t, c["rose"], c, size=13, h=30, pad=12)
        b.append(s_)
        x += tw + 8
    alt = "Tecnologías más usadas en repositorios públicos: " + ", ".join(f"{a} ({v})" for a, v in TECH_USO) + ". También: " + ", ".join(TAMBIEN) + ". Enfoque actual: " + ", ".join(ENFOQUE)
    return svg(W, H, "".join(b), css, alt)


def timeline(c):
    W, H = 1200, 238
    n = len(TRAYECTORIA)
    step = W / n
    ly = 92
    css = base_css(c, (("Inter", 400), ("Inter", 800), ("JBMono", 400), ("JBMono", 700)))
    b = [f'<path d="M{step/2},{ly} H{W-step/2}" stroke="{c["border"]}" stroke-width="2"/>']
    for i, (yr, t, d, k) in enumerate(TRAYECTORIA):
        cx = step * i + step / 2
        a = c[k]
        last = i == n - 1
        b.append(f'<g><text x="{cx}" y="{ly-30}" text-anchor="middle" class="mono" font-size="15" font-weight="700" fill="{a}">{yr}</text>'
                 f'<circle cx="{cx}" cy="{ly}" r="9" fill="{c["bg"]}" stroke="{a}" stroke-width="3"/>'
                 + (f'<circle cx="{cx}" cy="{ly}" r="4" fill="{a}"/>' if last else '')
                 + "".join(f'<text x="{cx}" y="{ly+40+j*21}" text-anchor="middle" class="sans" font-size="15.5" font-weight="800" fill="{c["text"]}">{esc(line)}</text>' for j, line in enumerate(wrap(t, 15.5, step - 20, "Inter", 800)[:2])))
        tl = len(wrap(t, 15.5, step - 20, "Inter", 800)[:2])
        for j, line in enumerate(wrap(d, 13, step - 22)[:4]):
            b.append(f'<text x="{cx}" y="{ly+46+tl*21+j*19}" text-anchor="middle" class="sans" font-size="13" fill="{c["muted"]}">{esc(line)}</text>')
        b.append('</g>')
    alt = "Trayectoria: " + "; ".join(f"{y} {t}: {d}" for y, t, d, _ in TRAYECTORIA)
    return svg(W, H, "".join(b), css, alt)


def formacion(c):
    W = 1200
    css = base_css(c, (("Inter", 400), ("Inter", 600), ("Inter", 800), ("JBMono", 400), ("JBMono", 700)))
    b = []
    # Formación académica
    b.append(f'<text x="0" y="22" class="mono" font-size="13" font-weight="700" fill="{c["copper"]}" letter-spacing="1">FORMACIÓN</text>')
    cw, y0 = 388, 40
    for i, (t, inst, tipo, k) in enumerate(ACADEMICA):
        x = i * (cw + 18) + 0.5
        a = c[k]
        b.append(f'<rect x="{x}" y="{y0}" width="{cw}" height="112" rx="14" fill="{c["surface"]}" stroke="{c["border"]}"/>'
                 f'<rect x="{x}" y="{y0+20}" width="4" height="30" fill="{a}"/>'
                 f'<text x="{x+24}" y="{y0+34}" class="mono" font-size="11.5" font-weight="700" fill="{a}" letter-spacing="0.8">{esc(tipo.upper())}</text>'
                 f'<text x="{x+24}" y="{y0+62}" class="sans" font-size="18" font-weight="800" fill="{c["text"]}">{esc(t)}</text>'
                 f'<text x="{x+24}" y="{y0+88}" class="sans" font-size="14" fill="{c["muted"]}">{esc(inst)}</text>')
    # Certificaciones Coderhouse
    y1 = y0 + 150
    b.append(f'<text x="0" y="{y1}" class="mono" font-size="13" font-weight="700" fill="{c["copper"]}" letter-spacing="1">CERTIFICACIONES CODERHOUSE</text>')
    n = len(CERT_CODER)
    bwid = W / n
    ring = [c["copper"], c["gold"], c["teal"], c["sky"], c["sage"], c["rose"]]
    for i, (ab, name) in enumerate(CERT_CODER):
        cx, cy = bwid * i + bwid / 2, y1 + 72
        a = ring[i % len(ring)]
        pts = " ".join(f"{cx + 40*__import__('math').cos(__import__('math').radians(60*k-90)):.1f},{cy + 40*__import__('math').sin(__import__('math').radians(60*k-90)):.1f}" for k in range(6))
        pts2 = " ".join(f"{cx + 33*__import__('math').cos(__import__('math').radians(60*k-90)):.1f},{cy + 33*__import__('math').sin(__import__('math').radians(60*k-90)):.1f}" for k in range(6))
        b.append(f'<polygon points="{pts}" fill="{a}" fill-opacity="0.12" stroke="{a}" stroke-width="2"/>'
                 f'<polygon points="{pts2}" fill="none" stroke="{a}" stroke-opacity="0.45" stroke-width="1"/>'
                 f'<text x="{cx}" y="{cy+6}" text-anchor="middle" class="mono" font-size="{16 if len(ab)<=3 else (14 if len(ab)<=5 else 12.5)}" font-weight="700" fill="{a}">{esc(ab)}</text>')
        for j, line in enumerate(wrap(name, 12.5, bwid - 8, "Inter", 600)[:2]):
            b.append(f'<text x="{cx}" y="{cy+64+j*17}" text-anchor="middle" class="sans" font-size="12.5" font-weight="600" fill="{c["muted"]}">{esc(line)}</text>')
    # Otras certificaciones + idiomas
    y2 = y1 + 206
    b.append(f'<text x="0" y="{y2}" class="mono" font-size="13" font-weight="700" fill="{c["copper"]}" letter-spacing="1">OTRAS CERTIFICACIONES</text>'
             f'<text x="{W-286}" y="{y2}" class="mono" font-size="13" font-weight="700" fill="{c["copper"]}" letter-spacing="1">IDIOMAS</text>')
    cw2 = 437
    for i, (org, yr, d, k) in enumerate(CERT_OTRAS):
        x = i * (cw2 + 18) + 0.5
        a = c[k]
        yy = y2 + 18
        b.append(f'<rect x="{x}" y="{yy}" width="{cw2}" height="124" rx="14" fill="{c["surface"]}" stroke="{c["border"]}"/>'
                 f'<text x="{x+22}" y="{yy+34}" class="sans" font-size="17" font-weight="800" fill="{c["text"]}">{esc(org)}</text>'
                 f'<text x="{x+cw2-22}" y="{yy+33}" text-anchor="end" class="mono" font-size="13" font-weight="700" fill="{a}">{yr}</text>')
        for j, line in enumerate(wrap(d, 13.5, cw2 - 44)[:3]):
            b.append(f'<text x="{x+22}" y="{yy+62+j*20}" class="sans" font-size="13.5" fill="{c["muted"]}">{esc(line)}</text>')
    xi, yy = W - 286 + 0.5, y2 + 18
    b.append(f'<rect x="{xi}" y="{yy}" width="285" height="124" rx="14" fill="{c["surface"]}" stroke="{c["border"]}"/>')
    for j, (lang, lvl) in enumerate(IDIOMAS):
        ly = yy + 42 + j * 46
        b.append(f'<text x="{xi+22}" y="{ly}" class="sans" font-size="16" font-weight="800" fill="{c["text"]}">{esc(lang)}</text>'
                 f'<text x="{xi+263}" y="{ly}" text-anchor="end" class="mono" font-size="13" font-weight="700" fill="{c["teal"]}">{esc(lvl)}</text>')
        dots = 6 if j == 0 else 5
        for d in range(6):
            b.append(f'<rect x="{xi+22+d*40}" y="{ly+12}" width="34" height="5" rx="2.5" fill="{c["teal"] if d < dots else c["surface2"]}"/>')
    H = yy + 126
    alt = ("Formación: " + "; ".join(f"{t}, {i}" for t, i, _, _ in ACADEMICA) + ". Certificaciones Coderhouse: " + ", ".join(n for _, n in CERT_CODER)
           + ". Otras: " + "; ".join(f"{o} {y}: {d}" for o, y, d, _ in CERT_OTRAS) + ". Idiomas: español nativo, inglés C1.")
    return svg(W, int(H), "".join(b), css, alt)


BANNERS = {
    "adoptme-api": dict(titulo="Adoptme API", categoria="BACKEND · CALIDAD", acento="teal",
                         bajada="API de adopciones con mocks, Swagger, tests funcionales y Docker",
                         tags=["Node.js", "Express", "MongoDB", "Swagger", "Mocha", "Docker"]),
    "ecommerce-backend-node": dict(titulo="E-commerce Backend", categoria="BACKEND · ARQUITECTURA", acento="gold",
                         bajada="Arquitectura en capas DAO, Repository y DTO con Passport, roles y tickets",
                         tags=["Node.js", "Express", "MongoDB", "Passport", "JWT", "Nodemailer"]),
    "CafePrompt": dict(titulo="CafePrompt", categoria="IA GENERATIVA · PYTHON", acento="rose",
                         bajada="De la ficha técnica de un café a un kit de contenido con IA generativa",
                         tags=["Python", "Gemini", "Prompt engineering", "Gradio", "Colab"]),
    "coffeelink-store-react": dict(titulo="CoffeeLink Store", categoria="FRONTEND · E-COMMERCE", acento="sage",
                         bajada="SPA de café de especialidad con catálogo, carrito y checkout en Firestore",
                         tags=["React 19", "Vite", "Tailwind CSS", "Firebase", "React Router"]),
}


def banner(c, d):
    W, H = 1280, 300
    a = c[d["acento"]]
    css = base_css(c, (("Inter", 400), ("Inter", 800), ("JBMono", 400), ("JBMono", 700))) + (
        "@keyframes rise{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}.r{animation:rise .7s ease-out both}")
    b = [f'<defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{c["bg"]}"/><stop offset="1" stop-color="{c["bg2"]}"/></linearGradient>'
         f'<radialGradient id="gl" cx="0.88" cy="0.5" r="0.5"><stop offset="0" stop-color="{a}" stop-opacity="0.2"/><stop offset="1" stop-color="{a}" stop-opacity="0"/></radialGradient>'
         f'<clipPath id="cl"><rect width="{W}" height="{H}" rx="22"/></clipPath></defs>',
         f'<g clip-path="url(#cl)"><rect width="{W}" height="{H}" fill="url(#bg)"/>', dot_grid(W, H, c),
         f'<rect width="{W}" height="{H}" fill="url(#gl)"/><rect width="{W}" height="5" fill="{a}"/></g>',
         f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="21.5" fill="none" stroke="{c["border"]}"/>',
         f'<g class="r"><text x="60" y="76" class="mono" font-size="14" font-weight="700" fill="{a}" letter-spacing="1.4">{esc(d["categoria"])}</text>'
         f'<text x="60" y="140" class="sans" font-size="54" font-weight="800" fill="{c["text"]}" letter-spacing="-1">{esc(d["titulo"])}</text>'
         f'<text x="60" y="182" class="sans" font-size="20" fill="{c["muted"]}">{esc(d["bajada"])}</text>']
    x = 60
    for t in d["tags"]:
        s_, wdt = pill(x, 214, t, a, c, size=14, h=32, pad=13)
        b.append(s_)
        x += wdt + 10
    b.append('</g>')
    b.append(f'<g transform="translate(1110,150)" fill="none" stroke="{a}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" opacity="0.9">'
             f'<path d="M-62,-30 L-92,0 L-62,30"/><path d="M62,-30 L92,0 L62,30"/><path d="M20,-52 L-20,52"/></g>'
             f'<text x="{W-60}" y="{H-30}" text-anchor="end" class="mono" font-size="13" fill="{c["faint"]}">github.com/sebakine</text>')
    return svg(W, H, "".join(b), css, f'{d["titulo"]}: {d["bajada"]}')


# =============================================================================
def main():
    for d in ("projects", "sections", "banners"):
        (OUT / d).mkdir(parents=True, exist_ok=True)
    for f in OUT.rglob("*.svg"):
        f.unlink()
    for name, c in THEMES.items():
        (OUT / f"header-{name}.svg").write_text(header(c), encoding="utf-8")
        (OUT / f"about-{name}.svg").write_text(about(c), encoding="utf-8")
        (OUT / f"skills-{name}.svg").write_text(competencias(c), encoding="utf-8")
        (OUT / f"tech-{name}.svg").write_text(tech_chart(c), encoding="utf-8")
        (OUT / f"coffeelink-{name}.svg").write_text(coffeelink_card(c), encoding="utf-8")
        (OUT / f"timeline-{name}.svg").write_text(timeline(c), encoding="utf-8")
        (OUT / f"education-{name}.svg").write_text(formacion(c), encoding="utf-8")
        (OUT / f"footer-{name}.svg").write_text(footer(c), encoding="utf-8")
        for num, title, comment in SECCIONES:
            (OUT / "sections" / f"{num}-{name}.svg").write_text(section(c, num, title, comment), encoding="utf-8")
        for p in PROYECTOS:
            (OUT / "projects" / f"{p['slug'].lower()}-{name}.svg").write_text(project_card(c, p), encoding="utf-8")
        for slug, d in BANNERS.items():
            (OUT / "banners" / f"{slug.lower()}-{name}.svg").write_text(banner(c, d), encoding="utf-8")
    print("SVG generados en", OUT)


if __name__ == "__main__":
    main()
