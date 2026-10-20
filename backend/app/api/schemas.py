"""
Formato de los datos que entran y salen de la API (JSON).

Están separados de las entidades del dominio a propósito: la API puede
mostrar los datos de otra forma (por ejemplo, sin la contraseña del
usuario) sin cambiar el dominio.

Horas y fechas:
- `start_time` es la hora de reloj del liceo, por ejemplo "09:30:00".
- Los campos que terminan en `_at` son momentos exactos con zona horaria,
  por ejemplo "2026-10-20T09:15:00-03:00".
"""

from datetime import date, datetime, time

from pydantic import BaseModel, Field

from app.domain.models import OrderStatus, Role


# ---------------------------------------------------------------------------
# Autenticación
# ---------------------------------------------------------------------------

class LoginRequest(BaseModel):
    email: str = Field(examples=["alumno1@cafeteria.test"])
    password: str = Field(examples=["alumno123"])


class UserResponse(BaseModel):
    id: int
    full_name: str
    email: str
    role: Role


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ---------------------------------------------------------------------------
# Productos
# ---------------------------------------------------------------------------

class ProductResponse(BaseModel):
    id: int
    name: str
    price: int = Field(description="Precio en pesos uruguayos, sin decimales.")
    is_sold_out: bool


class ProductCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    price: int = Field(gt=0)


class ProductUpdateRequest(BaseModel):
    """Todos los campos son opcionales: solo se cambia lo que se manda."""

    name: str | None = Field(default=None, min_length=1, max_length=100)
    price: int | None = Field(default=None, gt=0)
    is_sold_out: bool | None = None


# ---------------------------------------------------------------------------
# Recreos
# ---------------------------------------------------------------------------

class RecessResponse(BaseModel):
    id: int
    name: str
    start_time: time
    duration_minutes: int


class RecessCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    start_time: time = Field(examples=["10:00"])
    duration_minutes: int = Field(default=15, gt=0, le=240)


class RecessUpdateRequest(BaseModel):
    """Todos los campos son opcionales: solo se cambia lo que se manda."""

    name: str | None = Field(default=None, min_length=1, max_length=100)
    start_time: time | None = None
    duration_minutes: int | None = Field(default=None, gt=0, le=240)


class RecessTodayResponse(BaseModel):
    """Un recreo de hoy, con la información para saber si todavía se puede pedir."""

    id: int
    name: str
    start_time: time
    duration_minutes: int
    service_date: date
    starts_at: datetime
    ends_at: datetime
    ordering_closes_at: datetime
    is_accepting_orders: bool


# ---------------------------------------------------------------------------
# Pedidos
# ---------------------------------------------------------------------------

class OrderItemRequest(BaseModel):
    product_id: int
    quantity: int = Field(gt=0, examples=[2])


class OrderCreateRequest(BaseModel):
    recess_id: int
    items: list[OrderItemRequest] = Field(min_length=1)


class OrderItemResponse(BaseModel):
    product_id: int
    product_name: str
    quantity: int
    unit_price: int
    subtotal: int


class OrderResponse(BaseModel):
    id: int
    status: OrderStatus
    recess_id: int
    recess_name: str
    recess_start_time: time
    service_date: date
    created_at: datetime
    items: list[OrderItemResponse]
    total: int


class OrderStatusUpdateRequest(BaseModel):
    status: OrderStatus = Field(examples=["ready"])


# ---------------------------------------------------------------------------
# Cafetería
# ---------------------------------------------------------------------------

class CafeteriaOrderResponse(OrderResponse):
    student_name: str


class ProductQuantityResponse(BaseModel):
    product_name: str
    quantity: int


class NextRecessBoardResponse(BaseModel):
    recess: RecessTodayResponse | None
    orders: list[CafeteriaOrderResponse]
    products_to_prepare: list[ProductQuantityResponse]
    message: str | None = None


class RecessOrdersResponse(BaseModel):
    recess: RecessTodayResponse
    orders: list[CafeteriaOrderResponse]


class ProductSalesResponse(BaseModel):
    product_name: str
    units_sold: int
    revenue: int


class DailySalesSummaryResponse(BaseModel):
    service_date: date
    total_orders: int
    delivered_orders: int
    total_revenue: int
    products: list[ProductSalesResponse]


# ---------------------------------------------------------------------------
# Configuración
# ---------------------------------------------------------------------------

class ConfigurationResponse(BaseModel):
    order_cutoff_minutes: int = Field(description="Minutos antes del recreo en que se cierran los pedidos (X).")


class OrderCutoffUpdateRequest(BaseModel):
    order_cutoff_minutes: int = Field(ge=0, le=240, examples=[15])


# ---------------------------------------------------------------------------
# Errores
# ---------------------------------------------------------------------------

class ErrorResponse(BaseModel):
    code: str = Field(examples=["ORDERING_CLOSED"])
    detail: str = Field(examples=["Ya no se puede pedir para el primer recreo de las 09:30."])
