import asyncio
import os
from datetime import date
from typing import Literal

from fastapi import FastAPI, HTTPException

app = FastAPI(title="Source de ventes fictives")
ROWS = {
    "paris": [("P001", 2, 1500), ("P002", 1, 4000)],
    "lyon": [("L001", 3, 1200), ("L002", 1, 2400)],
}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/sales/{shop}")
async def sales(shop: Literal["paris", "lyon"], day: date):
    mode = os.getenv("DEMO_MODE", "ok")
    delay = 4 if mode == "timeout" else 0.3
    await asyncio.sleep(delay)
    if mode == "unavailable":
        raise HTTPException(status_code=503, detail="Panne fictive du fournisseur")
    rows = [
        {"sale_id": sale_id, "shop": shop, "day": day.isoformat(), "quantity": quantity, "unit_price_cents": cents}
        for sale_id, quantity, cents in ROWS[shop]
    ]
    if mode == "invalid":
        rows[0]["quantity"] = -1
    return rows

