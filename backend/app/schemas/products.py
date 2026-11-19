from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class ProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    sku: str
    slug: str
    name: str
    category: str
    description: str
    price: Decimal
    compare_at_price: Decimal | None
    stock_qty: int
    image_url: str
    badge: str | None
    featured: bool


class ProductPage(BaseModel):
    items: list[ProductOut]
    total: int
    page: int
    page_size: int


class OrderLineIn(BaseModel):
    product_id: UUID
    quantity: int = Field(ge=1, le=20)


class CreateOrderRequest(BaseModel):
    items: list[OrderLineIn] = Field(min_length=1, max_length=30)
    shipping_name: str = Field(min_length=2, max_length=160)
    shipping_phone: str = Field(min_length=8, max_length=32)
    shipping_address: str = Field(min_length=8, max_length=1000)
    shipping_city: str = Field(min_length=2, max_length=100)


class OrderOut(BaseModel):
    id: str
    order_number: str
    status: str
    payment_status: str
    subtotal: Decimal
    shipping_fee: Decimal
    total: Decimal
    currency: str
    created_at: str
