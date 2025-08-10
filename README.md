## ⚙️ ServoSenseApp (work in progress)

![Build Python](https://github.com/SculptTechProject/Servo-Sens-App/actions/workflows/ci-python.yml/badge.svg?branch=main)
![Build Node](https://github.com/SculptTechProject/Servo-Sens-App/actions/workflows/ci-node.yml/badge.svg?branch=main)
[![Release](https://img.shields.io/github/v/release/SculptTechProject/Servo-Sens-App)](../../releases)
[![License](https://img.shields.io/github/license/SculptTechProject/Servo-Sens-App)](./LICENSE)


**An engineering‑grade platform for real‑time sensor data ingestion, visualization and alerting.**
Backend: **Django + DRF + Channels** (ASGI, Redis). Frontend: **Nuxt 3 (Vue 3)**. Local dev via **Docker Compose**.

> Live WebSockets + one‑click **Quickstart/Seed** — see data flowing in seconds.

---

## 📁 See all docs:

### Click: [docs/](docs/)

## 🧱 Tech Stack

* 🐍 **Django 4 + Django REST Framework + Channels** (ASGI, WebSocket)
* 🐘 **PostgreSQL**, 🧰 **Redis** (Channels layer)
* 🌐 **Nuxt 3 / Vue 3**
* 🐳 **Docker Compose**
* 🧪 **unittest/pytest**, **flake8/black/isort**

---

## 🚀 Features

* 🔐 Token‑based authentication (create user, obtain token, `/me`)
* 🧩 Domain model: **Workspaces → Machines → Sensors → Readings/Events**
* 🧪 **Simulator** that generates live readings and threshold alerts (broadcast via WS)
* 📊 Nuxt dashboard with **real‑time readings**
* ⚡ **Quickstart/Seed** endpoints to spin up a demo workspace instantly

---

## 📦 Repository Layout

```
.
├─ backend/                 # Django project (DRF + Channels)
│  ├─ app/                  # settings, urls, ASGI
│  ├─ core/                 # models & Workspace API
│  ├─ simulator/            # start/stop + WS broadcast services
│  ├─ docker-compose.yml, Dockerfile
│  └─ requirements*.txt
└─ frontend/                # Nuxt 3 app
   ├─ app/ (pages, components, composables)
   └─ nuxt.config.ts
```

---

## 🧑‍🍳 Quickstart (local dev)

### 1) Backend (Django, ASGI)

```bash
cd backend
docker compose up
# Django API:       http://localhost:8000
# API Docs (Swagger): http://localhost:8000/api/docs/
# OpenAPI schema:     http://localhost:8000/api/schema/
```

Useful commands:

```bash
# run tests
docker compose run --rm app python manage.py test

# seed demo user & workspace (optional)
docker compose run --rm app python manage.py seed_demo
# prints: demo credentials and workspace_id

# migrations
docker compose run --rm app python manage.py makemigrations
docker compose run --rm app python manage.py migrate
```

> The stack uses Channels (ASGI) + Redis. The compose is set up to run an ASGI server and a Redis instance.

### 2) Frontend (Nuxt 3)

```bash
cd frontend
npm i
npm run dev
# http://localhost:3000  (or 4000 if 3000 is busy)
```

**Optional `.env` (defaults are already set in `nuxt.config.ts`):**

```env
NUXT_PUBLIC_API_BASE=/api
NUXT_PUBLIC_WS_BASE=/ws
# PORT=3000
```

Nuxt is configured to **proxy** requests to the backend:

```ts
// nuxt.config.ts (excerpt)
nitro: {
  routeRules: {
    '/api/**': { proxy: 'http://127.0.0.1:8000/api/**' },
    '/ws/**' : { proxy: 'http://127.0.0.1:8000/ws/**' }, // WebSockets proxy
  },
},
security: {
  headers: {
    contentSecurityPolicy: {
      'connect-src': ["'self'", 'http:', 'https:', 'ws:', 'wss:'], // relaxed for dev
    },
  },
},
```

This removes CORS pain and allows WS via the same origin (`localhost:3000`).

---

## 🔑 Authentication (API)

```bash
# register
curl -X POST http://localhost:8000/api/user/create/ \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@example.com","password":"demo123","name":"Demo"}'

# obtain token
curl -X POST http://localhost:8000/api/user/token/ \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@example.com","password":"demo123"}'
# -> {"token":"..."}
```

Add the token to subsequent requests:

```
Authorization: Token <YOUR_TOKEN>
```

---

## 🧪 Quick Demo Flow (UI)

1. Open **`/dashboard/workspaces`**.
2. Click **“Create demo workspace”** — it will create & seed a workspace and redirect to its detail view.
3. Click **Start** — if empty, the page seeds sensors and then starts the simulator. Live readings appear immediately.

---

## 🌐 Key Endpoints

**User**

* `POST /api/user/create/` — register
* `POST /api/user/token/` — obtain token
* `GET  /api/user/me/` — current user

**Workspaces**

* `GET  /api/workspaces/` — list (current user)
* `POST /api/workspaces/` — create
* `GET  /api/workspaces/{id}/` — retrieve
* `POST /api/workspaces/quickstart/` — create a demo workspace for the user (creates & seeds)
* `POST /api/workspaces/{id}/seed/` — seed a workspace (adds machine & sensors if empty)

**Simulator**

* `POST /api/sim/start/{id}/`
* `POST /api/sim/stop/{id}/`

**WebSocket (Channels)**

* `ws://localhost:8000/ws/workspaces/{id}/`

  * message samples:

    ```json
    { "type": "reading", "sensor_id": 1, "value": 61.5, "unit": "°C" }
    { "type": "event",   "level": "WARN", "sensor_id": 1, "message": "temperature alert" }
    ```

---

## ✅ Tests & Quality

```bash
# tests
cd backend
docker compose run --rm app python manage.py test

# style/format (if included in image)
docker compose run --rm app flake8
docker compose run --rm app isort --check .
docker compose run --rm app black --check .
```

---

## 🛠️ Troubleshooting

* **CSP blocks WebSocket** (browser shows `NS_ERROR_CONTENT_BLOCKED`):

  * Ensure `connect-src` allows `ws:`/`wss:` in dev (see `nuxt.config.ts`).
  * With proxy (`/ws/**`), the browser connects to `ws://localhost:3000/ws/...` and Nitro forwards to `:8000`.
* **Backend logs: `X of Y channels over capacity in group ws_*`**:

  * The WS client is not actually connected (CSP/CORS/URL). Fix CSP or WS URL.
* **Start clicked, but no data**:

  * Workspace has no sensors. Use **`POST /api/workspaces/{id}/seed/`** or the **Seed + Start** button in the UI.
* **404 for `/ws/...`**:

  * Make sure the backend runs an **ASGI** server (Daphne/Uvicorn) and Channels routing includes the consumer.

---

## 🗺️ Roadmap

* CRUD for machines/sensors (drag‑and‑drop canvas)
* Real‑time charts + history & aggregations
* Multi‑tenant/roles, exports, webhooks

---

## 🚧 Work in progress (pre-alpha). Stable enough to explore; expect breaking changes. Screens below use already simulated data.
<img width="1898" height="966" alt="image" src="https://github.com/user-attachments/assets/5342a3c6-b025-4b2c-902f-2ea81926cd88" />

<img width="1868" height="898" alt="image" src="https://github.com/user-attachments/assets/7f1160cf-8072-42ef-a144-fb94dfa7011a" />

<img width="677" height="404" alt="image" src="https://github.com/user-attachments/assets/c62b9284-9057-4e1a-82c4-2b9a9f5e016a" />

<img width="1865" height="915" alt="image" src="https://github.com/user-attachments/assets/ace13c0e-c846-4aed-93cf-df35634cb82b" />

<img width="531" height="440" alt="image" src="https://github.com/user-attachments/assets/e9470d56-90d8-494c-a621-f036dd1aeec3" />

---

## 📜 License

**MIT** — feel free to use, modify and share. A credit link is appreciated 🙌

# 📁 See all docs: [docs/](docs/)
