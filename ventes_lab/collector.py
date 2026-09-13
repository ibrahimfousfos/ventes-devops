import asyncio
from datetime import date

import httpx

from ventes_lab.domain import SHOPS, InvalidSales


class SourceUnavailable(RuntimeError):
    """La source HTTP ne répond pas correctement."""


async def fetch_sales(base_url: str, day: date, timeout: float) -> dict:
    async with httpx.AsyncClient(base_url=base_url.rstrip("/") + "/", timeout=timeout) as client:
        async def fetch_shop(shop):
            try:
                response = await client.get(f"sales/{shop}", params={"day": day.isoformat()})
                response.raise_for_status()
            except httpx.HTTPError as exc:
                raise SourceUnavailable(f"Source indisponible : {shop}") from exc
            try:
                return response.json()
            except ValueError as exc:
                raise InvalidSales("La source ne renvoie pas du JSON valide") from exc

        results = await asyncio.gather(*(fetch_shop(shop) for shop in SHOPS), return_exceptions=True)
        for result in results:
            if isinstance(result, BaseException):
                raise result
        return dict(zip(SHOPS, results, strict=True))

