import math
import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    database_url: str = "sqlite:///./ventes.db"
    source_base_url: str = "http://127.0.0.1:8001"
    request_timeout_seconds: float = 2.0

    def __post_init__(self):
        if not self.database_url.startswith(("sqlite:", "postgresql+psycopg:")):
            raise ValueError("DATABASE_URL doit utiliser sqlite: ou postgresql+psycopg:")
        if not self.source_base_url.startswith(("http://", "https://")):
            raise ValueError("SOURCE_BASE_URL doit être une URL HTTP ou HTTPS")
        if not math.isfinite(self.request_timeout_seconds) or self.request_timeout_seconds <= 0:
            raise ValueError("REQUEST_TIMEOUT_SECONDS doit être un nombre positif fini")

    @classmethod
    def from_env(cls):
        return cls(
            database_url=os.getenv("DATABASE_URL", "sqlite:///./ventes.db"),
            source_base_url=os.getenv("SOURCE_BASE_URL", "http://127.0.0.1:8001"),
            request_timeout_seconds=float(os.getenv("REQUEST_TIMEOUT_SECONDS", "2")),
        )

