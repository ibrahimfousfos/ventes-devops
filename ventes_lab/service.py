import asyncio
from datetime import date

from ventes_lab.collector import fetch_sales
from ventes_lab.config import Settings
from ventes_lab.domain import validate_batch
from ventes_lab.storage import Storage


def import_sales(day: date, settings: Settings, storage: Storage) -> dict:
    payloads = asyncio.run(fetch_sales(settings.source_base_url, day, settings.request_timeout_seconds))
    sales = validate_batch(payloads, day)
    inserted = storage.save(sales)
    return {"day": day.isoformat(), "received": len(sales), "inserted": inserted, "skipped": len(sales) - inserted}

