-- ---------------------------------------------------------------------------
-- Base de datos de la cafetería: creación del esquema.
--
-- Este archivo lo corre la imagen de PostgreSQL sola, al iniciar con un
-- volumen vacío (docker-entrypoint-initdb.d, ver docker-compose.yml).
-- Si los datos ya existen, no se vuelve a ejecutar: para reiniciar la base
-- desde cero hay que borrar el volumen (`docker compose down -v`).
--
-- Los nombres de las tablas son los acordados en el equipo (español) y las
-- columnas usan los mismos nombres que los atributos de las entidades de
-- app/domain/models.py, así el mapeo en app/repositories/postgres.py es
-- directo.
-- ---------------------------------------------------------------------------


-- Usuarios: alumnos y personal de la cafetería. No hay registro desde la
-- app; se cargan con los datos de ejemplo (repositories/seed_data.py).

CREATE TABLE IF NOT EXISTS usuarios (
    id             SERIAL PRIMARY KEY,
    full_name      TEXT NOT NULL,
    email          TEXT NOT NULL,
    password_hash  TEXT NOT NULL,
    role           TEXT NOT NULL CHECK (role IN ('student', 'cafeteria'))
);

-- Un solo correo sin importar mayúsculas y minúsculas.
CREATE UNIQUE INDEX IF NOT EXISTS usuarios_email_lower ON usuarios (lower(email));


-- Catálogo. Los precios son pesos uruguayos enteros, sin decimales.

CREATE TABLE IF NOT EXISTS productos (
    id           SERIAL PRIMARY KEY,
    name         TEXT NOT NULL,
    price        INTEGER NOT NULL CHECK (price > 0),
    is_sold_out  BOOLEAN NOT NULL DEFAULT FALSE
);


-- Recreos: uno por día a la misma hora. `start_time` es la hora de reloj
-- del liceo, SIN zona horaria (la zona la aporta APP_TIMEZONE al calcular).

CREATE TABLE IF NOT EXISTS recreos (
    id                SERIAL PRIMARY KEY,
    name              TEXT NOT NULL,
    start_time        TIME NOT NULL,
    duration_minutes  INTEGER NOT NULL DEFAULT 15 CHECK (duration_minutes > 0)
);


-- Configuración de la aplicación: pares clave → valor guardados como texto.
-- Acá vive X (order_cutoff_minutes), que la cafetería cambia sin desplegar.

CREATE TABLE IF NOT EXISTS configuracion (
    clave  TEXT PRIMARY KEY,
    valor  TEXT NOT NULL
);


-- Pedidos. `created_at` es un momento exacto CON zona horaria: tiene que
-- ser TIMESTAMPTZ, si no se pierde el desfase y cambia de significado.

CREATE TABLE IF NOT EXISTS pedidos (
    id            SERIAL PRIMARY KEY,
    student_id    INTEGER NOT NULL REFERENCES usuarios (id),
    recess_id     INTEGER NOT NULL REFERENCES recreos (id),
    service_date  DATE NOT NULL,
    created_at    TIMESTAMPTZ NOT NULL,
    status        TEXT NOT NULL CHECK (status IN ('pending', 'ready', 'delivered'))
);

CREATE INDEX IF NOT EXISTS pedidos_por_dia_y_recreo ON pedidos (service_date, recess_id);
CREATE INDEX IF NOT EXISTS pedidos_por_alumno       ON pedidos (student_id, created_at DESC);


-- Líneas del pedido. Guardan una copia del nombre y del precio en el
-- momento de pedir: si después cambia el precio, el pedido histórico y el
-- resumen de ventas siguen mostrando lo que se cobró realmente.

CREATE TABLE IF NOT EXISTS pedido_items (
    id            SERIAL PRIMARY KEY,
    pedido_id     INTEGER NOT NULL REFERENCES pedidos (id) ON DELETE CASCADE,
    product_id    INTEGER NOT NULL REFERENCES productos (id),
    product_name  TEXT NOT NULL,
    quantity      INTEGER NOT NULL CHECK (quantity > 0),
    unit_price    INTEGER NOT NULL CHECK (unit_price > 0)
);

CREATE INDEX IF NOT EXISTS pedido_items_por_pedido ON pedido_items (pedido_id);
