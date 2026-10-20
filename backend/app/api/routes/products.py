from fastapi import APIRouter, Depends, status

from app.api.dependencies import get_catalog_service, get_current_user, require_cafeteria
from app.api.presenters import present_product
from app.api.schemas import ProductCreateRequest, ProductResponse, ProductUpdateRequest
from app.services.catalog_service import CatalogService

router = APIRouter(prefix="/products", tags=["Productos"])


@router.get("", response_model=list[ProductResponse], dependencies=[Depends(get_current_user)])
def list_products(catalog: CatalogService = Depends(get_catalog_service)):
    return [present_product(product) for product in catalog.list_products()]


@router.post(
    "",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_cafeteria)],
)
def create_product(request: ProductCreateRequest, catalog: CatalogService = Depends(get_catalog_service)):
    new_product = catalog.create_product(name=request.name, price=request.price)
    return present_product(new_product)


@router.patch("/{product_id}", response_model=ProductResponse, dependencies=[Depends(require_cafeteria)])
def update_product(
    product_id: int,
    request: ProductUpdateRequest,
    catalog: CatalogService = Depends(get_catalog_service),
):
    """Sirve también para marcar un producto como agotado: `{"is_sold_out": true}`."""
    updated_product = catalog.update_product(
        product_id,
        name=request.name,
        price=request.price,
        is_sold_out=request.is_sold_out,
    )
    return present_product(updated_product)
