<p align="center">
  <img src="docs/banner.svg" alt="banner de collection-skill" width="100%"/>
</p>

<h3 align="center">
  Descubrir · Catalogar · Elegir · Recolectar
</h3>

<p align="center">
  <a href="README.md">English</a> ·
  <a href="README.zh-CN.md">简体中文</a> ·
  <a href="README.ja.md">日本語</a> ·
  <a href="https://github.com/Yuuqq/collection-skill/blob/main/README.es.md">Español</a>
</p>

<p align="center">
  <img alt="estado" src="https://img.shields.io/badge/estado-activo-22c55e?style=flat-square">
  <img alt="licencia" src="https://img.shields.io/badge/licencia-MIT-blue?style=flat-square">
  <img alt="catálogo" src="https://img.shields.io/badge/herramientas-183-8b5cf6?style=flat-square">
  <img alt="lenguaje" src="https://img.shields.io/badge/lenguaje%20principal-Python-3776AB?style=flat-square">
  <img alt="plataforma" src="https://img.shields.io/badge/plataforma-multiplataforma-475569?style=flat-square">
</p>

---

> Una skill que **descubre y cataloga skills y repositorios de recolección/scraping en GitHub**, y luego **recomienda progresivamente la herramienta adecuada y comienza a extraer** cuando quieres obtener datos.

## ✨ Características

| | |
|:--|:--|
| 🗂️ **Catálogo curado** | Descubre repos en GitHub y los clasifica en **cinco categorías canónicas**, con deduplicación y puntuación. |
| 🧭 **Divulgación progresiva** | Nunca vuelca todo el catálogo — menú de categorías → ficha de herramienta → flujo → recolección. |
| 🗃️ **JSON como fuente** | `tool-catalog.json` es la única fuente de verdad; la vista Markdown se genera. |
| 🔐 **Seguro por defecto** | Lee tokens desde el llavero de `gh` / variables de entorno — sin credenciales en el repo. |
| ⏱️ **Programable** | Instala una actualización periódica vía cron / Programador de tareas. |

## 📦 Qué hace

Dos mitades que comparten **una base de conocimiento**:

<p align="center">
  <img src="docs/flow.svg" alt="Cómo funciona collection-skill" width="92%"/>
</p>

### ① Descubrir & Catalogar
Escanea GitHub periódicamente en busca de repos *de recolección*, en cinco categorías:

| Etiqueta | Significado | Ejemplos |
|----------|-------------|----------|
| 🕸️ `web-scraper` | HTML estático / HTTP simple | BeautifulSoup, httpx, Selectolax, Scrapy |
| ⚡ `dynamic-scraper` | Páginas con JS, SPA | Playwright, Selenium, Crawl4AI |
| 🔌 `api-collector` | REST/GraphQL, SDK, ETL | recolectores por SDK, pipelines |
| 🤖 `agent-skill` | Skills de Claude/GPT, servidores MCP | frameworks de uso de herramientas |
| 📚 `dataset` | Datasets públicos, awesome-lists | repos curados de recursos |

### ② Elegir & Recolectar
Cuando dices *"quiero extraer X"*, recorre un embudo corto:

```
menú de categorías  →  ficha de herramienta  →  cargar flujo  →  confirmar alcance  →  recolectar
```

## 📊 Estado del catálogo

> Generado desde `tool-catalog.json` · última actualización `2026-07-05`

| Categoría | Cuenta | | Lenguajes principales |
|-----------|-------:|---|------------------------|
| 🕸️ web-scraper | 42 | | Python · Go · JS |
| 🔌 api-collector | 41 | | Python · TypeScript |
| ⚡ dynamic-scraper | 39 | | Python · TypeScript |
| 🤖 agent-skill | 31 | | JavaScript · Python |
| 📚 dataset | 30 | | HTML · Markdown |
| **Total** | **183** | | **Python (89)** lidera |

## 🎴 Tarjetas por categoría

