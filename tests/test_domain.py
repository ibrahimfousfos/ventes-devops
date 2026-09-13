from datetime import date

from ventes_lab.domain import Sale, summarize
import pytest
from pydantic import ValidationError

def test_revenue_multiplies_quantity_by_unit_price():
    sale = Sale(sale_id="demo", shop="paris", day=date(2026, 9, 12), quantity=2, unit_price_cents=1500)
    assert summarize([sale])["revenue_cents"] == 3000

def test_vente_refuse_quantite_negative():
    with pytest.raises(ValidationError):
        Sale(
            sale_id="vente-invalide",
            shop="paris",
            day=date(2026, 9, 13),
            quantity=-1,
            unit_price_cents=1500,
        )