# Base Linux avec Python 3.12.
FROM python:3.12-slim-trixie

# La meme version de uv que celle utilisee pour le projet.
COPY --from=ghcr.io/astral-sh/uv:0.12.9 /uv /usr/local/bin/uv

WORKDIR /app
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_PYTHON_DOWNLOADS=never

# Les dependances sont reconstruites pour Linux a partir du verrouillage.
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev --no-install-project

COPY ventes_lab ./ventes_lab

# L'application s'execute avec un utilisateur non administrateur.
RUN useradd --create-home appuser && chown appuser:appuser /app
USER appuser

# Le port sera publie sur le PC par Compose.
EXPOSE 8000
CMD ["/app/.venv/bin/uvicorn", "ventes_lab.api:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
