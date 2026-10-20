"""
Catálogo: productos y recreos.

Todos pueden consultarlo; solo la cafetería lo modifica
(eso lo controla la capa de API).
"""

from datetime import time

from app.domain.errors import InvalidDataError, NotFoundError
from app.domain.models import Product, Recess
from app.repositories.interfaces import ProductRepository, RecessRepository


class CatalogService:

    def __init__(self, product_repository: ProductRepository, recess_repository: RecessRepository):
        self.product_repository = product_repository
        self.recess_repository = recess_repository

    # -----------------------------------------------------------------------
    # Productos
    # -----------------------------------------------------------------------

    def list_products(self) -> list[Product]:
        return self.product_repository.list_all()

    def get_product(self, product_id: int) -> Product:
        product = self.product_repository.get_by_id(product_id)

        if product is None:
            raise NotFoundError(f"No existe el producto {product_id}.")

        return product

    def create_product(self, name: str, price: int) -> Product:
        self._validate_price(price)

        new_product = Product(id=None, name=name.strip(), price=price)
        return self.product_repository.add(new_product)

    def update_product(
        self,
        product_id: int,
        name: str | None = None,
        price: int | None = None,
        is_sold_out: bool | None = None,
    ) -> Product:
        """Actualiza solo los campos que vienen con valor."""
        product = self.get_product(product_id)

        if name is not None:
            product.name = name.strip()

        if price is not None:
            self._validate_price(price)
            product.price = price

        if is_sold_out is not None:
            product.is_sold_out = is_sold_out

        return self.product_repository.update(product)

    @staticmethod
    def _validate_price(price: int) -> None:
        if price <= 0:
            raise InvalidDataError("El precio tiene que ser mayor que cero.")

    # -----------------------------------------------------------------------
    # Recreos
    # -----------------------------------------------------------------------

    def list_recesses(self) -> list[Recess]:
        return self.recess_repository.list_all()

    def recesses_by_id(self) -> dict[int, Recess]:
        return {recess.id: recess for recess in self.recess_repository.list_all()}

    def get_recess(self, recess_id: int) -> Recess:
        recess = self.recess_repository.get_by_id(recess_id)

        if recess is None:
            raise NotFoundError(f"No existe el recreo {recess_id}.")

        return recess

    def create_recess(self, name: str, start_time: time, duration_minutes: int) -> Recess:
        self._validate_duration(duration_minutes)

        new_recess = Recess(id=None, name=name.strip(), start_time=start_time, duration_minutes=duration_minutes)
        return self.recess_repository.add(new_recess)

    def update_recess(
        self,
        recess_id: int,
        name: str | None = None,
        start_time: time | None = None,
        duration_minutes: int | None = None,
    ) -> Recess:
        """Actualiza solo los campos que vienen con valor."""
        recess = self.get_recess(recess_id)

        if name is not None:
            recess.name = name.strip()

        if start_time is not None:
            recess.start_time = start_time

        if duration_minutes is not None:
            self._validate_duration(duration_minutes)
            recess.duration_minutes = duration_minutes

        return self.recess_repository.update(recess)

    @staticmethod
    def _validate_duration(duration_minutes: int) -> None:
        if duration_minutes <= 0:
            raise InvalidDataError("La duración del recreo tiene que ser mayor que cero.")
