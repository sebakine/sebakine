#!/usr/bin/env python3
"""Genera los SVG del perfil (tema claro y oscuro) en ../assets.

Uso:  python3 scripts/build.py
Requiere: fonttools, brotli y Pillow (pip install fonttools brotli pillow)

Todo el contenido editable (textos, proyectos, stack, formación) está en DATOS.
Las fuentes Inter y JetBrains Mono (licencia OFL) se incrustan en cada SVG para que
el perfil se vea igual en cualquier sistema. Los logos vienen de Simple Icons (CC0).
Los gráficos se dibujan a 880 px de ancho: GitHub muestra el README a ~846 px, así
que el texto se ve prácticamente a su tamaño real.
"""
from __future__ import annotations

import base64
import html
import json
import math
import os
from pathlib import Path

from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent.parent
HERE = Path(__file__).resolve().parent
FONTS = HERE / "fonts"
SHOTS = HERE / "shots"
OUT = ROOT / "assets"
ICONS = json.loads((HERE / "icons.json").read_text(encoding="utf-8"))

W = 880          # ancho de los gráficos de ancho completo
CARD_W = 432     # tarjetas a dos columnas (2 × 432 + 16 = 880)
GAP = 16

# =============================================================================
# PALETA — "Espresso & Code"
# =============================================================================
THEMES = {
    "dark": dict(
        bg="#15100D", bg2="#1F1713", surface="#1C1512", surface2="#241B16",
        border="#3A2B23", text="#F4EADF", muted="#B4A293", faint="#9C8878",
        copper="#E3894C", gold="#D8B07A", teal="#62B6A4", rose="#DB7F7A",
        sky="#86A9D6", sage="#A3C27F", grid="#2C211B", crema="#C89A6A",
    ),
    "light": dict(
        bg="#FBF6F0", bg2="#F3EADF", surface="#FFFFFF", surface2="#FAF4EC",
        border="#E6D7C6", text="#2A1D16", muted="#6E5C50", faint="#7A6858",
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
    bajada="Construyo APIs y aplicaciones web con arquitectura en capas, autenticación robusta y pruebas. "
           "Enfoco mi crecimiento en ingeniería de datos e IA con Python. Fundador de CoffeeLink.",
    chips=[("Chile", "faint"), ("Inglés C1", "gold"), ("Remoto · híbrido · presencial", "faint"), ("Disponibilidad inmediata", "teal")],
)

ABOUT_CODE = [
    [("kw", "const "), ("var", "sebastian"), ("p", " = {")],
    [("prop", "  rol"), ("p", ": "), ("str", '"Fullstack Developer"'), ("p", ",")],
    [("prop", "  stack"), ("p", ": ["), ("str", '"Node.js"'), ("p", ", "), ("str", '"Express"'), ("p", ", "), ("str", '"MongoDB"'), ("p", ", "), ("str", '"React"'), ("p", ", "), ("str", '"Python"'), ("p", "],")],
    [("prop", "  enfoque"), ("p", ": ["), ("str", '"Ingeniería de datos"'), ("p", ", "), ("str", '"AI Engineering"'), ("p", "],")],
    [("prop", "  construyendo"), ("p", ": "), ("str", '"CoffeeLink"'), ("p", ","), ("com", "  // POS + plataforma para cafeterías")],
    [("prop", "  practicas"), ("p", ": ["), ("str", '"capas"'), ("p", ", "), ("str", '"testing"'), ("p", ", "), ("str", '"CI/CD"'), ("p", ", "), ("str", '"seguridad"'), ("p", "],")],
    [("prop", "  idiomas"), ("p", ": ["), ("str", '"Español nativo"'), ("p", ", "), ("str", '"Inglés C1"'), ("p", "],")],
    [("prop", "  disponibilidad"), ("p", ": "), ("str", '"inmediata"'), ("p", ","), ("com", "  // remoto, híbrido o presencial")],
    [("prop", "  datoCurioso"), ("p", ": "), ("str", '"barista de especialidad"'), ("p", ",")],
    [("p", "} "), ("kw", "as const"), ("p", ";")],
]

AHORA = [
    ("CONSTRUYENDO", "copper", "CoffeeLink: POS de escritorio y Platform Web en desarrollo."),
    ("APRENDIENDO", "teal", "Airflow, dbt e ingeniería de datos con Python."),
    ("DISPONIBLE", "gold", "Inmediatamente, en modalidad remota, híbrida o presencial."),
]

SECCIONES = [
    ("01", "Sobre mí", "// quién soy"),
    ("02", "Stack y competencias", "// lo que uso y lo que sé hacer"),
    ("03", "Proyectos destacados", "// lo que mejor me representa"),
    ("04", "Trayectoria y formación", "// cómo llegué hasta aquí"),
    ("05", "Actividad", "// contribuciones del último año"),
]

TECH_USO = [  # repositorios públicos donde aparece cada tecnología (noviembre 2026)
    ("Node.js", 19), ("Express", 17), ("MongoDB y Mongoose", 13), ("HTML y CSS", 12),
    ("Tests de integración", 10), ("Python", 8), ("JWT", 7), ("GitHub Actions", 5),
    ("Socket.io", 5), ("Handlebars", 5), ("pytest", 4), ("Docker", 3),
]

STACK = [
    ("LENGUAJES", "copper", ["JavaScript", "TypeScript", "Python", "SQL", "HTML5", "CSS3", "Sass", "Bash", "Handlebars"]),
    ("BACKEND", "gold", ["Node.js", "Express", "NestJS", "Prisma", "Mongoose", "Passport", "JWT", "bcrypt", "Zod", "Socket.io",
                         "Nodemailer", "Helmet", "Swagger", "Multer"]),
    ("FRONTEND", "sky", ["React", "React Router", "Vite", "Tailwind CSS", "Bootstrap", "Firebase", "Electron"]),
    ("PYTHON Y DATOS", "rose", ["pandas", "Pydantic", "httpx", "Tenacity", "Beautiful Soup", "Playwright", "Typer", "Rich", "Jinja",
                                "Matplotlib", "Altair", "Streamlit", "Django", "Gradio", "Gemini", "gTTS"]),
    ("ORQUESTACIÓN Y BASES DE DATOS", "teal", ["Apache Airflow", "dbt", "Cosmos", "PostgreSQL", "MongoDB", "MySQL", "SQLite"]),
    ("TESTING Y CALIDAD", "sage", ["Jest", "Mocha", "Chai", "Supertest", "pytest", "Hypothesis", "Ruff", "mypy", "ESLint",
                                   "Prettier", "pre-commit"]),
    ("DEVOPS Y NUBE", "copper", ["Docker", "GitHub Actions", "GitHub Pages", "uv", "Git", "Linux", "AWS", "Azure", "Postman"]),
]

COMPETENCIAS = [
    ("APIs REST y arquitectura en capas", "copper", "Router, controller, service, repository y DAO; DTO, factory de persistencia, paginación y manejo de errores.", "API de Eventos · E-commerce Backend · Turnos"),
    ("Autenticación y autorización", "gold", "JWT en cookie HttpOnly, Passport, bcrypt, autorización por roles, propiedad de recursos y recuperación de contraseña.", "API de Eventos · E-commerce Backend · Adoptme"),
    ("Ingeniería de datos", "teal", "Pipelines ETL con Python y PostgreSQL, modelo estrella, dbt (staging, marts, snapshots) y orquestación con Airflow.", "ETL Datos Chile · Airflow y dbt · Limpiador"),
    ("Bases de datos", "sky", "MongoDB y Mongoose: modelado, populate, agregaciones y paginación. PostgreSQL y SQLite en proyectos de datos.", "Turnos y Reservas · ETL Datos Chile"),
    ("Calidad y testing", "sage", "Supertest, Mocha y Chai sobre Mongo en memoria; pytest, Hypothesis, Ruff y mypy; integración continua.", "API de Eventos · Adoptme · Limpiador"),
    ("IA generativa", "rose", "Prompt engineering, cadenas de prompts con Gemini, evaluación LLM-as-judge e interfaces con Gradio.", "CafePrompt"),
    ("Frontend", "sky", "React 19 con Context y React Router, Vite, Tailwind CSS y Firebase; vistas server-side con Handlebars; Sass.", "CoffeeLink Store · Milodón · Turnos"),
    ("DevOps y seguridad", "copper", "Docker y docker-compose, GitHub Actions, Swagger/OpenAPI, Helmet, rate limiting y hardening de Linux.", "Adoptme · API de Eventos · Lab de hardening"),
]

COFFEELINK = dict(
    titulo="CoffeeLink",
    categoria="PROYECTO PRINCIPAL · EN DESARROLLO",
    desc="Infraestructura financiera y capa de datos para cafeterías y tostadurías de especialidad en Latinoamérica: un POS de escritorio para la operación diaria y una plataforma web con paneles por rol y servicios analíticos en Python.",
    modulos=[("POS", "Electron · React · NestJS · Prisma"), ("Platform Web", "React · Vite · Tailwind · NestJS"), ("Datos", "Servicios analíticos en Python")],
    tags=["TypeScript", "Nx monorepo", "NestJS", "Prisma", "Electron", "Stripe"],
    nota="Código privado",
)

PROYECTOS = [
    dict(slug="etl-datos-chile", titulo="ETL Datos Chile", categoria="DATOS · ETL", acento="teal",
         desc="Pipeline ETL de sismos (USGS) e indicadores económicos (mindicador.cl) hacia un modelo estrella en PostgreSQL, con dashboard en Streamlit.",
         tags=["Python", "PostgreSQL", "Streamlit", "Docker", "GitHub Actions"], nota="Proyecto personal", shot="etl-datos-chile.jpg"),
    dict(slug="orquestacion-airflow-dbt", titulo="Orquestación Airflow + dbt", categoria="DATOS · ORQUESTACIÓN", acento="sky",
         desc="DAGs de Airflow 3 con scheduling por assets y Cosmos; proyecto dbt con staging, intermedia, marts y snapshots, documentado en GitHub Pages.",
         tags=["Airflow", "dbt", "Cosmos", "PostgreSQL", "Docker"], nota="Proyecto personal", shot="orquestacion-airflow-dbt.jpg"),
    dict(slug="CafePrompt", titulo="CafePrompt", categoria="IA GENERATIVA · PYTHON", acento="rose",
         desc="Convierte la ficha técnica de un lote de café en un kit de contenido (texto, imagen y audio) con una cadena de prompts y evaluación LLM-as-judge.",
         tags=["Python", "Gemini", "Gradio", "Colab", "gTTS"], nota="IA: Generación de Prompts · Coderhouse", shot="cafeprompt.jpg"),
    dict(slug="entrega-5-backend-2-coderhouse", titulo="API de Eventos e Inscripciones", categoria="BACKEND · SEGURIDAD", acento="copper",
         desc="JWT en cookie HttpOnly y autorización por roles (user, organizer, admin) con propiedad de recursos. Zod, Helmet, rate limiting, tests y CI.",
         tags=["Node.js", "Express", "MongoDB", "Zod", "GitHub Actions"], nota="Programación Backend II · Coderhouse",
         api=[("POST", "/api/sessions/login", "rate limit"), ("GET", "/api/sessions/current", "JWT cookie"),
              ("GET", "/api/events", "público"), ("POST", "/api/events", "organizer"),
              ("PATCH", "/api/events/:eid", "dueño o admin"), ("GET", "/api/users", "admin")]),
    dict(slug="adoptme-api", titulo="Adoptme API", categoria="BACKEND · CALIDAD", acento="gold",
         desc="API de adopciones con datos de prueba (Faker), documentación Swagger, pruebas funcionales con Mocha, Chai y Supertest, y contenedor Docker.",
         tags=["Node.js", "Swagger", "Mocha", "Supertest", "Docker"], nota="Programación Backend III · Coderhouse",
         api=[("GET", "/api/docs", "Swagger UI"), ("GET", "/api/pets", "mascotas"),
              ("POST", "/api/adoptions/:uid/:pid", "adopción"), ("GET", "/api/mocks/mockingpets", "Faker"),
              ("POST", "/api/mocks/generateData", "semilla"), ("PUT", "/api/users/:uid", "usuarios")]),
    dict(slug="coffeelink-store-react", titulo="CoffeeLink Store", categoria="FRONTEND · E-COMMERCE", acento="sage",
         desc="SPA de café de especialidad: catálogo desde Firestore, carrito global con Context y checkout que descuenta stock en un lote atómico.",
         tags=["React 19", "Vite", "Tailwind CSS", "Firebase"], nota="React JS · Coderhouse",
         store=[("Etiopía Yirgacheffe", "$9.800"), ("Colombia Huila", "$8.900"), ("Brasil Cerrado", "$8.200")]),
]

TRAYECTORIA = [
    ("2019", "Gestión ágil de proyectos", "Scrum, Lean y Six Sigma en LinkedIn Learning", "gold"),
    ("2023", "Primeros pasos en programación", "Formación autodidacta y bootcamps", "faint"),
    ("2025", "Desarrollo Web", "HTML, Sass, accesibilidad y SEO", "sky"),
    ("2026", "Carrera Fullstack", "JavaScript, React, Python y Backend I a III", "copper"),
    ("2026", "Datos e IA", "ETL, Airflow, dbt y prompt engineering", "rose"),
    ("2026", "CoffeeLink", "Fundador: POS y plataforma para cafeterías", "teal"),
]

ACADEMICA = [
    ("Ingeniería Informática", "Universidad de Playa Ancha · Valparaíso", "Estudios universitarios", "sky"),
    ("Carrera Desarrollo Full Stack", "Coderhouse", "Carrera completa", "copper"),
    ("Diplomado en Desarrollo Full Stack", "Coderhouse", "Diplomado", "gold"),
]
CERT_CODER = [("BE I", "Programación Backend I"), ("BE II", "Programación Backend II"), ("BE III", "Programación Backend III"),
              ("JS", "JavaScript"), ("React", "React JS"), ("Py", "Python"), ("Web", "Desarrollo Web"),
              ("Sec", "Ciberseguridad"), ("IA", "IA: Generación de Prompts")]
CERT_OTRAS = [
    ("LinkedIn Learning", "2019", "17 cursos con certificado: Scrum, Lean, Six Sigma Green Belt (fundamentos), gestión ágil, Design Thinking y Microsoft Project.", "sky"),
    ("Google Actívate", "2019", "Fundamentos de Marketing Digital, avalado por IAB Europe y The Open University.", "sage"),
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
MISSING: set = set()


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
        if g in hmtx:
            total += hmtx[g][0]
        else:
            MISSING.add(ch)
            total += upm * 0.55
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
ALL_FONTS = (("Inter", 400), ("Inter", 600), ("Inter", 800), ("JBMono", 400), ("JBMono", 700))


def svg(w, h, body, css, title):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{esc(title)}">'
            f"<title>{esc(title)}</title><style>{css}</style>{body}</svg>")


def base_css(c, fonts=ALL_FONTS):
    return font_css(*fonts) + (
        f".sans{{font-family:{SANS}}}.mono{{font-family:{MONO}}}"
        "@media (prefers-reduced-motion: reduce){*{animation:none!important}}"
        + ("*{animation:none!important}" if os.environ.get("PREVIEW") else "")
    )


def pill(x, y, label, color, c, size=13.5, fam="JBMono", pad=11, h=28, fill_op=0.12):
    f, wt = ("JBMono", 400) if fam == "JBMono" else ("Inter", 600)
    width = text_width(label, size, f, wt) + pad * 2
    cls = "mono" if fam == "JBMono" else "sans"
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{width:.1f}" height="{h}" rx="{h/2}" fill="{color}" fill-opacity="{fill_op}" stroke="{color}" stroke-opacity="0.35"/>'
            f'<text x="{x+pad:.1f}" y="{y+h/2+size*0.36:.1f}" class="{cls}" font-size="{size}" font-weight="{wt}" fill="{color}">{esc(label)}</text>'), width


