"""
Repositorios con PostgreSQL.

Implementa exactamente los mismos contratos que `interfaces.py`, con
psycopg 3 y un pool de conexiones compartido por todos los repositorios.
Como los servicios solo conocen las interfaces, ni las rutas ni las
reglas de negocio cambian: el resto de la aplicación anda igual.

Cada operación corre en su propia transacción. En particular,
`OrderRepository.add` guarda el pedido y sus líneas juntos: o se guarda
todo, o no se guarda nada.

Las tablas las crea `db/init.sql` (ver `docker-compose.yml`).
"""

import atexit
from collections import defaultdict
from contextlib import contextmanager
from datetime import date

from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

from app.domain.models import Order, OrderItem, OrderStatus, Product, Recess, Role, User
from app.repositories.interfaces import (
    OrderRepository,
    ProductRepository,
    RecessRepository,
    Repositories,
    SettingsRepository,
    UserRepository,
)


# ---------------------------------------------------------------------------
# Conexión
# ---------------------------------------------------------------------------

@contextmanager
def _transaction(pool: ConnectionPool):
    """
    Una conexión del pool con transacción abierta y filas con nombre.

    Commitea al terminar bien; si algo falla, hace rollback y propaga el
    error. Las filas llegan como diccionarios (`dict_row`), así que leer
    una columna es `row["price"]` en vez de contar posiciones.
    """
    with pool.connection() as connection:
        connection.row_factory = dict_row
        with connection.transaction():
            yield connection


def build_postgres_repositories(database_url: str, app_timezone: str = "America/Montevideo") -> Repositories:
    """
    Crea los repositorios sobre PostgreSQL y comparte un solo pool entre
    todos ellos. `app_timezone` se fija en la sesión: así los `timestamptz`
    (`created_at`) se devuelven en la zona del liceo y la API responde con
    el desfase correcto, igual que con los repositorios en memoria.
    """
    if not database_url:
        raise ValueError("Falta DATABASE_URL: sin cadena de conexión no se puede usar REPOSITORY_BACKEND=postgres.")

    pool = ConnectionPool(
        conninfo=database_url,
        min_size=1,
        max_size=10,
        kwargs={"options": f"-c TimeZone={app_timezone}"},
    )
    atexit.register(_close_pool, pool)

    return Repositories(
        users=PostgresUserRepository(pool),
        products=PostgresProductRepository(pool),
        recesses=PostgresRecessRepository(pool),
        orders=PostgresOrderRepository(pool),
        settings=PostgresSettingsRepository(pool),
    )


def _close_pool(pool: ConnectionPool) -> None:
    """Al terminar el proceso devuelve las conexiones limpias al servidor."""
    pool.close()


# ---------------------------------------------------------------------------
# Conversión de filas → entidades
# ---------------------------------------------------------------------------

def _user_from_row(row: dict) -> User:
    return User(
        id=row["id"],
        full_name=row["full_name"],
        email=row["email"],
        password_hash=row["password_hash"],
        role=Role(row["role"]),
    )


def _product_from_row(row: dict) -> Product:
    return Product(
        id=row["id"],
        name=row["name"],
        price=row["price"],
        is_sold_out=row["is_sold_out"],
    )


def _recess_from_row(row: dict) -> Recess:
    return Recess(
        id=row["id"],
        name=row["name"],
        start_time=row["start_time"],
        duration_minutes=row["duration_minutes"],
    )


def _order_from_row(row: dict) -> Order:
    return Order(
        id=row["id"],
        student_id=row["student_id"],
        recess_id=row["recess_id"],
        service_date=row["service_date"],
        created_at=row["created_at"],
        status=OrderStatus(row["status"]),
    )


def _order_item_from_row(row: dict) -> OrderItem:
    return OrderItem(
        product_id=row["product_id"],
        product_name=row["product_name"],
        quantity=row["quantity"],
        unit_price=row["unit_price"],
    )


