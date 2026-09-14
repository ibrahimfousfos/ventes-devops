from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

SHOPS = ("paris", "lyon")


class InvalidSales(ValueError):
    """Le lot reçu ne respecte pas le contrat des ventes."""


class Sale(BaseModel):
    model_config = ConfigDict(extra="forbid")
    sale_id: str = Field(min_length=1, max_length=64)
    shop: Literal["paris", "lyon"]
    day: date
    quantity: int = Field(gt=0, strict=True)
    unit_price_cents: int = Field(ge=0, strict=True)


def validate_batch(payloads: dict, day: date) -> list[Sale]:
    if set(payloads) != set(SHOPS):
        raise InvalidSales("Le lot doit contenir les deux boutiques")
    sales = []
    seen = set()
    for shop in SHOPS:
        rows = payloads[shop]
        if not isinstance(rows, list):
            raise InvalidSales("Une source doit renvoyer une liste de ventes")
        for row in rows:
            try:
                sale = Sale.model_validate(row)
            except ValueError as exc:
                raise InvalidSales("Une vente est invalide") from exc
            if sale.shop != shop or sale.day != day:
                raise InvalidSales("Boutique ou date incohérente")
            key = (sale.shop, sale.sale_id)
            if key in seen:
                raise InvalidSales("Identifiant de vente répété dans le lot")
            seen.add(key)
            sales.append(sale)
    return sales


def summarize(sales: list[Sale]) -> dict:
    return {
        "sales_count": len(sales),
        "total_quantity": sum(s.quantity for s in sales),
        "revenue_cents": sum(s.quantity * s.unit_price_cents for s in sales),
        "currency": "EUR",
    }

