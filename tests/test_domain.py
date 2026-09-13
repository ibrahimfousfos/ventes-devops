from datetime import date

from ventes_lab.domain import Sale, summarize


def test_revenue_multiplies_quantity_by_unit_price():
    sale = Sale(sale_id="demo", shop="paris", day=date(2026, 9, 12), quantity=2, unit_price_cents=1500)
    assert summarize([sale])["revenue_cents"] == 3000

