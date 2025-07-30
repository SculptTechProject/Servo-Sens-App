# ServoSenseApp – TODO Plan

## ✅ MVP (first working release)

### Frontend (Nuxt)

- [ ] **Switch app language to English** (copy PL → EN).
- [ ] Prepare i18n (nuxt-i18n) — `en` default, `pl` optional.
- [ ] **Workspaces list**: “Create demo workspace” (quickstart) + “Create new”.
- [ ] **Workspace detail**: auto **Seed + Start** if empty.
- [ ] WS reconnect (exponential backoff) + toast on error.
- [ ] Simple **Readings** list + **Events** list.
- [ ] Auth guard: toggle Dashboard/Login/Logout by token.
- [ ] Add `.env.example` (API/WS base, PORT) and reference it in README.

### Backend (Django)

- [ ] Endpoints: `workspaces/`, `workspaces/{id}/`, `workspaces/seed/`, `workspaces/quickstart/`.
- [ ] Simulator start/stop + WS broadcast (Channels/Redis).
- [ ] Workspace serializer: include `machines_count`, `sensors_count`.
- [ ] Management command `seed_demo` (demo user + workspace + sensors).
- [ ] DRF Spectacular summaries/descriptions for new endpoints.

### Docs

- [ ] README (EN): dev quickstart (Docker), quick demo flow, WS info, **Redis** mention.
- [ ] GIF/screenshot of live readings.
- [ ] GitHub topics + pin **ServoSenseApp**.

---

## 🧪 Tests & Quality

- [ ] BE tests: workspaces (list/detail/seed/quickstart), simulator start/stop.
- [ ] BE test: “reading saved” after simulator starts.
- [ ] Lint/format: flake8, black, isort (+ pre-commit).
- [ ] FE smoke tests (pages render) + basic composables (useApi/useWs).

---

## 🐳 DevOps (dev & prod)

- [ ] Nuxt proxy (`routeRules`) for `/api/**` and `/ws/**` (+ dev CSP `connect-src` allow http/ws).
- [ ] FE Docker (prod build + serve via preview or Nginx).
- [ ] ASGI prod (Daphne/Uvicorn) + `REDIS_URL` + `ALLOWED_HOSTS`.
- [ ] Compose `prod` profile (app + db + redis + nginx).
- [ ] Healthchecks (DB/Redis) + basic logging.

---

## 🔐 Security

- [ ] Tight CSP/CORS for production domains.
- [ ] DRF throttling/rate-limit for auth/token.
- [ ] Secrets via `.env` (no keys in repo).

---

## 📊 UX – next step

- [ ] Live chart (`uPlot`/`Chart.js`) — value + threshold.
- [ ] Filters: by sensor / last N minutes.
- [ ] History endpoint: `GET /api/readings?sensor_id=&limit=&since=`.

---

## 🧭 Backlog / nice-to-have

- [ ] CRUD for Machines/Sensors (**drag & drop canvas**).
- [ ] Aggregations: min/max/avg per 1m/5m/1h.
- [ ] Webhook/Email on alerts.
- [ ] Roles/teams (multi-tenant).
- [ ] Export CSV/Parquet.

---

## 🧲 Drag & Drop – detailed plan

### Backend (Django/DRF)

- [ ] **CRUD endpoints**
  - `GET/POST /api/workspaces/{id}/machines/`
  - `PATCH/DELETE /api/machines/{id}/`
  - `GET/POST /api/machines/{id}/sensors/`
  - `PATCH/DELETE /api/sensors/{id}/`
- [ ] **Positions & layout**
  - Keep `Machine.x/y`; optionally add `width`, `height`, `icon`, `color`.
  - **Bulk layout save**: `POST /api/workspaces/{id}/layout/` with list of `{id,x,y}`.
- [ ] **Validation**
  - Sensor must belong to a machine **in the same workspace**.
  - `Sensor.kind` limited to choices; `threshold` optional.
- [ ] **WS broadcast (topology)**
  - Broadcast to `ws_{workspace}` on changes:
    - `{"type":"topology","subtype":"machine_added|updated|removed","machine":{...}}`
    - `{"type":"topology","subtype":"sensor_added|updated|removed","sensor":{...}}`
  - Keep existing `reading` / `event` messages as is.
- [ ] **Permissions**
  - `IsAuthenticated`; restrict to workspace owner.

### Frontend (Nuxt)

- [ ] **Canvas component**
  - `components/canvas/WorkspaceCanvas.vue` (use **vue-konva** or **interact.js**).
  - Render machine “cards” (icon/title) + sensor “pills” on machine edge.
- [ ] **Drag & drop**
  - From **palette** (machine types) → drop on canvas → `POST /machines`.
  - Drag existing machine → debounce
