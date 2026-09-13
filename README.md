# Ventes DevOps — le projet de départ

Un seul projet pour apprendre Git, les tests, Docker, la CI/CD et Airflow.
Toutes les données sont fictives. Le code métier et l'API de départ sont fournis.
Les fichiers Docker, les workflows GitHub Actions et le DAG Airflow seront construits
pendant les missions : le ZIP est le point de départ de l'exercice.

## Le résultat à viser

Deux boutiques exposent leurs ventes par HTTP. Un traitement Python collecte leurs
données, les valide et les enregistre. Une API permet de consulter les indicateurs.
Tu feras ensuite exécuter l'import par Airflow, fonctionner les services dans Docker,
vérifier les changements par GitHub Actions et déployer une version sur un serveur de démonstration.

On commence avec SQLite pour lancer le projet immédiatement. PostgreSQL arrive dans
la mission Docker Compose. Le code d'accès aux deux moteurs est déjà présent.

## Démarrer sur ton PC Windows

Prérequis : Python 3.12 et uv, que tu as déjà utilisés. Extraire le dossier
`ventes-devops` dans `C:\Dev`, puis ouvrir ce dossier dans VS Code.
Le fichier `pyproject.toml` doit être directement dans le dossier ouvert.

Dans le terminal PowerShell :

```powershell
cd C:\Dev\ventes-devops
uv sync --frozen
uv run pytest
```

Le test fourni vérifie un calcul métier. Tu complèteras la couverture dans la mission 2.
`uv.lock` fixe les versions résolues ; `--frozen` les réutilise. Il n'est pas nécessaire
d'activer manuellement un environnement virtuel pour utiliser `uv run`.

**Terminal 1 — la source fictive :**

```powershell
uv run uvicorn ventes_lab.demo_source:app --host 127.0.0.1 --port 8001
```

**Terminal 2 — l'API du projet :**

```powershell
uv run uvicorn ventes_lab.api:create_app --factory --host 127.0.0.1 --port 8000
```

**Terminal 3 — importer et consulter :**

```powershell
Invoke-RestMethod -Method Post http://127.0.0.1:8000/imports/2026-09-12
Invoke-RestMethod "http://127.0.0.1:8000/sales/summary?day=2026-09-12"
```

Sur une base neuve, le premier import renvoie `received=4`, `inserted=4`, `skipped=0`.
La synthèse renvoie **4 ventes, 7 articles et 13 000 centimes, soit 130 EUR**.
Un deuxième import de la même date renvoie `inserted=0`, `skipped=4` : le total reste 130 EUR.
Une autre date constitue une autre journée de ventes fictives.

Ouvrir [l'interface de l'API](http://127.0.0.1:8000/docs) pour essayer les routes
avec « Try it out ». Arrêter chaque serveur avec `Ctrl+C` dans son terminal.

## Les routes

| Route | Fonction |
| --- | --- |
| `GET /health` | Vérifier que le processus de l'API répond. |
| `GET /ready` | Vérifier que l'API peut interroger sa base. |
| `POST /imports/{day}` | Collecter, valider et enregistrer une journée. |
| `GET /sales/summary?day=...` | Lire les indicateurs de cette journée. |
| `GET /docs` | Consulter la documentation interactive. |

La source fictive possède `GET /sales/paris?day=...` et `GET /sales/lyon?day=...`.
Elle introduit une petite attente réseau simulée, utile pour comprendre la collecte concurrente.

## Configuration

| Variable | Valeur par défaut | Usage |
| --- | --- | --- |
| `DATABASE_URL` | `sqlite:///./ventes.db` | Emplacement de la base. |
| `SOURCE_BASE_URL` | `http://127.0.0.1:8001` | Adresse du fournisseur fictif. |
| `REQUEST_TIMEOUT_SECONDS` | `2` | Délai maximal configuré pour les opérations HTTP. |
| `DEMO_MODE` | `ok` | Dans le terminal de la source : `ok`, `invalid`, `unavailable` ou `timeout`. |

Le fichier `.env.example` documente les variables. **L'application ne le charge pas
automatiquement.** Dans PowerShell, définir une variable avant de démarrer le serveur :

```powershell
$env:SOURCE_BASE_URL = "http://127.0.0.1:8001"
uv run uvicorn ventes_lab.api:create_app --factory --host 127.0.0.1 --port 8000
```

Chaque terminal possède son environnement. Redémarrer le processus après une modification.
Dans Docker Compose, on transmettra ces variables explicitement au bon service.

Pour PostgreSQL, le format attendu sera :
`postgresql+psycopg://UTILISATEUR:MOT_DE_PASSE@HOTE:5432/ventes`.
La base `ventes` devra déjà exister ; l'application crée ensuite sa table.

## Première panne à essayer

Arrêter la source dans son terminal, puis la relancer ainsi :

```powershell
$env:DEMO_MODE = "unavailable"
uv run uvicorn ventes_lab.demo_source:app --host 127.0.0.1 --port 8001
```

Relancer un import : l'API doit renvoyer **503**, tandis que `/health` reste accessible.
Pour revenir au fonctionnement normal, arrêter la source, exécuter
`$env:DEMO_MODE = "ok"`, puis la relancer.

Le mode `invalid` renvoie une quantité négative : l'import doit répondre **502** et
n'enregistrer aucune nouvelle vente. Le mode `timeout` dépasse le délai HTTP par défaut
et doit provoquer **503**. Utiliser une date neuve pour observer l'absence d'import partiel.

## Les fichiers à connaître

| Fichier | Rôle |
| --- | --- |
| `ventes_lab/domain.py` | Contrat des ventes, validation du lot et calcul des indicateurs. |
| `ventes_lab/collector.py` | Collecte HTTP concurrente avec `async` et `await`. |
| `ventes_lab/storage.py` | Transactions et stockage SQLite / PostgreSQL. |
| `ventes_lab/service.py` | Assemblage collecte, validation et stockage. |
| `ventes_lab/api.py` | Routes et traduction des erreurs en réponses HTTP. |
| `ventes_lab/demo_source.py` | Fournisseur fictif et pannes reproductibles. |
| `tests/test_domain.py` | Premier test à partir duquel travailler. |
| `docs/REFERENCE.md` | Documentation des notions, exemples et erreurs. |
| `docs/MISSIONS.md` | Parcours et critères pour savoir quand passer à la suite. |
| `docs/VERIFICATION.md` | Vérifications réellement effectuées sur ce kit. |

## Limites choisies pour garder le projet court

- Une clé `(date, boutique, identifiant)` désigne une vente. Réimporter cette clé
  conserve les premières valeurs ; corriger une vente existante demanderait une règle supplémentaire.
- Toute la collecte et la validation précèdent l'écriture. Le lot valide est enregistré
  dans une transaction. Un lot invalide est refusé en entier.
- `/ready` contrôle la base ; il ne contrôle pas la source HTTP.
- L'API n'a pas d'authentification. Le déploiement d'apprentissage sera accessible
  via un tunnel SSH, avec les services liés à l'interface locale du serveur.
- Le démarrage crée la table par commodité. Les migrations de schéma pourront venir ensuite.

**Commencer par la mission 1.** La référence sert à retrouver une explication au moment où tu en as besoin.

