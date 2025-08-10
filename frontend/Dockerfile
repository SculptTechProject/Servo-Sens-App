# --- Base ---
FROM node:22-alpine AS base

WORKDIR /app
RUN apk add --no-cache libc6-compat

# --- Deps (cache) ---
FROM base AS deps
COPY package.json package-lock.json* ./
RUN --mount=type=cache,target=/root/.npm npm ci

# --- Dev target ---
FROM base AS dev
ENV NUXT_HOST=0.0.0.0 NUXT_PORT=3000
COPY --from=deps /app/node_modules ./node_modules
COPY . .
EXPOSE 3000
CMD ["npm","run","dev"]

# --- Build (prod) ---
FROM base AS build
ENV NODE_ENV=production
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

# --- Runtime (prod) ---
FROM node:22-alpine AS prod
WORKDIR /app
ENV NODE_ENV=production
# Nuxt Nitro node-server output
ENV PORT=3000 NITRO_PORT=3000 NUXT_HOST=0.0.0.0
COPY --from=build /app/.output ./.output
EXPOSE 3000
CMD ["node",".output/server/index.mjs"]