# Cafetería · Pedidos para el recreo

Una aplicación web para que los alumnos pidan en la cafetería **desde el celular, antes del recreo**, y encuentren su pedido pronto cuando suena el timbre.

Proyecto del Laboratorio de Kubernetes del curso de DevOps (UCU).

---

## El problema

En el recreo se forma una fila larga en la cafetería. El tiempo se va en esperar y muchos alumnos se quedan sin comprar. Si la cafetería supiera de antemano qué va a pedir cada uno, podría tener todo preparado.

## La solución

- **El alumno** entra desde el celular, elige lo que quiere, elige el recreo y confirma. Después puede ver el estado de su pedido: *pendiente*, *listo* o *entregado*.
- **La cafetería** tiene una pantalla con todo lo que tiene que preparar para el próximo recreo: cada pedido con el nombre del alumno y el total de cada producto (por ejemplo, "12 medialunas, 8 cafés"). A medida que avanza, marca los pedidos como listos y después como entregados.

## La regla principal

> Se puede pedir solo hasta **X minutos antes** de cada recreo.

- Si el recreo es a las 09:30 y X es 15, se puede pedir hasta las 09:15. Después de esa hora la app no deja pedir y lo explica con un mensaje claro: *"Ya no se puede pedir para el primer recreo de las 09:30. Los pedidos cerraron a las 09:15."*
- **La cafetería cambia X cuando quiere**, desde su pantalla, y el cambio aplica en el momento. No hace falta que intervenga nadie del equipo técnico.
- La regla la controla el servidor, no la pantalla del celular. Aunque alguien intente saltearse la app, el pedido fuera de hora se rechaza igual.

## Qué incluye

**Lo esencial**
- Catálogo de productos con precio
- Recreos configurados con su hora de inicio
- Pedidos con varios productos
- Estado del pedido visible para el alumno
- Pantalla de la cafetería con lo pendiente del próximo recreo

**Extras**
- Resumen de ventas del día
- Productos agotados (no se pueden pedir mientras estén marcados así)

## Quién usa la app

| Rol | Qué puede hacer |
|---|---|
| Alumno | Ver el catálogo y los recreos, hacer pedidos, consultar sus pedidos |
| Cafetería | Ver los pedidos por recreo, marcarlos como listos o entregados, cambiar X, gestionar productos y recreos, ver el resumen de ventas |

## Cómo está armado (a grandes rasgos)

La app tiene tres partes:

1. **La pantalla** (frontend), lo que se ve en el celular.
2. **El servidor** (backend), que guarda las reglas y responde a la pantalla.
3. **La base de datos**, donde quedan guardados los pedidos aunque se reinicie todo.

Las tres corren en el cluster de Kubernetes del laboratorio. Cada vez que el equipo sube un cambio a la rama principal, una pipeline de Jenkins prueba todo, arma la nueva versión y la publica sola.

El detalle técnico de cada decisión está en [architecture.md](architecture.md).

## Estado actual

| Parte | Estado |
|---|---|
| Servidor (backend) | ✅ Completo y con pruebas. Por ahora guarda los datos en memoria |
| Base de datos | ⏳ Pendiente |
| Pantalla (frontend) | ✅ Completa: alumno (pedir, mis pedidos) y cafetería (tablero, pedidos de hoy, ventas, ajustes) |
| Despliegue en Kubernetes | ⏳ Pendiente |
| Pipeline de Jenkins | ⏳ Pendiente |

## Probarlo en tu computadora

Solo hace falta tener **Docker** instalado.

```bash
docker compose up --build
```

Después abrí **http://localhost:8080** en el navegador (o en el celular, con la IP de tu computadora) y entrá con alguno de los usuarios de prueba.

La documentación del servidor está en **http://localhost:8000/api/docs**: ahí está la lista de todo lo que ofrece y se puede probar cada función desde la misma página.

Usuarios de prueba:

| Rol | Correo | Contraseña |
|---|---|---|
| Alumno | alumno1@cafeteria.test | alumno123 |
| Alumno | alumno2@cafeteria.test | alumno123 |
| Cafetería | cafeteria@cafeteria.test | cafeteria123 |

Para correr las pruebas automáticas:

```bash
docker compose --profile test run --rm backend-tests
```

## Equipo

| Integrante | Responsabilidad |
|---|---|
| _completar_ | Backend y Docker |
| _completar_ | Base de datos |
| _completar_ | Frontend |
| _completar_ | Kubernetes |
| _completar_ | Jenkins |