def pills_flow(x0, y0, max_x, items, color, c, size=13.5, h=28, gap=8, row_gap=8, max_rows=99):
    """Dibuja pills en filas; devuelve (svg, y_final)."""
    out, x, y, rows = [], x0, y0, 1
    for t in items:
        s, wdt = pill(x, y, t, color, c, size=size, h=h)
        if x + wdt > max_x and x > x0:
            rows += 1
            if rows > max_rows:
                break
            x, y = x0, y + h + row_gap
            s, wdt = pill(x, y, t, color, c, size=size, h=h)
        out.append(s)
        x += wdt + gap
    return "".join(out), y + h


def dot_grid(w, h, c, step=24, r=1.1, op=0.9, pid="g"):
    return (f'<defs><pattern id="{pid}" width="{step}" height="{step}" patternUnits="userSpaceOnUse">'
            f'<circle cx="2" cy="2" r="{r}" fill="{c["grid"]}" opacity="{op}"/></pattern></defs>'
            f'<rect width="{w}" height="{h}" fill="url(#{pid})"/>')


def card_bg(x, y, w, h, c, rx=14, fill=None):
    return f'<rect x="{x+0.5:.1f}" y="{y+0.5:.1f}" width="{w-1:.1f}" height="{h-1:.1f}" rx="{rx}" fill="{fill or c["surface"]}" stroke="{c["border"]}"/>'