<table>
  <tr>
    <td width="50%" align="center"><img src="docs/card-web-scraper.svg" alt="tarjeta web-scraper"/><br><sub><a href="docs/card-web-scraper.svg">🕸️ web-scraper · 42 herramientas</a></sub></td>
    <td width="50%" align="center"><img src="docs/card-dynamic-scraper.svg" alt="tarjeta dynamic-scraper"/><br><sub><a href="docs/card-dynamic-scraper.svg">⚡ dynamic-scraper · 39 herramientas</a></sub></td>
  </tr>
  <tr>
    <td width="50%" align="center"><img src="docs/card-api-collector.svg" alt="tarjeta api-collector"/><br><sub><a href="docs/card-api-collector.svg">🔌 api-collector · 41 herramientas</a></sub></td>
    <td width="50%" align="center"><img src="docs/card-agent-skill.svg" alt="tarjeta agent-skill"/><br><sub><a href="docs/card-agent-skill.svg">🤖 agent-skill · 31 herramientas</a></sub></td>
  </tr>
  <tr>
    <td colspan="2" align="center"><img src="docs/card-dataset.svg" alt="tarjeta dataset"/><br><sub><a href="docs/card-dataset.svg">📚 dataset · 30 herramientas</a></sub></td>
  </tr>
</table>

## 🚀 Uso

Invoca la skill y habla con naturalidad:

| Dices | Qué ocurre |
|-------|------------|
| `refresh` / `discover` / `actualizar` | Ejecuta `scripts/discover_repos.py`, actualiza el catálogo |
| `quiero extraer X` / `抓 X 数据` | Divulgación progresiva → categorías → ficha → recolección |
| `browse` / `ver catálogo` | Vista de solo lectura de categorías/fichas |
| `schedule` / `programar` | Instala una actualización periódica (cron / Programador de tareas) |

## 🛠️ Inicio rápido

```bash
# 1. (recomendado) autenticarse — 30 req/min de búsqueda vs 10 sin autenticar
gh auth login

# 2. primera actualización
python scripts/discover_repos.py
python scripts/build_catalog_md.py

# 3. (opcional) programar actualización semanal — invoca la skill y di "programar"
```

## 🗺️ Estructura del proyecto

```
collection-skill/
├── SKILL.md                       # Enrutador + principios esenciales
├── workflows/
│   ├── discover-catalog.md        # Actualizar desde GitHub
│   ├── match-and-crawl.md         # Divulgación progresiva → recolección
│   ├── browse-catalog.md          # Vista de solo lectura
│   └── schedule-refresh.md        # Instalar actualización periódica
├── references/
│   ├── tool-catalog.json          # Dato canónico (edita esto)
│   ├── tool-catalog.md            # Vista generada (no editar)
│   ├── discovery-log.md           # Historial de solo anexión
│   ├── category-keywords.md       # Términos de búsqueda por categoría
│   ├── repo-schema.md             # Esquema de entrada
│   └── rate-limit-guide.md        # Límites de la API de GitHub
├── templates/
│   ├── crawl-template.md          # Flujo de recolección genérico
│   ├── discovery-log-entry.md
│   └── run_scheduled_refresh.sh.template
├── scripts/
│   ├── discover_repos.py          # Búsqueda en GitHub → catálogo
│   ├── build_catalog_md.py        # JSON → Markdown
│   └── add_repo.py                # Añadir una entrada manualmente
└── docs/                          # Banners y diagramas del README
```

## ⚖️ Reglas de diseño

- **JSON es canónico.** `tool-catalog.md` se regenera con `build_catalog_md.py` — nunca lo edites a mano.
- **Divulgación progresiva.** Primero categorías, luego fichas, y el flujo solo tras elegir herramienta.
- **Sin credenciales en el repo.** Los tokens provienen de `$GITHUB_TOKEN` o `gh auth token`.
- **Campos de usuario preservados.** El redescubrimiento nunca sobrescribe `notes`, `verified`, `favorite`, `workflow_file`.
- **Respeta los límites.** Honra `robots.txt`, los límites de tasa y los términos; confirma el alcance antes de recolectar en un dominio nuevo.

## 🌍 Traducciones

| Idioma | Archivo |
|--------|---------|
| English | [`README.md`](README.md) |
| 简体中文 | [`README.zh-CN.md`](README.zh-CN.md) |
| 日本語 | [`README.ja.md`](README.ja.md) |
| Español | [`README.es.md`](README.es.md) |

## 📄 Licencia

MIT
