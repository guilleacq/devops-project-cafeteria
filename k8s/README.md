# Despliegue en Kubernetes

La app corre en el cluster del laboratorio, namespace `alumno-team4`, y se
entra por **https://pedidos.reto-ucu.net**.

| Archivo | Qué crea | Equivale en docker-compose a |
|---|---|---|
| `db.yaml` | PostgreSQL + su disco + el Service `db` | servicio `db` y volumen `postgres-data` |
| `backend.yaml` | La API + sus variables + el Service `backend-svc` | servicio `backend` |
| `frontend.yaml` | nginx con la app + el Service `frontend-svc` | servicio `frontend` |
| `ingress.yaml` | La URL pública (un `ApisixRoute`): `/api` → backend, `/` → frontend | `ports:` |
| `jenkins.yaml` | Jenkins + su disco, en https://jenkins-pedidos.reto-ucu.net | — |

La imagen de Jenkins (`jenkins/Dockerfile`) se construye y se sube una vez a mano:

```bash
docker buildx build --platform linux/amd64 -t guilleacq/cafeteria-jenkins:v1 --push ./jenkins
```

## Antes de empezar

Usar el kubeconfig del equipo:

```bash
export KUBECONFIG=~/Downloads/team4.kubeconfig
```

## Primera vez: secretos y esquema de la base

Estas dos cosas se crean con un comando y **no** se guardan en el repo.

**1. El Secret** con las contraseñas. Elegir una contraseña para la base y
usarla en los dos lugares donde dice `CAMBIAR`:

```bash
kubectl create secret generic cafeteria-secret \
  --from-literal=POSTGRES_PASSWORD='CAMBIAR' \
  --from-literal=DATABASE_URL='postgresql://cafeteria:CAMBIAR@db:5432/cafeteria' \
  --from-literal=JWT_SECRET="$(openssl rand -hex 32)"
```

**2. El ConfigMap** con `db/init.sql`, que crea las tablas la primera vez:

```bash
kubectl create configmap db-init --from-file=db/init.sql
```

## Desplegar

```bash
kubectl apply -f k8s/
```

Ver cómo va (todos tienen que llegar a `Running` y `1/1`):

```bash
kubectl get pods
```

Es normal que el backend se reinicie una o dos veces al principio, mientras
Postgres termina de arrancar.

## Comandos útiles

```bash
kubectl logs deployment/backend          # ver los logs del backend
kubectl describe pod <nombre-del-pod>    # ver por qué un pod no arranca
kubectl rollout restart deployment/backend
```
