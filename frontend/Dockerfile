# ---------------------------------------------------------------------------
# Imagen del frontend. Tiene dos etapas:
#
#   build    → Node compila la app (si no compila, la pipeline se corta acá)
#   runtime  → nginx sirve los archivos estáticos   (etapa por defecto)
# ---------------------------------------------------------------------------

FROM node:20-alpine AS build

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .
RUN npm run build


# ---------------------------------------------------------------------------
FROM nginxinc/nginx-unprivileged:1.27-alpine AS runtime

# A dónde manda nginx las llamadas a /api. En el cluster, el nombre del
# Service del backend; en docker compose, el servicio "backend".
ENV BACKEND_URL=http://backend:8000

# La imagen oficial pasa los archivos de templates/ por envsubst al arrancar.
COPY nginx.conf.template /etc/nginx/templates/default.conf.template
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 8080