def _lum(hexcol):
    h = hexcol.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    f = lambda v: v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def contrast(a, b):
    la, lb = sorted((_lum(a), _lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def logo(name, x, y, size, c):
    """Logo de Simple Icons escalado a `size`; devuelve '' si no existe."""
    ic = ICONS.get(name)
    if not ic:
        return ""
    col = "#" + ic["hex"]
    if contrast(col, c["surface"]) < 3.0:
        col = c["text"]
    s = size / 24
    return f'<path transform="translate({x:.1f},{y:.1f}) scale({s:.4f})" d="{ic["path"]}" fill="{col}"/>'


def shot_data(name):
    return "data:image/jpeg;base64," + base64.b64encode((SHOTS / name).read_bytes()).decode()


# =============================================================================
# COMPONENTES
# =============================================================================
def header(c):
    H = 330
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
        f'<radialGradient id="glow" cx="0.85" cy="0.45" r="0.45"><stop offset="0" stop-color="{c["copper"]}" stop-opacity="0.18"/><stop offset="1" stop-color="{c["copper"]}" stop-opacity="0"/></radialGradient>'
        f'<clipPath id="clip"><rect width="{W}" height="{H}" rx="22"/></clipPath></defs>',
        f'<g clip-path="url(#clip)"><rect width="{W}" height="{H}" fill="url(#bgg)"/>',
        dot_grid(W, H, c),
        f'<rect width="{W}" height="{H}" fill="url(#glow)"/>',
        f'<rect x="0" y="0" width="{W}" height="5" fill="{c["copper"]}"/></g>',
        f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="21.5" fill="none" stroke="{c["border"]}"/>',
    ]
    x = 44
    pw = text_width(PERFIL["prompt"], 14.5, "JBMono", 400)
    b.append(f'<g class="r1"><text x="{x}" y="58" class="mono" font-size="14.5" fill="{c["muted"]}"><tspan fill="{c["teal"]}">~/sebakine</tspan> <tspan fill="{c["copper"]}">$</tspan> whoami</text>'
             f'<rect class="cur" x="{x+pw+7:.1f}" y="45" width="9" height="16" fill="{c["copper"]}"/></g>')
    b.append(f'<text class="sans r2" x="{x}" y="112" font-size="42" font-weight="800" fill="{c["text"]}" letter-spacing="-0.9">{esc(PERFIL["nombre"])}</text>')
    b.append(f'<text class="sans r3" x="{x}" y="146" font-size="18.5" font-weight="600" fill="{c["gold"]}">{esc(PERFIL["titular"])}</text>')
    lines = wrap(PERFIL["bajada"], 15, 570)
    b.append('<g class="r3">' + "".join(f'<text class="sans" x="{x}" y="{182 + i*23}" font-size="15" fill="{c["muted"]}">{esc(l)}</text>' for i, l in enumerate(lines)) + "</g>")
    cy = 182 + len(lines) * 23 + 14
    cx, parts = x, []
    for label, col in PERFIL["chips"]:
        color = c[col]
        if col == "teal":
            wdt = text_width(label, 13.5, "Inter", 600) + 40
            parts.append(f'<rect x="{cx}" y="{cy}" width="{wdt:.1f}" height="30" rx="15" fill="{color}" fill-opacity="0.12" stroke="{color}" stroke-opacity="0.4"/>'
                         f'<circle cx="{cx+15}" cy="{cy+15}" r="4" fill="{color}"/><circle class="pl" cx="{cx+15}" cy="{cy+15}" r="4" fill="none" stroke="{color}" stroke-width="1.5"/>'
                         f'<text x="{cx+27}" y="{cy+19.8}" class="sans" font-size="13.5" font-weight="600" fill="{color}">{esc(label)}</text>')
        else:
            p, wdt = pill(cx, cy, label, color, c, size=13.5, fam="Inter", h=30, pad=14)
            parts.append(p)
        cx += wdt + 8
    b.append(f'<g class="r4">{"".join(parts)}</g>')

    # Ilustración original: taza con arte latte en forma de </>
    cu, cr, cg = c["copper"], c["crema"], c["gold"]
    b.append(f'<g transform="translate(752,176) scale(0.66)">'
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
             f'<text x="-170" y="-108" class="mono" font-size="20" fill="{c["faint"]}">{{ }}</text>'
             f'<text x="118" y="-118" class="mono" font-size="20" fill="{c["faint"]}">=&gt;</text>'
             f'<text x="104" y="-62" class="mono" font-size="18" fill="{c["faint"]}">200 OK</text>'
             "</g>")
    return svg(W, H, "".join(b), css, f"{PERFIL['nombre']} — {PERFIL['titular']}")


def section(c, num, title, comment):
    H = 60
    tw = text_width(title, 24, "Inter", 800)
    nw = text_width(num, 15, "JBMono", 700)
    x2 = nw + 14 + tw + 20
    cw = text_width(comment, 13.5, "JBMono", 400)
    body = (f'<text x="0" y="39" class="mono" font-size="15" font-weight="700" fill="{c["copper"]}">{num}</text>'
            f'<text x="{nw+14:.1f}" y="41" class="sans" font-size="24" font-weight="800" fill="{c["text"]}" letter-spacing="-0.3">{esc(title)}</text>'
            f'<defs><linearGradient id="ln" x1="0" x2="1"><stop offset="0" stop-color="{c["copper"]}" stop-opacity="0.8"/><stop offset="1" stop-color="{c["border"]}" stop-opacity="0.4"/></linearGradient></defs>'
            f'<rect x="{x2:.1f}" y="33" width="{max(30, W - x2 - cw - 20):.1f}" height="2" rx="1" fill="url(#ln)"/>'
            f'<text x="{W}" y="38" text-anchor="end" class="mono" font-size="13.5" fill="{c["faint"]}">{esc(comment)}</text>')
    return svg(W, H, body, base_css(c, (("Inter", 800), ("JBMono", 400), ("JBMono", 700))), f"{num} {title}")


def about(c):
    lh, top = 28, 78
    H = top + lh * (len(ABOUT_CODE) - 1) + 30
    col = dict(kw=c["copper"], var=c["gold"], prop=c["text"], str=c["teal"], p=c["muted"], com=c["faint"])
    css = base_css(c, (("JBMono", 400), ("JBMono", 700)))
    b = [card_bg(0, 0, W, H, c, rx=16),
         f'<path d="M16.5,0.5 H{W-16.5} A16,16 0 0 1 {W-0.5},16.5 V44 H0.5 V16.5 A16,16 0 0 1 16.5,0.5 Z" fill="{c["surface2"]}"/>',
         f'<path d="M0.5,44 H{W-0.5}" stroke="{c["border"]}"/>']
    for i, k in enumerate(["copper", "gold", "teal"]):
        b.append(f'<circle cx="{24+i*20}" cy="22" r="6" fill="{c[k]}"/>')
    b.append(f'<rect x="96" y="9" width="128" height="35" rx="7" fill="{c["surface"]}"/><text x="112" y="31" class="mono" font-size="13.5" fill="{c["text"]}">sebastian.ts</text>'
             f'<text x="{W-20}" y="28" text-anchor="end" class="mono" font-size="13" fill="{c["faint"]}">TypeScript · UTF-8</text>')
    for i, line in enumerate(ABOUT_CODE):
        y = top + i * lh
        spans = "".join(f'<tspan fill="{col[k]}"{" font-style=\"italic\"" if k=="com" else ""}>{esc(t)}</tspan>' for k, t in line)
        b.append(f'<text x="34" y="{y}" text-anchor="end" class="mono" font-size="13" fill="{c["faint"]}" opacity="0.8">{i+1}</text>'
                 f'<text x="52" y="{y}" class="mono" font-size="15" xml:space="preserve">{spans}</text>')
    return svg(W, H, "".join(b), css, "Sobre mí: Fullstack Developer, backend con Node.js y datos con Python; construyendo CoffeeLink; Chile.")


def ahora(c):
    H, pad = 148, 22
    colw = (W - 2 * pad - 2 * 24) / 3
    css = base_css(c, (("Inter", 400), ("Inter", 800), ("JBMono", 700))) + (
        "@keyframes pulse{0%{r:4;opacity:1}100%{r:11;opacity:0}}.pl{animation:pulse 2s ease-out infinite}")
    b = [card_bg(0, 0, W, H, c, rx=16),
         f'<circle cx="{pad+5}" cy="32" r="4" fill="{c["teal"]}"/><circle class="pl" cx="{pad+5}" cy="32" r="4" fill="none" stroke="{c["teal"]}" stroke-width="1.5"/>',
         f'<text x="{pad+18}" y="38" class="sans" font-size="18" font-weight="800" fill="{c["text"]}">Ahora mismo</text>']
    for i, (lab, k, txt) in enumerate(AHORA):
        x = pad + i * (colw + 24)
        a = c[k]
        b.append(f'<rect x="{x:.1f}" y="60" width="3" height="66" rx="1.5" fill="{a}"/>'
                 f'<text x="{x+14:.1f}" y="76" class="mono" font-size="13" font-weight="700" fill="{a}" letter-spacing="1">{esc(lab)}</text>')
        for j, line in enumerate(wrap(txt, 14.5, colw - 16)[:3]):
            b.append(f'<text x="{x+14:.1f}" y="{100 + j*21}" class="sans" font-size="14.5" fill="{c["muted"]}">{esc(line)}</text>')
    alt = "Ahora mismo: " + " ".join(f"{l.capitalize()}: {t}" for l, _, t in AHORA)
    return svg(W, H, "".join(b), css, alt)


def tech_chart(c):
    pad, top, bh, gap = 24, 74, 20, 14
    half = len(TECH_USO) // 2 + len(TECH_USO) % 2
    H = top + half * (bh + gap) + 14
    colw = (W - 2 * pad - 40) / 2
    lw, bw = 160, colw - 160 - 40
    mx = max(v for _, v in TECH_USO)
    css = base_css(c, (("Inter", 400), ("Inter", 800), ("JBMono", 400), ("JBMono", 700)))
    b = [card_bg(0, 0, W, H, c, rx=16),
         f'<defs><linearGradient id="bar" x1="0" x2="1"><stop offset="0" stop-color="{c["copper"]}"/><stop offset="1" stop-color="{c["gold"]}"/></linearGradient></defs>',
         f'<text x="{pad}" y="38" class="sans" font-size="18" font-weight="800" fill="{c["text"]}">Más usadas</text>',
         f'<text x="{W-pad}" y="37" text-anchor="end" class="mono" font-size="13" fill="{c["faint"]}">repositorios públicos donde aparece cada una</text>',
         f'<path d="M{W/2},{top-6} V{H-18}" stroke="{c["border"]}" stroke-dasharray="3 5"/>']
    for i, (name, v) in enumerate(TECH_USO):
        col, row = divmod(i, half)
        x0 = pad + col * (colw + 40)
        y = top + row * (bh + gap)
        w = bw * v / mx
        bx = x0 + lw
        b.append(f'<text x="{bx-12:.1f}" y="{y+bh*0.74:.1f}" text-anchor="end" class="sans" font-size="14.5" fill="{c["text"]}">{esc(name)}</text>'
                 f'<rect x="{bx:.1f}" y="{y}" width="{bw:.1f}" height="{bh}" rx="5" fill="{c["surface2"]}"/>'
                 f'<rect x="{bx:.1f}" y="{y}" width="{w:.1f}" height="{bh}" rx="5" fill="url(#bar)"/>'
                 f'<text x="{bx+w+8:.1f}" y="{y+bh*0.74:.1f}" class="mono" font-size="13.5" font-weight="700" fill="{c["muted"]}">{v}</text>')
    alt = "Tecnologías más usadas en repositorios públicos: " + ", ".join(f"{a} ({v})" for a, v in TECH_USO)
    return svg(W, H, "".join(b), css, alt)


def stack(c):
    pad, ch, isz, fs = 22, 30, 15, 13.5
    css = base_css(c, (("Inter", 600), ("Inter", 800), ("JBMono", 700)))
    b, y = [], 30
    b.append(f'<text x="{pad}" y="{y+8}" class="sans" font-size="18" font-weight="800" fill="{c["text"]}">Lenguajes, librerías y frameworks</text>')
    y += 34
    for gi, (label, k, items) in enumerate(STACK):
        a = c[k]
        b.append(f'<text x="{pad}" y="{y+12}" class="mono" font-size="13" font-weight="700" fill="{a}" letter-spacing="1">{esc(label)}</text>')
        y += 24
        x = pad
        for t in items:
            has = bool(ICONS.get(t))
            tw = text_width(t, fs, "Inter", 600)
            wdt = tw + 22 + (isz + 7 if has else 9)
            if x + wdt > W - pad:
                x, y = pad, y + ch + 8
            b.append(f'<rect x="{x:.1f}" y="{y}" width="{wdt:.1f}" height="{ch}" rx="8" fill="{c["surface2"]}" stroke="{c["border"]}"/>')
            tx = x + 11
            if has:
                b.append(logo(t, tx, y + (ch - isz) / 2, isz, c))
                tx += isz + 7
            else:
                b.append(f'<circle cx="{tx+2:.1f}" cy="{y+ch/2}" r="2.5" fill="{a}"/>')
                tx += 9
            b.append(f'<text x="{tx:.1f}" y="{y+ch/2+fs*0.36:.1f}" class="sans" font-size="{fs}" font-weight="600" fill="{c["text"]}">{esc(t)}</text>')
            x += wdt + 7
        y += ch + 22
    H = y + 2
    alt = "Stack: " + "; ".join(f"{l.capitalize()}: {', '.join(it)}" for l, _, it in STACK)
    return svg(W, H, card_bg(0, 0, W, H, c, rx=16) + "".join(b), css, alt)


def competencias(c):
    cols, ch = 2, 150
    rows = (len(COMPETENCIAS) + 1) // 2
    H = rows * ch + (rows - 1) * 14
    css = base_css(c, (("Inter", 400), ("Inter", 800), ("JBMono", 700)))
    b = []
    for i, (t, k, d, ev) in enumerate(COMPETENCIAS):
        r, q = divmod(i, cols)
        x, y = q * (CARD_W + GAP), r * (ch + 14)
        a = c[k]
        b.append(card_bg(x, y, CARD_W, ch, c)
                 + f'<rect x="{x}" y="{y+20}" width="4" height="28" fill="{a}"/>'
                 f'<text x="{x+22}" y="{y+40}" class="sans" font-size="16.5" font-weight="800" fill="{c["text"]}">{esc(t)}</text>'
                 f'<text x="{x+CARD_W-20}" y="{y+39}" text-anchor="end" class="mono" font-size="13" font-weight="700" fill="{a}">{i+1:02d}</text>')
        for j, line in enumerate(wrap(d, 14, CARD_W - 44)[:3]):
            b.append(f'<text x="{x+22}" y="{y+68+j*20}" class="sans" font-size="14" fill="{c["muted"]}">{esc(line)}</text>')
        b.append(f'<text x="{x+22}" y="{y+ch-17}" class="sans" font-size="13.5" fill="{c["faint"]}"><tspan fill="{a}" font-weight="800">→ </tspan>{esc(ev)}</text>')
    alt = "Competencias: " + "; ".join(f"{t}: {d}" for t, _, d, _ in COMPETENCIAS)
    return svg(W, H, "".join(b), css, alt)


def coffeelink_card(c):
    d = COFFEELINK
    lx, lw = 32, 470
    desc = wrap(d["desc"], 14.5, lw)
    tags_y = 116 + len(desc) * 22 + 6
    tags_svg, end = pills_flow(lx, tags_y, lx + lw, d["tags"], c["copper"], c, size=13, h=26, gap=7)
    H = max(end + 30, 262)
    css = base_css(c) + "@keyframes pulse{0%{r:4;opacity:1}100%{r:11;opacity:0}}.pl{animation:pulse 2s ease-out infinite}"
    b = [f'<defs><linearGradient id="cl" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{c["copper"]}" stop-opacity="0.16"/><stop offset="0.6" stop-color="{c["gold"]}" stop-opacity="0.04"/><stop offset="1" stop-color="{c["teal"]}" stop-opacity="0.10"/></linearGradient>'
         f'<clipPath id="cc"><rect width="{W}" height="{H}" rx="18"/></clipPath></defs>',
         f'<g clip-path="url(#cc)"><rect width="{W}" height="{H}" fill="{c["surface"]}"/><rect width="{W}" height="{H}" fill="url(#cl)"/>'
         f'<rect width="6" height="{H}" fill="{c["copper"]}"/></g>',
         f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="17.5" fill="none" stroke="{c["border"]}"/>',
         f'<circle cx="{lx+5}" cy="36" r="4" fill="{c["teal"]}"/><circle class="pl" cx="{lx+5}" cy="36" r="4" fill="none" stroke="{c["teal"]}" stroke-width="1.5"/>',
         f'<text x="{lx+17}" y="41" class="mono" font-size="13" font-weight="700" fill="{c["teal"]}" letter-spacing="1">{esc(d["categoria"])}</text>',
         f'<text x="{lx}" y="86" class="sans" font-size="34" font-weight="800" fill="{c["text"]}" letter-spacing="-0.6">{esc(d["titulo"])}</text>']
    for i, line in enumerate(desc):
        b.append(f'<text x="{lx}" y="{116 + i*22}" class="sans" font-size="14.5" fill="{c["muted"]}">{esc(line)}</text>')
    b.append(tags_svg)
    mx, mw = 534, W - 534 - 26
    for i, (name, st) in enumerate(d["modulos"]):
        y = 28 + i * 66
        b.append(f'<rect x="{mx}" y="{y}" width="{mw}" height="56" rx="11" fill="{c["surface2"]}" stroke="{c["border"]}"/>'
                 f'<rect x="{mx}" y="{y+13}" width="3" height="30" rx="1.5" fill="{[c["copper"], c["gold"], c["teal"]][i]}"/>'
                 f'<text x="{mx+18}" y="{y+24}" class="sans" font-size="15.5" font-weight="600" fill="{c["text"]}">{esc(name)}</text>'
                 f'<text x="{mx+18}" y="{y+44}" class="mono" font-size="13" fill="{c["faint"]}">{esc(st)}</text>')
    b.append(f'<text x="{W-26}" y="{H-20}" text-anchor="end" class="mono" font-size="13" fill="{c["faint"]}">{esc(d["nota"])}</text>')
    return svg(W, H, "".join(b), css, f'{d["titulo"]}: {d["desc"]}')


METHOD = {"GET": "teal", "POST": "copper", "PATCH": "gold", "PUT": "gold", "DELETE": "rose"}


def api_panel(c, rows, a, w, h):
    """Ilustración de los endpoints reales de la API (en lugar de una captura)."""
    b = [f'<rect width="{w}" height="{h}" fill="{c["bg"]}"/>', dot_grid(w, h, c, step=20, pid="ap"),
         f'<rect x="16" y="16" width="{w-32}" height="{h-32}" rx="10" fill="{c["surface"]}" stroke="{c["border"]}"/>',
         f'<text x="32" y="42" class="mono" font-size="13" font-weight="700" fill="{a}" letter-spacing="0.8">REST API</text>',
         f'<text x="{w-32}" y="42" text-anchor="end" class="mono" font-size="13" fill="{c["faint"]}">Express · JSON</text>',
         f'<path d="M16,54 H{w-16}" stroke="{c["border"]}"/>']
    for i, (m, path, note) in enumerate(rows):
        y = 64 + i * 22.5
        mc = c[METHOD[m]]
        bw = text_width(m, 11.5, "JBMono", 700) + 12
        b.append(f'<rect x="32" y="{y}" width="{bw:.1f}" height="17" rx="4" fill="{mc}" fill-opacity="0.16"/>'
                 f'<text x="38" y="{y+12.6:.1f}" class="mono" font-size="11.5" font-weight="700" fill="{mc}">{m}</text>'
                 f'<text x="{32+bw+8:.1f}" y="{y+13:.1f}" class="mono" font-size="13" fill="{c["text"]}">{esc(path)}</text>'
                 f'<text x="{w-32}" y="{y+13:.1f}" text-anchor="end" class="sans" font-size="12.5" fill="{c["faint"]}">{esc(note)}</text>')
    return "".join(b)


def store_panel(c, items, a, w, h):
    """Esquema de la interfaz de CoffeeLink Store con productos reales del catálogo."""
    b = [f'<rect width="{w}" height="{h}" fill="{c["bg"]}"/>',
         f'<rect x="16" y="16" width="{w-32}" height="{h-32}" rx="10" fill="{c["surface"]}" stroke="{c["border"]}"/>',
         f'<path d="M16,48 H{w-16}" stroke="{c["border"]}"/>',
         f'<text x="30" y="38" class="sans" font-size="14" font-weight="800" fill="{c["text"]}">CoffeeLink</text>',
         f'<text x="{w-64}" y="37" text-anchor="end" class="sans" font-size="12.5" fill="{c["faint"]}">Granos · Métodos</text>',
         f'<circle cx="{w-40}" cy="32" r="9" fill="{a}" fill-opacity="0.18" stroke="{a}"/>'
         f'<text x="{w-40}" y="36" text-anchor="middle" class="sans" font-size="11" font-weight="800" fill="{a}">3</text>']
    cw = (w - 32 - 28 - 16) / 3
    tones = [c["crema"], c["copper"], c["gold"]]
    for i, (name, price) in enumerate(items):
        x = 30 + i * (cw + 8)
        b.append(f'<rect x="{x:.1f}" y="60" width="{cw:.1f}" height="138" rx="8" fill="{c["surface2"]}" stroke="{c["border"]}"/>'
                 f'<rect x="{x+8:.1f}" y="68" width="{cw-16:.1f}" height="62" rx="6" fill="{tones[i]}" fill-opacity="0.28"/>'
                 f'<ellipse cx="{x+cw/2:.1f}" cy="99" rx="11" ry="15" fill="none" stroke="{tones[i]}" stroke-width="2" transform="rotate(25 {x+cw/2:.1f} 99)"/>'
                 f'<path d="M{x+cw/2-4:.1f},88 q8,11 0,22" fill="none" stroke="{tones[i]}" stroke-width="2"/>')
        for j, line in enumerate(wrap(name, 12, cw - 16, "Inter", 600)[:2]):
            b.append(f'<text x="{x+8:.1f}" y="{148 + j*15}" class="sans" font-size="12" font-weight="600" fill="{c["text"]}">{esc(line)}</text>')
        b.append(f'<text x="{x+8:.1f}" y="188" class="mono" font-size="12" font-weight="700" fill="{a}">{esc(price)}</text>')
    return "".join(b)


def project_card(c, p):
    H, sh = 452, 216
    a = c[p["acento"]]
    css = base_css(c)
    b = [f'<defs><clipPath id="top"><path d="M14,0 H{CARD_W-14} A14,14 0 0 1 {CARD_W},14 V{sh} H0 V14 A14,14 0 0 1 14,0 Z"/></clipPath>'
         f'<linearGradient id="cg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{a}" stop-opacity="0.08"/><stop offset="0.6" stop-color="{a}" stop-opacity="0"/></linearGradient></defs>',
         card_bg(0, 0, CARD_W, H, c), f'<rect x="0.5" y="0.5" width="{CARD_W-1}" height="{H-1}" rx="14" fill="url(#cg)"/>']
    if "shot" in p:
        media = f'<image href="{shot_data(p["shot"])}" x="0" y="0" width="{CARD_W}" height="{sh}" preserveAspectRatio="xMidYMid slice"/>'
    elif "api" in p:
        media = api_panel(c, p["api"], a, CARD_W, sh)
    else:
        media = store_panel(c, p["store"], a, CARD_W, sh)
    b.append(f'<g clip-path="url(#top)">{media}</g>'
             f'<path d="M0.5,{sh} H{CARD_W-0.5}" stroke="{c["border"]}"/><rect x="22" y="{sh-2}" width="56" height="4" rx="2" fill="{a}"/>')
    y = sh + 32
    b.append(f'<text x="22" y="{y}" class="mono" font-size="13" font-weight="700" fill="{a}" letter-spacing="1">{esc(p["categoria"])}</text>'
             f'<text x="22" y="{y+30}" class="sans" font-size="21" font-weight="800" fill="{c["text"]}" letter-spacing="-0.3">{esc(p["titulo"])}</text>'
             f'<text x="22" y="{y+52}" class="mono" font-size="13" fill="{c["faint"]}">sebakine/{esc(p["slug"])}</text>')
    for i, line in enumerate(wrap(p["desc"], 14, CARD_W - 44)[:3]):
        b.append(f'<text x="22" y="{y+80+i*20}" class="sans" font-size="14" fill="{c["muted"]}">{esc(line)}</text>')
    tags, _ = pills_flow(22, y + 132, CARD_W - 22, p["tags"], a, c, size=12.5, h=25, gap=6, max_rows=1)
    b.append(tags)
    b.append(f'<path d="M22,{H-36} H{CARD_W-22}" stroke="{c["border"]}" stroke-dasharray="3 5"/>'
             f'<text x="22" y="{H-14}" class="mono" font-size="13" fill="{c["faint"]}">{esc(p["nota"])}</text>'
             f'<text x="{CARD_W-22}" y="{H-14}" text-anchor="end" class="mono" font-size="13" font-weight="700" fill="{a}">ver repo →</text>')
    return svg(CARD_W, H, "".join(b), css, f'{p["titulo"]}: {p["desc"]}')


def timeline(c):
    H = 176
    n = len(TRAYECTORIA)
    step = W / n
    ly = 44
    css = base_css(c, (("Inter", 400), ("Inter", 800), ("JBMono", 700)))
    b = [f'<path d="M{step/2},{ly} H{W-step/2}" stroke="{c["border"]}" stroke-width="2"/>']
    for i, (yr, t, d, k) in enumerate(TRAYECTORIA):
        cx = step * i + step / 2
        a = c[k]
        b.append(f'<text x="{cx}" y="{ly-20}" text-anchor="middle" class="mono" font-size="13.5" font-weight="700" fill="{a}">{yr}</text>'
                 f'<circle cx="{cx}" cy="{ly}" r="8" fill="{c["bg"]}" stroke="{a}" stroke-width="3"/>'
                 + (f'<circle cx="{cx}" cy="{ly}" r="3.5" fill="{a}"/>' if i == n - 1 else ''))
        tl = wrap(t, 14.5, step - 14, "Inter", 800)[:2]
        for j, line in enumerate(tl):
            b.append(f'<text x="{cx}" y="{ly+34+j*19}" text-anchor="middle" class="sans" font-size="14.5" font-weight="800" fill="{c["text"]}">{esc(line)}</text>')
        for j, line in enumerate(wrap(d, 13.5, step - 14)[:3]):
            b.append(f'<text x="{cx}" y="{ly+38+len(tl)*19+j*18}" text-anchor="middle" class="sans" font-size="13.5" fill="{c["muted"]}">{esc(line)}</text>')
    alt = "Trayectoria: " + "; ".join(f"{y} {t}: {d}" for y, t, d, _ in TRAYECTORIA)
    return svg(W, H, "".join(b), css, alt)


def formacion(c):
    css = base_css(c)
    b = [f'<text x="0" y="18" class="mono" font-size="13" font-weight="700" fill="{c["copper"]}" letter-spacing="1">FORMACIÓN</text>']
    cw, y0, chh = (W - 2 * GAP) / 3, 32, 122
    for i, (t, inst, tipo, k) in enumerate(ACADEMICA):
        x = i * (cw + GAP)
        a = c[k]
        b.append(card_bg(x, y0, cw, chh, c) + f'<rect x="{x:.1f}" y="{y0+18}" width="4" height="26" fill="{a}"/>'
                 f'<text x="{x+20:.1f}" y="{y0+31}" class="mono" font-size="12.5" font-weight="700" fill="{a}" letter-spacing="0.8">{esc(tipo.upper())}</text>')
        tl = wrap(t, 16, cw - 40, "Inter", 800)[:2]
        for j, line in enumerate(tl):
            b.append(f'<text x="{x+20:.1f}" y="{y0+56+j*20}" class="sans" font-size="16" font-weight="800" fill="{c["text"]}">{esc(line)}</text>')
        b.append(f'<text x="{x+20:.1f}" y="{y0+56+len(tl)*20+6}" class="sans" font-size="13" fill="{c["muted"]}">{esc(inst)}</text>')
    y1 = y0 + chh + 34
    b.append(f'<text x="0" y="{y1}" class="mono" font-size="13" font-weight="700" fill="{c["copper"]}" letter-spacing="1">CERTIFICACIONES CODERHOUSE</text>')
    n = len(CERT_CODER)
    bwid = W / n
    ring = [c["copper"], c["gold"], c["teal"], c["sky"], c["sage"], c["rose"]]
    for i, (ab, name) in enumerate(CERT_CODER):
        cx, cy = bwid * i + bwid / 2, y1 + 54
        a = ring[i % len(ring)]
        pts = " ".join(f"{cx + 31*math.cos(math.radians(60*k-90)):.1f},{cy + 31*math.sin(math.radians(60*k-90)):.1f}" for k in range(6))
        pts2 = " ".join(f"{cx + 25*math.cos(math.radians(60*k-90)):.1f},{cy + 25*math.sin(math.radians(60*k-90)):.1f}" for k in range(6))
        b.append(f'<polygon points="{pts}" fill="{a}" fill-opacity="0.12" stroke="{a}" stroke-width="2"/>'
                 f'<polygon points="{pts2}" fill="none" stroke="{a}" stroke-opacity="0.45" stroke-width="1"/>'
                 f'<text x="{cx}" y="{cy+5}" text-anchor="middle" class="mono" font-size="{14 if len(ab)<=3 else 12.5}" font-weight="700" fill="{a}">{esc(ab)}</text>')
        fsz = 13 if all(text_width(wd, 13, "Inter", 600) <= bwid - 8 for wd in name.split()) else 12
        for j, line in enumerate(wrap(name, fsz, bwid - 8, "Inter", 600)[:3]):
            b.append(f'<text x="{cx}" y="{cy+52+j*16}" text-anchor="middle" class="sans" font-size="{fsz}" font-weight="600" fill="{c["muted"]}">{esc(line)}</text>')
    y2 = y1 + 170
    iw = 236
    cw2 = (W - iw - 2 * GAP) / 2
    b.append(f'<text x="0" y="{y2}" class="mono" font-size="13" font-weight="700" fill="{c["copper"]}" letter-spacing="1">OTRAS CERTIFICACIONES</text>'
             f'<text x="{W-iw}" y="{y2}" class="mono" font-size="13" font-weight="700" fill="{c["copper"]}" letter-spacing="1">IDIOMAS</text>')
    yy, chh2 = y2 + 14, 150
    for i, (org, yr, d, k) in enumerate(CERT_OTRAS):
        x = i * (cw2 + GAP)
        a = c[k]
        b.append(card_bg(x, yy, cw2, chh2, c)
                 + f'<text x="{x+20:.1f}" y="{yy+32}" class="sans" font-size="16" font-weight="800" fill="{c["text"]}">{esc(org)}</text>'
                 f'<text x="{x+cw2-20:.1f}" y="{yy+31}" text-anchor="end" class="mono" font-size="13" font-weight="700" fill="{a}">{yr}</text>')
        for j, line in enumerate(wrap(d, 13.5, cw2 - 40)[:5]):
            b.append(f'<text x="{x+20:.1f}" y="{yy+58+j*19}" class="sans" font-size="13.5" fill="{c["muted"]}">{esc(line)}</text>')
    xi = W - iw
    b.append(card_bg(xi, yy, iw, chh2, c))
    for j, (lang, lvl) in enumerate(IDIOMAS):
        ly = yy + 40 + j * 56
        b.append(f'<text x="{xi+20}" y="{ly}" class="sans" font-size="16" font-weight="800" fill="{c["text"]}">{esc(lang)}</text>'
                 f'<text x="{xi+iw-20}" y="{ly}" text-anchor="end" class="mono" font-size="13" font-weight="700" fill="{c["teal"]}">{esc(lvl)}</text>')
        dots = 6 if j == 0 else 5
        seg = (iw - 40 - 5 * 6) / 6
        for k in range(6):
            b.append(f'<rect x="{xi+20+k*(seg+6):.1f}" y="{ly+12}" width="{seg:.1f}" height="5" rx="2.5" fill="{c["teal"] if k < dots else c["surface2"]}"/>')
    H = yy + chh2 + 2
    alt = ("Formación: " + "; ".join(f"{t}, {i}" for t, i, _, _ in ACADEMICA) + ". Certificaciones Coderhouse: " + ", ".join(n for _, n in CERT_CODER)
           + ". Otras: " + "; ".join(f"{o} {y}: {d}" for o, y, d, _ in CERT_OTRAS) + ". Idiomas: español nativo, inglés C1.")
    return svg(W, int(H), "".join(b), css, alt)


SNAKE_DOTS = {  # deben coincidir con .github/workflows/snake.yml
    "light": ["#EFE4D6", "#E5C29B", "#D49A62", "#B86F35", "#8A4A1E"],
    "dark": ["#2B211B", "#5A3C28", "#8A5A35", "#C07A45", "#F0A060"],
}


def activity(c, name):
    H = 40
    css = base_css(c, (("Inter", 400), ("JBMono", 400)))
    dots = SNAKE_DOTS[name]
    lx = W - 4 - 5 * 18 - text_width("Más", 13.5, "Inter", 400)
    b = [f'<text x="0" y="25" class="sans" font-size="14" fill="{c["muted"]}">Cada cuadro es un día · la serpiente recorre las contribuciones y se actualiza a diario</text>',
         f'<text x="{lx-8-text_width("Menos", 13.5):.1f}" y="25" class="sans" font-size="13.5" fill="{c["faint"]}">Menos</text>']
    for i, col in enumerate(dots):
        b.append(f'<rect x="{lx + i*18:.1f}" y="12" width="13" height="13" rx="3" fill="{col}" stroke="{c["border"]}" stroke-width="0.6"/>')
    b.append(f'<text x="{W}" y="25" text-anchor="end" class="sans" font-size="13.5" fill="{c["faint"]}">Más</text>')
    return svg(W, H, "".join(b), css, "Leyenda del gráfico de actividad")


def footer(c):
    H = 90
    css = base_css(c, (("JBMono", 400),)) + "@keyframes dash{to{stroke-dashoffset:-40}}.w{animation:dash 6s linear infinite}"
    path = "M0,45 " + " ".join(f"Q{x+27.5},{30 if (x//55)%2==0 else 60} {x+55},45" for x in range(0, W, 55))
    body = (f'<defs><clipPath id="fc"><rect x="0" y="0" width="{W/2-200}" height="{H}"/><rect x="{W/2+200}" y="0" width="{W/2-200}" height="{H}"/></clipPath></defs>'
            f'<path class="w" clip-path="url(#fc)" d="{path}" fill="none" stroke="{c["copper"]}" stroke-opacity="0.5" stroke-width="2" stroke-dasharray="8 12"/>'
            f'<text x="{W/2}" y="50" text-anchor="middle" class="mono" font-size="14" fill="{c["muted"]}">hecho con código y café de especialidad</text>')
    return svg(W, H, body, css, "Hecho con código y café de especialidad")


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
        files = {
            f"header-{name}.svg": header(c), f"about-{name}.svg": about(c), f"ahora-{name}.svg": ahora(c),
            f"tech-{name}.svg": tech_chart(c), f"stack-{name}.svg": stack(c), f"skills-{name}.svg": competencias(c),
            f"coffeelink-{name}.svg": coffeelink_card(c), f"timeline-{name}.svg": timeline(c),
            f"education-{name}.svg": formacion(c), f"activity-{name}.svg": activity(c, name), f"footer-{name}.svg": footer(c),
        }
        for num, title, comment in SECCIONES:
            files[f"sections/{num}-{name}.svg"] = section(c, num, title, comment)
        for p in PROYECTOS:
            files[f"projects/{p['slug'].lower()}-{name}.svg"] = project_card(c, p)
        for slug, d in BANNERS.items():
            files[f"banners/{slug.lower()}-{name}.svg"] = banner(c, d)
        for rel, content in files.items():
            (OUT / rel).write_text(content, encoding="utf-8")
    if MISSING:
        print("AVISO: caracteres sin glifo en las fuentes:", "".join(sorted(MISSING)))
    print("SVG generados en", OUT)


if __name__ == "__main__":
    main()
