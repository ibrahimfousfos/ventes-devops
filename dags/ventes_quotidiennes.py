"""Import quotidien des ventes via l'API du projet.

Pour un lancement manuel, choisir une date dans le champ day.
Pour les lancements planifies, traiter la journee qui vient de se terminer.
"""

import json
import logging
import os
from datetime import date, timedelta
from urllib.request import Request, urlopen

import pendulum
from airflow.sdk import CronDataIntervalTimetable, Param, dag, get_current_context, task
from airflow.sdk.exceptions import AirflowFailException

logger = logging.getLogger(__name__)


def appeler_api(path: str, method: str = "GET") -> dict:
    """Une erreur HTTP ou un timeout fait echouer la tache : Airflow la reprendra."""
    base_url = os.environ.get("VENTES_API_URL", "http://api:8000").rstrip("/")
    request = Request(base_url + path, method=method, headers={"Accept": "application/json"})
    with urlopen(request, timeout=10) as response:
        result = json.load(response)
    logger.info("%s %s : %s", method, path, json.dumps(result, ensure_ascii=False))
    return result


@dag(
    dag_id="ventes_quotidiennes",
    description="Verifier l'API, importer les ventes et controler le bilan.",
    # Minuit en France ; chaque execution traite la journee precedente.
    schedule=CronDataIntervalTimetable("0 0 * * *", timezone="Europe/Paris"),
    start_date=pendulum.datetime(2026, 9, 1, tz="Europe/Paris"),
    catchup=False,
    max_active_runs=1,
    default_args={
        "owner": "ibrahim",
        "retries": 2,
        "retry_delay": timedelta(seconds=30),
        "execution_timeout": timedelta(minutes=2),
    },
    params={
        "day": Param(
            None,
            type=["null", "string"],
            format="date",
            description="Date a importer manuellement (AAAA-MM-JJ). Exemple : 2026-09-14.",
        ),
    },
    tags=["ventes", "entretien"],
)
def ventes_quotidiennes():
    @task
    def verifier_api():
        appeler_api("/ready")

    @task(multiple_outputs=False)
    def importer_ventes() -> dict:
        context = get_current_context()
        requested_day = context["params"].get("day")
        if requested_day:
            day = date.fromisoformat(requested_day).isoformat()
        else:
            interval_start = context.get("data_interval_start")
            if interval_start is None:
                raise AirflowFailException("Renseigne day pour ce lancement manuel : AAAA-MM-JJ.")
            day = interval_start.in_timezone("Europe/Paris").date().isoformat()
        return appeler_api(f"/imports/{day}", method="POST")

    @task(multiple_outputs=False)
    def verifier_bilan(import_result: dict) -> dict:
        day = import_result["day"]
        result = appeler_api(f"/sales/summary?day={day}")
        # Valeurs connues de notre source fictive, identiques chaque jour.
        expected = {
            "day": day,
            "sales_count": 4,
            "total_quantity": 7,
            "revenue_cents": 13000,
            "currency": "EUR",
        }
        if result != expected:
            raise ValueError(f"Bilan inattendu : {result}. Attendu : {expected}")
        return result

    api_disponible = verifier_api()
    resultat_import = importer_ventes()
    api_disponible >> resultat_import
    verifier_bilan(resultat_import)


ventes_quotidiennes()
