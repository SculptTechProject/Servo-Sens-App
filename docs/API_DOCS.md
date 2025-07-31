# API Documentation & Automation

This document explains how to **generate**, **publish**, and **consume** API documentation and TypeScript types for the project.

* Backend: Django + DRF + DRF‑Spectacular (OpenAPI)
* Frontend: Nuxt 3 (Vue 3)
* Local dev: Docker Compose

---

## Table of Contents

* [Overview](https://chatgpt.com/c/688b9034-1bc8-832a-b333-1d5803d4e889#overview)
* [Prerequisites](https://chatgpt.com/c/688b9034-1bc8-832a-b333-1d5803d4e889#prerequisites)
* [Local Generation (Schema → Redoc HTML → TS Types)](https://chatgpt.com/c/688b9034-1bc8-832a-b333-1d5803d4e889#local-generation-schema--redoc-html--ts-types)
* [Makefile Targets](https://chatgpt.com/c/688b9034-1bc8-832a-b333-1d5803d4e889#makefile-targets)
* [NPM Scripts Alternative](https://chatgpt.com/c/688b9034-1bc8-832a-b333-1d5803d4e889#npm-scripts-alternative)
* [GitHub Actions: Build & Publish Docs](https://chatgpt.com/c/688b9034-1bc8-832a-b333-1d5803d4e889#github-actions-build--publish-docs)
* [Consuming the Generated Types in Nuxt](https://chatgpt.com/c/688b9034-1bc8-832a-b333-1d5803d4e889#consuming-the-generated-types-in-nuxt)
* [Linking from README](https://chatgpt.com/c/688b9034-1bc8-832a-b333-1d5803d4e889#linking-from-readme)
* [Optional: Redoc via CDN (no CLI)](https://chatgpt.com/c/688b9034-1bc8-832a-b333-1d5803d4e889#optional-redoc-via-cdn-no-cli)
* [Troubleshooting](https://chatgpt.com/c/688b9034-1bc8-832a-b333-1d5803d4e889#troubleshooting)

---

## Overview

We use **DRF‑Spectacular** to produce an **OpenAPI** schema from the Django backend. From this schema we:

1. Build a **static HTML** documentation page with **Redoc** (`docs/api.html`).
2. Generate **TypeScript types** consumed by the Nuxt app (great DX with `api<T>()`).
3. Optionally publish the docs automatically to **GitHub Pages** via a CI workflow.

---

## Prerequisites

* **Docker** (for running the backend command that emits the schema)
* **Node.js** (for CLI tools: `redoc-cli`, `openapi-typescript`)

> You can pin versions in `package.json` devDependencies for reproducible builds.

---

## Local Generation (Schema → Redoc HTML → TS Types)

### 1) Export OpenAPI schema from Django

From the **backend** directory:

```bash
cd backend
# Writes to backend/schema.yaml inside the container workdir (/app)
docker compose run --rm app python manage.py spectacular --file /app/schema.yaml
```

You should now have `backend/schema.yaml` in your repo.

### 2) Build static Redoc HTML

From the **repo root**:

```bash
# One-off install (or add to devDependencies)
npm i -D redoc-cli

# Build static HTML docs
npx redoc-cli build backend/schema.yaml -o docs/api.html
```

`docs/api.html` can be served by GitHub Pages or any static host.

### 3) Generate TypeScript types for the Nuxt app

```bash
npm i -D openapi-typescript
npx openapi-typescript backend/schema.yaml -o frontend/app/types/api.d.ts
```

This gives you rich typings for endpoints, request/response shapes, etc.

---

## Makefile Targets

Create a `Makefile` at the **repo root** for convenience:

```makefile
.PHONY: schema types redoc docs

schema:
	cd backend && docker compose run --rm app python manage.py spectacular --file /app/schema.yaml

types:
	npx openapi-typescript backend/schema.yaml -o frontend/app/types/api.d.ts

redoc:
	npx redoc-cli build backend/schema.yaml -o docs/api.html

docs: schema types redoc
```

Usage:

```bash
make docs   # runs schema + types + redoc
```

---

## NPM Scripts Alternative

If you prefer scripts instead of a Makefile, add to **repo root**`package.json`:

```json
{
  "scripts": {
    "api:schema": "cd backend && docker compose run --rm app python manage.py spectacular --file /app/schema.yaml",
    "api:types": "openapi-typescript backend/schema.yaml -o frontend/app/types/api.d.ts",
    "api:redoc": "redoc-cli build backend/schema.yaml -o docs/api.html",
    "docs": "npm run api:schema && npm run api:types && npm run api:redoc"
  },
  "devDependencies": {
    "openapi-typescript": "^6.7.0",
    "redoc-cli": "^0.13.21"
  }
}
```

Then run:

```bash
npm run docs
```

---

## GitHub Actions: Build & Publish Docs

This workflow generates the schema, builds `docs/api.html`, and publishes the `docs/` folder to **GitHub Pages**.

1. Enable **GitHub Pages**: *Settings → Pages* → Source: **GitHub Actions**.
2. Add `.github/workflows/docs.yml`:

```yaml
name: Build & Publish API Docs

on:
  push:
    branches: [ main ]
  workflow_dispatch:

jobs:
  docs:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      # Use Node for doc tooling
      - uses: actions/setup-node@v4
        with:
          node-version: '20'

      # Generate OpenAPI schema using the backend container
      - name: Generate OpenAPI schema
        working-directory: backend
        run: |
          docker compose up -d db redis || true
          docker compose run --rm app python manage.py spectacular --file /app/schema.yaml
          docker compose down

      - name: Install doc tools
        run: npm i -D redoc-cli openapi-typescript

      - name: Build docs (Redoc) and TS types
        run: |
          npx redoc-cli build backend/schema.yaml -o docs/api.html
          npx openapi-typescript backend/schema.yaml -o frontend/app/types/api.d.ts

      - name: Upload Pages artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: docs

      - name: Deploy to GitHub Pages
        uses: actions/deploy-pages@v4
```

> If your backend container needs environment variables for `manage.py spectacular`, inject them in the workflow step as needed.

---

## Consuming the Generated Types in Nuxt

With `frontend/app/types/api.d.ts` in place, you can type your `useApi` calls.

Example (pseudo‑typed):

```ts
// In a Vue/Nuxt file
import type { paths } from '~/app/types/api';

// GET /api/workspaces/ response type (200)
type WorkspacesList = paths['/api/workspaces/']['get']['responses']['200']['content']['application/json'];

const api = useApi();
const items = ref<WorkspacesList>([]);

onMounted(async () => {
  items.value = await api<WorkspacesList>('/api/workspaces/');
});
```

This pattern gives you autocompletion for fields and compile‑time checks for request/response shapes.

---

## Linking from README

In your `README.md`, add a **Docs** section that points to this file and to the live Redoc page (if publishing to Pages):

```md
## 📚 API Docs
- Developer guide: [docs/API_DOCS.md](docs/API_DOCS.md)
- Redoc (static HTML): [docs/api.html](docs/api.html)
- Live (GitHub Pages): <https://YOUR_GH_USERNAME.github.io/YOUR_REPO/api.html>
```

Replace the URL with your repository’s Pages URL.

---

## Optional: Redoc via CDN (no CLI)

If you prefer not to use `redoc-cli`, you can commit `docs/index.html` using the CDN build:

```html
<!doctype html>
<html>
  <head>
    <meta charset="utf-8"/>
    <title>ServoSenseApp API</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>body{margin:0}</style>
    <script src="https://cdn.redoc.ly/redoc/latest/bundles/redoc.standalone.js"></script>
  </head>
  <body>
    <redoc spec-url="../backend/schema.yaml"></redoc>
  </body>
</html>
```

Then the CI only needs to regenerate `backend/schema.yaml`.

---

## Troubleshooting

* **CSP blocks WebSocket** while browsing docs locally through the app dev server: this docs flow only builds static HTML; serve `docs/` statically (e.g., GitHub Pages) to avoid CSP configured for the app runtime.
* **Schema generation fails**: ensure the Django app starts migrations in the container; if your `manage.py` requires env vars, pass them to `docker compose run` in the workflow.
* **Type generation errors**: validate `backend/schema.yaml` (e.g., `npx @redocly/cli lint backend/schema.yaml`) and update `openapi-typescript`.

---

**License:** MIT
