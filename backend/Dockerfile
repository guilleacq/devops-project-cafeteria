# ---------------------------------------------------------------------------
# Imagen del backend. Tiene tres etapas:
#
#   base     → Python + dependencias de la aplicación
#   test     → base + dependencias de prueba; corre pytest   (docker build --target test)
#   runtime  → la imagen que se despliega                    (etapa por defecto)
# ---------------------------------------------------------------------------

FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    TZ=America/Montevideo

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt


# ---------------------------------------------------------------------------
FROM base AS test

COPY requirements-dev.txt .
RUN pip install -r requirements-dev.txt

COPY app ./app
COPY tests ./tests

CMD ["pytest", "-v"]


# ---------------------------------------------------------------------------
FROM base AS runtime

# Usuario sin privilegios: el contenedor nunca corre como root.
RUN useradd --create-home --uid 10001 appuser

COPY app ./app

USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