def _load_orders(connection, query: str, params: tuple) -> list[Order]:
    """Pedidos de una consulta, cada uno con sus líneas ya cargadas."""
    rows = connection.execute(query, params).fetchall()

    if not rows:
        return []

    items_by_order = _items_of_orders(connection, [row["id"] for row in rows])

    orders = []
    for row in rows:
        order = _order_from_row(row)
        order.items = items_by_order.get(order.id, [])
        orders.append(order)

    return orders


def _items_of_orders(connection, order_ids: list[int]) -> dict[int, list[OrderItem]]:
    rows = connection.execute(
        "SELECT * FROM pedido_items WHERE pedido_id = ANY(%s) ORDER BY id",
        (order_ids,),
    ).fetchall()

    items_by_order: dict[int, list[OrderItem]] = defaultdict(list)

    for row in rows:
        items_by_order[row["pedido_id"]].append(_order_item_from_row(row))

    return items_by_order


def _ensure_row_exists(cursor, entity_id: int | None) -> None:
    if cursor.rowcount == 0:
        raise KeyError(f"No existe una entidad con id {entity_id}.")


# ---------------------------------------------------------------------------
# Usuarios
# ---------------------------------------------------------------------------

class PostgresUserRepository(UserRepository):

    def __init__(self, pool: ConnectionPool):
        self._pool = pool

    def add(self, user: User) -> User:
        with _transaction(self._pool) as connection:
            row = connection.execute(
                """
                INSERT INTO usuarios (full_name, email, password_hash, role)
                VALUES (%s, %s, %s, %s)
                RETURNING id
                """,
                (user.full_name, user.email, user.password_hash, user.role.value),
            ).fetchone()

        user.id = row["id"]
        return user

    def get_by_id(self, user_id: int) -> User | None:
        with _transaction(self._pool) as connection:
            row = connection.execute("SELECT * FROM usuarios WHERE id = %s", (user_id,)).fetchone()

        return _user_from_row(row) if row else None

    def get_by_email(self, email: str) -> User | None:
        with _transaction(self._pool) as connection:
            row = connection.execute(
                "SELECT * FROM usuarios WHERE lower(email) = lower(%s)",
                (email.strip(),),
            ).fetchone()

        return _user_from_row(row) if row else None


# ---------------------------------------------------------------------------
# Productos
# ---------------------------------------------------------------------------

class PostgresProductRepository(ProductRepository):

    def __init__(self, pool: ConnectionPool):
        self._pool = pool

    def add(self, product: Product) -> Product:
        with _transaction(self._pool) as connection:
            row = connection.execute(
                """
                INSERT INTO productos (name, price, is_sold_out)
                VALUES (%s, %s, %s)
                RETURNING id
                """,
                (product.name, product.price, product.is_sold_out),
            ).fetchone()

        product.id = row["id"]
        return product

    def update(self, product: Product) -> Product:
        with _transaction(self._pool) as connection:
            cursor = connection.execute(
                """
                UPDATE productos
                SET name = %s, price = %s, is_sold_out = %s
                WHERE id = %s
                """,
                (product.name, product.price, product.is_sold_out, product.id),
            )
            _ensure_row_exists(cursor, product.id)

        return product

    def get_by_id(self, product_id: int) -> Product | None:
        with _transaction(self._pool) as connection:
            row = connection.execute("SELECT * FROM productos WHERE id = %s", (product_id,)).fetchone()

        return _product_from_row(row) if row else None

    def list_all(self) -> list[Product]:
        with _transaction(self._pool) as connection:
            rows = connection.execute("SELECT * FROM productos ORDER BY name").fetchall()

        return [_product_from_row(row) for row in rows]


# ---------------------------------------------------------------------------
# Recreos
# ---------------------------------------------------------------------------

