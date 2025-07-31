# ServoSenseApp – Project Guide

This guide gives you a **big‑picture overview**, local **setup instructions**, development workflows, conventions, and troubleshooting for ServoSenseApp.

* Backend: **Django + DRF + Channels** (ASGI, Redis)
* Frontend: **Nuxt 3 (Vue 3)**
* Local dev: **Docker Compose**

---

## Table of Contents

* [Overview](https://chatgpt.com/c/688b9034-1bc8-832a-b333-1d5803d4e889#overview)
* [Features](https://chatgpt.com/c/688b9034-1bc8-832a-b333-1d5803d4e889#features)
* [Architecture](https://chatgpt.com/c/688b9034-1bc8-832a-b333-1d5803d4e889#architecture)
* [Repository Layout](https://chatgpt.com/c/688b9034-1bc8-832a-b333-1d5803d4e889#repository-layout)
* [Quickstart (Local Dev)](https://chatgpt.com/c/688b9034-1bc8-832a-b333-1d5803d4e889#quickstart-local-dev)
* [Environment & Config](https://chatgpt.com/c/688b9034-1bc8-832a-b333-1d5803d4e889#environment--config)
* [Domain Model](https://chatgpt.com/c/688b9034-1bc8-832a-b333-1d5803d4e889#domain-model)
* [Simulator & WebSockets](https://chatgpt.com/c/688b9034-1bc8-832a-b333-1d5803d4e889#simulator--websockets)
* [Frontend (Nuxt) – Conventions](https://chatgpt.com/c/688b9034-1bc8-832a-b333-1d5803d4e889#frontend-nuxt--conventions)
* [Keyboard Shortcuts](https://chatgpt.com/c/688b9034-1bc8-832a-b333-1d5803d4e889#keyboard-shortcuts)
* [API & Docs](https://chatgpt.com/c/688b9034-1bc8-832a-b333-1d5803d4e889#api--docs)
* [Testing & Quality](https://chatgpt.com/c/688b9034-1bc8-832a-b333-1d5803d4e889#testing--quality)
* [Troubleshooting](https://chatgpt.com/c/688b9034-1bc8-832a-b333-1d5803d4e889#troubleshooting)
* [Deployment (notes)](https://chatgpt.com/c/688b9034-1bc8-832a-b333-1d5803d4e889#deployment-notes)
* [Roadmap](https://chatgpt.com/c/688b9034-1bc8-832a-b333-1d5803d4e889#roadmap)
* [Glossary](https://chatgpt.com/c/688b9034-1bc8-832a-b333-1d5803d4e889#glossary)

---

## Overview

ServoSenseApp is an engineering‑grade platform for **real‑time sensor monitoring**: ingest readings, visualize live dashboards, and raise alerts on thresholds. It ships with a **simulator** that emits data through **Channels (WebSockets)** so you can see activity in seconds.

---

## Features

* 🔐 Token‑based auth (register, obtain token, `/me`).
* 🧩 Domain: **Workspaces → Machines → Sensors → Readings/Events**.
* 🧪 **Simulator** with threshold alerts; live broadcast via WS.
* 📊 Nuxt dashboard with **drag‑and‑drop canvas** (assign sensors to machines), live readings and events.
* ⚡ **Quickstart/Seed** endpoints for instant demo data.

---

## Architecture

**Backend (ASGI):** Django + DRF expose REST endpoints; Channels handles WebSockets with Redis as the channel layer. A simulator service pushes readings and events to workspace groups.

**Frontend:** Nuxt 3 app consumes REST (`useApi`) and WS (`useWs`), renders a canvas to position machines and attach sensors.

```
+----------------------------+        +-----------------+
|        Nuxt 3 (Vue)        |  REST  |     Django/DRF  |
|  - useApi, useWs           | <----> |  + Channels     |
|  - Canvas & Live Dashboard |        |  + Simulator    |
+--------------^-------------+  WS    +----^------------+
               |                          |
               +--------------------------+
                       Redis (channel layer)
```

---

## Repository Layout

```
.
├─ backend/                 # Django project (DRF + Channels)
│  ├─ app/                  # settings, urls, ASGI
│  ├─ core/                 # models & Workspace API
│  ├─ simulator/            # start/stop + WS broadcast services
│  ├─ requirements*.txt
│  └─ docker-compose.yml, Dockerfile
└─ frontend/                # Nuxt 3 app
   ├─ app/ (pages, components, composables)
   └─ nuxt.config.ts
```

---

## Quickstart (Local Dev)

### Backend

```bash
cd backend
docker compose up
# API:              http://localhost:8000
# Swagger (DRF):    http://localhost:8000/api/docs/
# OpenAPI JSON/YAML http://localhost:8000/api/schema/
```

Useful:

```bash
# run tests
docker compose run --rm app python manage.py test

# migrations
docker compose run --rm app python manage.py makemigrations
docker compose run --rm app python manage.py migrate
```

### Frontend

```bash
cd frontend
npm i
npm run dev
# http://localhost:3000  (Nitro proxies /api and /ws to backend)
```

`nuxt.config.ts` proxies:

```ts
nitro: {
  routeRules: {
    '/api/**': { proxy: 'http://127.0.0.1:8000/api/**' },
    '/ws/**' : { proxy: 'http://127.0.0.1:8000/ws/**' },
  },
},
security: {
  headers: {
    contentSecurityPolicy: {
      'connect-src': ["'self'", 'http:', 'https:', 'ws:', 'wss:'],
    },
  },
},
```

### Quick demo flow (UI)

1. Visit **`/dashboard/workspaces`**.
2. Click **Quickstart (demo)** – creates/seeds a workspace and redirects to its detail view.
3. Click **Start** to start the simulator; readings stream in real‑time.

---

## Environment & Config

**Frontend `.env` (optional, defaults in `nuxt.config.ts`):**

```env
NUXT_PUBLIC_API_BASE=/api
NUXT_PUBLIC_WS_BASE=/ws
# PORT=3000
```

**Backend:** environment is encapsulated in Docker Compose; add secrets/env vars if your `manage.py` requires them for schema build.

---

## Domain Model

Core entities and relations:

* **Workspace** (owned by `User`)
* **Machine** (`workspace` FK; fields: `name`, `kind`, `x`, `y`)
* **Sensor** (`machine` FK nullable; fields: `kind`, `unit`, `threshold`) — unassigned sensors appear in the **Pool** until attached.
* **Reading** (`sensor`, `ts`, `value`)
* **Event** (`workspace`, `ts`, `level`, `sensor?`, `message`)

**Typical flow:** seed a workspace → one or more machines → attach sensors → simulator emits readings → threshold checks create events.

---

## Simulator & WebSockets

**REST control:**

* `POST /api/sim/start/{workspace_id}/`
* `POST /api/sim/stop/{workspace_id}/`

**WebSocket channel:**

* `ws://localhost:8000/ws/workspaces/{workspace_id}/`

**Messages:**

```json
{ "type": "reading", "sensor_id": 1, "value": 61.5, "unit": "°C", "ts": "..." }
{ "type": "event",   "level": "WARN", "sensor_id": 1, "message": "temperature alert" }
```

**Frontend canvas:**

* drag machines (persist `x`,`y` via `PATCH /api/core/machines/{id}/`)
* drag sensors onto machines (persist `PATCH /api/core/sensors/{id}/ { machine }`)
* dropping on **Pool** detaches (`machine: null`).

---

## Frontend (Nuxt) – Conventions

* **Pages:**
  * `pages/dashboard/workspaces/index.vue` – list & quickstart
  * `pages/dashboard/workspaces/[id].vue` – canvas/detail
* **Composables:**`useApi` (typed `api<T>()`) and `useWs` for live updates.
* **State:** keep `last_ws_id` in `localStorage` so the **Continue** button works.
* **UI:** dark theme, Tailwind utility classes.

**Typing `useApi` calls:**

```ts
// Example: type list response using generated OpenAPI types
type WorkspacesList = paths['/api/workspaces/']['get']['responses']['200']['content']['application/json'];
const api = useApi();
const items = ref<WorkspacesList>([]);
items.value = await api<WorkspacesList>('/api/workspaces/');
```

---

## Keyboard Shortcuts

On the dashboard list:

* **g w** → go to Workspaces
* **g n** → open *New workspace* modal
* **g q** → Quickstart demo
* **g l** → Continue last workspace
* **/** → focus search
* **1..9** → open N‑th workspace in the filtered list
* **?** → toggle the shortcuts help modal

(See the dashboard script for implementation.)

---

## API & Docs

* Swagger UI: `/api/docs/` (served by backend)
* OpenAPI schema: `/api/schema/`
* **Static docs (Redoc):**`docs/api.html` built from the schema.
* **Developer guide:**`docs/API_DOCS.md` – explains how to generate schema, Redoc HTML, and TS types; includes CI workflow for GitHub Pages.

> **What is Redoc?** Redoc is a tool that takes an **OpenAPI** schema (YAML/JSON) and renders a **clean, static HTML documentation** page. It’s an alternative to Swagger UI, great when you want a **read‑only**, **SEO‑friendly**, easily hostable `api.html` without a running backend.

---

## Testing & Quality

```bash
cd backend
# unit tests
docker compose run --rm app python manage.py test

# style/format (if available in image)
docker compose run --rm app flake8
docker compose run --rm app isort --check .
docker compose run --rm app black --check .
```

---

## Troubleshooting

* **WS connects but no data** → Ensure CSP allows `ws:`/`wss:` and the Nitro proxy forwards `/ws/**` to backend. Start the simulator.
* **Logs show: `X of Y channels over capacity`** → Usually the browser wasn’t connected (CSP or wrong WS URL). Fix CSP/URL.
* **`PATCH /api/core/machines/{id}/` returns 404** → Make sure the router exposes Machine/Sensor endpoints (ViewSets registered under `/api/core/...`).
* **Docs not updating** → Rebuild schema and `docs/api.html` (`make docs` or `npm run docs`). In CI, check container env for `manage.py spectacular`.

---

## Deployment (notes)

* Run Django under an **ASGI** server (Uvicorn/Daphne) with Redis reachable for Channels.
* Serve Nuxt as static (SSR/SPA) or behind a reverse proxy that forwards `/api/**` and `/ws/**` to backend.
* Harden CSP for production; allow only the required origins.

---

## Roadmap

* Full CRUD on machines/sensors via API + UI forms
* Real‑time charts + historical aggregation
* Roles/permissions, multi‑tenant workspaces
* Export/reporting, webhooks

---

## Glossary

* **OpenAPI** – Specification describing REST endpoints, schemas, and auth.
* **DRF‑Spectacular** – Django library that auto‑generates OpenAPI from DRF.
* **Redoc** – Static HTML renderer for OpenAPI docs (clean UI, no backend needed).
* **Channels** – Django’s ASGI layer enabling WebSockets and background tasks.
* **Nitro Proxy** – Nuxt’s route rules that forward `/api/**` and `/ws/**` to backend.

**License:** MIT
