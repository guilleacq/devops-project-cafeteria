"""
Chequeo de salud. Lo usan las probes de Kubernetes para saber si el
contenedor está vivo y listo para recibir tráfico.
"""

from fastapi import APIRouter

router = APIRouter(tags=["Salud"])


@router.get("/health")
def health_check() -> dict:
    return {"status": "ok"}
