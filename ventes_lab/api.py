import logging
from contextlib import asynccontextmanager
from datetime import date

from fastapi import FastAPI, HTTPException
from sqlalchemy.exc import SQLAlchemyError

from ventes_lab.collector import SourceUnavailable
from ventes_lab.config import Settings
from ventes_lab.domain import InvalidSales
from ventes_lab.service import import_sales
from ventes_lab.storage import Storage

logger = logging.getLogger("uvicorn.error")


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings.from_env()
    storage = Storage(settings.database_url)

    @asynccontextmanager
    async def lifespan(app):
        storage.initialize()
        try:
            yield
        finally:
            storage.close()

    app = FastAPI(title="Ventes DevOps — API pédagogique", version="0.1.0", lifespan=lifespan)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.get("/ready")
    def ready():
        try:
            storage.ready()
        except SQLAlchemyError as exc:
            raise HTTPException(status_code=503, detail="Base indisponible") from exc
        return {"status": "ready"}

    @app.post("/imports/{day}")
    def run_import(day: date):
        try:
            result = import_sales(day, settings, storage)
        except SourceUnavailable as exc:
            raise HTTPException(status_code=503, detail="Source indisponible") from exc
        except InvalidSales as exc:
            raise HTTPException(status_code=502, detail=str(exc)) from exc
        except SQLAlchemyError as exc:
            raise HTTPException(status_code=503, detail="Base indisponible") from exc
        logger.info("import day=%s received=%s inserted=%s skipped=%s", day, result["received"], result["inserted"], result["skipped"])
        return result

    @app.get("/sales/summary")
    def summary(day: date):
        try:
            return storage.summary(day)
        except SQLAlchemyError as exc:
            raise HTTPException(status_code=503, detail="Base indisponible") from exc

    return app