class PostgresRecessRepository(RecessRepository):

    def __init__(self, pool: ConnectionPool):
        self._pool = pool

    def add(self, recess: Recess) -> Recess:
        with _transaction(self._pool) as connection:
            row = connection.execute(
                """
                INSERT INTO recreos (name, start_time, duration_minutes)
                VALUES (%s, %s, %s)
                RETURNING id
                """,
                (recess.name, recess.start_time, recess.duration_minutes),
            ).fetchone()

        recess.id = row["id"]
        return recess

    def update(self, recess: Recess) -> Recess:
        with _transaction(self._pool) as connection:
            cursor = connection.execute(
                """
                UPDATE recreos
                SET name = %s, start_time = %s, duration_minutes = %s
                WHERE id = %s
                """,
                (recess.name, recess.start_time, recess.duration_minutes, recess.id),
            )
            _ensure_row_exists(cursor, recess.id)

        return recess

    def get_by_id(self, recess_id: int) -> Recess | None:
        with _transaction(self._pool) as connection:
            row = connection.execute("SELECT * FROM recreos WHERE id = %s", (recess_id,)).fetchone()

        return _recess_from_row(row) if row else None

    def list_all(self) -> list[Recess]:
        with _transaction(self._pool) as connection:
            rows = connection.execute("SELECT * FROM recreos ORDER BY start_time").fetchall()

        return [_recess_from_row(row) for row in rows]


# ---------------------------------------------------------------------------
# Pedidos
# ---------------------------------------------------------------------------

class PostgresOrderRepository(OrderRepository):

    def __init__(self, pool: ConnectionPool):
        self._pool = pool

    def add(self, order: Order) -> Order:
        with _transaction(self._pool) as connection:
            row = connection.execute(
                """
                INSERT INTO pedidos (student_id, recess_id, service_date, created_at, status)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
                """,
                (
                    order.student_id,
                    order.recess_id,
                    order.service_date,
                    order.created_at,
                    order.status.value,
                ),
            ).fetchone()

            order.id = row["id"]

            for item in order.items:
                connection.execute(
                    """
                    INSERT INTO pedido_items (pedido_id, product_id, product_name, quantity, unit_price)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (order.id, item.product_id, item.product_name, item.quantity, item.unit_price),
                )

        return order

    def update(self, order: Order) -> Order:
        with _transaction(self._pool) as connection:
            cursor = connection.execute(
                "UPDATE pedidos SET status = %s WHERE id = %s",
                (order.status.value, order.id),
            )
            _ensure_row_exists(cursor, order.id)

        return order

    def get_by_id(self, order_id: int) -> Order | None:
        with _transaction(self._pool) as connection:
            row = connection.execute("SELECT * FROM pedidos WHERE id = %s", (order_id,)).fetchone()

            if row is None:
                return None

            order = _order_from_row(row)
            order.items = _items_of_orders(connection, [order.id]).get(order.id, [])

        return order

    def list_by_student(self, student_id: int) -> list[Order]:
        with _transaction(self._pool) as connection:
            return _load_orders(
                connection,
                """
                SELECT * FROM pedidos
                WHERE student_id = %s
                ORDER BY created_at DESC, id DESC
                """,
                (student_id,),
            )

    def list_by_service_date(self, service_date: date) -> list[Order]:
        with _transaction(self._pool) as connection:
            return _load_orders(
                connection,
                """
                SELECT * FROM pedidos
                WHERE service_date = %s
                ORDER BY created_at ASC, id ASC
                """,
                (service_date,),
            )


# ---------------------------------------------------------------------------
# Configuración (clave → valor)
# ---------------------------------------------------------------------------

class PostgresSettingsRepository(SettingsRepository):

    def __init__(self, pool: ConnectionPool):
        self._pool = pool

    def get_value(self, key: str) -> str | None:
        with _transaction(self._pool) as connection:
            row = connection.execute(
                "SELECT valor FROM configuracion WHERE clave = %s",
                (key,),
            ).fetchone()

        return row["valor"] if row else None

    def set_value(self, key: str, value: str) -> None:
        with _transaction(self._pool) as connection:
            connection.execute(
                """
                INSERT INTO configuracion (clave, valor)
                VALUES (%s, %s)
                ON CONFLICT (clave) DO UPDATE SET valor = EXCLUDED.valor
                """,
                (key, value),
            )
