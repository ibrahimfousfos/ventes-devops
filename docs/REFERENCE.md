# Référence — Git, tests, API, Docker, CI/CD et Airflow

Ce document couvre les notions utiles au projet **Ventes DevOps**. Commencer par Git
et le lien entre tests et merge, puis ouvrir les autres sections pendant les missions.
Les exemples sont de petits repères ; le parcours pratique est dans `MISSIONS.md`.

## 1. La carte du projet

Il existe deux enchaînements indépendants, qui se rejoignent dans l'application déployée.

| Enchaînement | Déclenchement | Résultat |
| --- | --- | --- |
| Livraison du code : Git, GitHub Actions, registre, serveur | Tu proposes puis intègres une modification. | Une version testée de l'application est déployée. |
| Traitement des données : Airflow, API d'import, base | Une journée doit être traitée ou rejouée. | Les ventes sont enregistrées et les indicateurs consultables. |

Dans le traitement, Python peut attendre plusieurs réponses HTTP en concurrence avec
`async`/`await`. Cela ne remplace ni les tests ni la planification par Airflow.

## 2. Git et GitHub

**Git** gère l'historique des versions. **GitHub** héberge des dépôts Git et ajoute
les pull requests, les revues et les automatisations.

| Notion | Signification concrète |
| --- | --- |
| Dépôt / repository | Les fichiers d'un projet et leur historique Git. |
| Working tree | Les fichiers tels qu'ils sont actuellement sur ton disque. |
| Staging area / index | Les modifications sélectionnées pour le prochain commit. |
| `git add` | Sélectionner des modifications dans l'index. |
| Commit | Enregistrer un état versionné dans l'historique local, avec un message et un identifiant. |
| Branche | Un nom qui suit une ligne de travail ; tu peux développer une modification séparément. |
| `main` | Le nom choisi ici pour la branche principale ; ce nom n'implique aucune protection automatique. |
| `origin` | Le nom conventionnel donné au dépôt distant. |
| Clone | Récupérer un dépôt avec son historique et configurer un lien vers son origine. |
| Push | Envoyer des commits et mettre à jour des références sur le dépôt distant. |
| Fetch | Récupérer les informations distantes sans les intégrer dans ta branche de travail. |
| Pull | Récupérer, puis intégrer selon les options/configurations : avance rapide, merge ou rebase. |
| Pull request / PR | Une proposition de changement à discuter, tester et fusionner sur GitHub. |
| Diff | La différence entre deux états de fichiers. |
| Conflit | Git ne sait pas combiner automatiquement certaines modifications ; une résolution est nécessaire. |
| Tag | Un nom associé à un point de l'historique, souvent pour une version publiée. |

Un commit ne publie pas automatiquement le code. Un push ne fusionne pas automatiquement
une branche dans `main`. Une PR n'est pas la même chose qu'un `git pull`.

La PR rassemble le contexte, le diff, les commits et les contrôles pour décider si le
changement peut être intégré. [Référence GitHub sur les PR](https://docs.github.com/en/pull-requests/reference/pull-requests).

### Merge, squash et rebase

| Opération | Effet sur l'historique | Ce qu'on apprend ici |
| --- | --- | --- |
| Merge | Intègre les changements ; peut créer un commit de fusion si les histoires ont divergé. Une avance rapide est parfois possible. | Le premier mécanisme à pratiquer. |
| Squash merge | Regroupe le contenu d'une PR en un nouveau commit sur la branche cible. | Comprendre pourquoi plusieurs commits de travail peuvent devenir un seul commit final. |
| Rebase | Rejoue des commits sur une nouvelle base ; les commits rejoués reçoivent de nouveaux identifiants. | Une démonstration sur des branches locales après le premier merge. |

Un rebase n'ajoute pas de tests et ne remplace pas une revue. Réécrire une histoire déjà
partagée peut perturber les autres personnes qui l'utilisent : on s'entraîne d'abord sur
des commits locaux. [Explication du rebase par Pro Git](https://git-scm.com/book/en/v2/Git-Branching-Rebasing).

### Les commandes à reconnaître

| Commande | Question à laquelle elle répond |
| --- | --- |
| `git status` | Sur quelle branche suis-je, et quels fichiers ont changé ? |
| `git diff` | Qu'ai-je modifié sans encore le sélectionner pour un commit ? |
| `git diff --cached` | Qu'est-ce que mon prochain commit contiendra ? |
| `git switch -c nom` | Comment commencer une branche de travail ? |
| `git add fichier` | Comment sélectionner ce changement ? |
| `git commit -m "message"` | Comment enregistrer cette étape localement ? |
| `git push -u origin nom` | Comment envoyer cette branche et définir son suivi ? |
| `git fetch origin` | Qu'est-ce qui a changé sur le dépôt distant ? |
| `git pull --ff-only` | Comment mettre à jour sans créer implicitement une fusion si les historiques ont divergé ? |
| `git log --oneline --graph --all` | À quoi ressemble l'historique ? |
| `git revert SHA` | Comment créer un nouveau commit qui annule les changements d'un ancien commit ? |

## 3. Pourquoi tester avant de merger ?

Dans notre projet, une modification peut transformer le calcul `quantité × prix` en
simple addition ou oublier la quantité. Le code peut démarrer normalement tout en
renvoyant un chiffre d'affaires faux. Un test avec un résultat connu permet de le détecter.

Le circuit de travail sera : proposer une PR, exécuter les tests, lire le diff, corriger
les problèmes, puis fusionner. Des tests verts donnent des preuves sur les cas testés ;
ils ne prouvent pas l'absence de tout bug.

**Une CI rouge ne bloque pas toujours le merge à elle seule.** Il faut configurer les
contrôles obligatoires sur la branche ou dans un ruleset, et vérifier les possibilités
de contournement. Dans l'exercice, le compte utilisé doit respecter cette règle.
[Contrôles obligatoires GitHub](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches#require-status-checks-before-merging).

## 4. Les types de tests

| Type | Ce qu'on vérifie | Exemple du projet |
| --- | --- | --- |
| Unitaire | Une petite unité de comportement en isolant les dépendances inutiles. | Une quantité de 2 à 1 500 centimes donne 3 000 centimes. |
| Intégration | Plusieurs composants réels coopèrent correctement. | Une route valide un import et écrit dans une base temporaire. |
| Bout en bout / E2E | Le parcours complet, avec les services réellement démarrés. | Source HTTP, API, PostgreSQL : importer puis lire 130 EUR. |
| Smoke test | Quelques contrôles rapides après un démarrage ou un déploiement. | `/ready` répond et une route essentielle fonctionne. |
| Non-régression | Un comportement déjà attendu reste correct après modification. | Un second import ne double pas les ventes. |
| Contrat / schéma | Les données échangées respectent les champs, types et contraintes attendus. | Une source contient un identifiant et une quantité positive. |
| Performance / charge | Le comportement sous un volume ou une concurrence définis. | Observer les délais quand plusieurs clients appellent l'API. À approfondir après le socle. |

Ces catégories peuvent se recouvrir : un test de non-régression peut être unitaire
ou d'intégration. Le niveau dépend de ce que le test traverse réellement.

Pour chaque comportement, penser à quatre familles de cas :

| Famille | Exemples |
| --- | --- |
| Nominal | Une journée valide avec les deux boutiques. |
| Limite | Liste vide, une seule vente, prix nul autorisé. |
| Invalide | Quantité négative, date différente de la journée demandée, champ absent. |
| Défaillance technique | Source en panne, délai dépassé, base inaccessible. |

## 5. Pytest : les mécanismes utiles

Un test suit souvent **préparer → agir → vérifier**. Donner des valeurs connues au système,
appeler le comportement, puis comparer son résultat à l'attendu.

### `assert` et résultat attendu

```python
def test_total():
    assert 2 * 1500 == 3000
```

Dans le vrai test fourni, on appelle `summarize` pour vérifier le comportement de l'application.
`assert` provoque un échec si la condition est fausse ; pytest montre attendu et obtenu.

### `pytest.raises` : une erreur peut être le bon comportement

```python
import pytest
from ventes_lab.config import Settings

def test_delai_invalide():
    with pytest.raises(ValueError):
        Settings(request_timeout_seconds=0)
```

Si l'application accepte zéro sans lever d'exception, ce test échoue avec
`DID NOT RAISE`. Cela signifie que l'erreur attendue n'a pas été levée. On vérifie alors
la règle attendue et le code, au lieu de supprimer mécaniquement le test.
[Assertions et exceptions avec pytest](https://docs.pytest.org/en/stable/how-to/assert.html).

### `parametrize` : plusieurs cas pour la même règle

```python
@pytest.mark.parametrize("timeout", [0, -1, float("inf")])
def test_delais_invalides(timeout):
    with pytest.raises(ValueError):
        Settings(request_timeout_seconds=timeout)
```

Pytest exécute un cas par valeur et indique celui qui échoue.
[Paramétrage](https://docs.pytest.org/en/stable/how-to/parametrize.html).

### Fixtures : préparer un contexte réutilisable et isolé

```python
from fastapi.testclient import TestClient
from ventes_lab.api import create_app

@pytest.fixture
def client(tmp_path):
    settings = Settings(database_url=f"sqlite:///{tmp_path / 'test.db'}")
    with TestClient(create_app(settings)) as client:
        yield client
```

`tmp_path` fournit un dossier temporaire propre au test. Le contexte `with` active
le démarrage et l'arrêt de l'application. Il évite d'utiliser tes vraies données locales.
Une fixture prépare un contexte ; elle n'est pas automatiquement un mock.
[Fixtures pytest](https://docs.pytest.org/en/stable/how-to/fixtures.html).

### Mock, patch, monkeypatch et AsyncMock

**Un mock est un outil de simulation, pas une catégorie de test.** Il peut remplacer
un fournisseur HTTP pour que le test soit rapide et déterministe.

| Outil | Fonction |
| --- | --- |
| `Mock` | Objet de remplacement configurable ; permet aussi d'inspecter ses appels. |
| `AsyncMock` | Remplacement d'une fonction attendue avec `await`. |
| `patch` | Remplacement temporaire d'un attribut dans l'espace de noms approprié. |
| `monkeypatch` | Fixture pytest pour modifier temporairement attributs, variables d'environnement ou éléments similaires. |
| Fixture | Prépare les ressources du test ; peut utiliser un mock mais n'en est pas un synonyme. |

Exemple de panne simulée dans les tests de l'API :

```python
from unittest.mock import AsyncMock
from ventes_lab.collector import SourceUnavailable

def test_source_en_panne(client, monkeypatch):
    fake = AsyncMock(side_effect=SourceUnavailable("panne simulée"))
    monkeypatch.setattr("ventes_lab.service.fetch_sales", fake)
    response = client.post("/imports/2026-09-12")
    assert response.status_code == 503
    fake.assert_awaited_once()
```

On remplace **`ventes_lab.service.fetch_sales`**, car c'est le nom lu par le service,
même si la fonction a été définie dans `collector.py`. Remplacer le mauvais nom peut
laisser le véritable appel réseau se produire.

`return_value` définit un résultat simulé ; `side_effect` peut provoquer une exception.
`monkeypatch.setenv` et `delenv` servent aux scénarios de configuration.
[Bibliothèque standard mock](https://docs.python.org/3/library/unittest.mock.html),
[monkeypatch dans pytest](https://docs.pytest.org/en/stable/how-to/monkeypatch.html).

Ne remplacer que les dépendances nécessaires au scénario. Si tout est simulé, le test
ne montre pas que les composants fonctionnent ensemble. Les tests avec PostgreSQL réel
et le parcours complet complètent les tests rapides utilisant mocks et SQLite.

### Lire un résultat de test

| Résultat | Interprétation |
| --- | --- |
| `PASSED` | Les vérifications du cas ont réussi. |
| `FAILED` avec `AssertionError` | Le résultat ne correspond pas à l'attendu. |
| `DID NOT RAISE` | L'exception attendue n'a pas eu lieu. |
| `ERROR` pendant la collecte | Le module de test n'a pas pu être chargé, par exemple à cause d'un import. |
| `ERROR` pendant une fixture | Le contexte nécessaire au test n'a pas pu être préparé ou nettoyé. |

Commandes utiles : `uv run pytest`, `uv run pytest -q`,
`uv run pytest tests/test_domain.py`, `uv run pytest -k revenue`, `uv run pytest -x`.
Le coverage mesure les portions de code parcourues ; un fort taux ne garantit pas
que les assertions détectent les erreurs importantes.

## 6. Erreurs Python, données et HTTP

| Erreur ou symptôme | Sens | Réaction utile |
| --- | --- | --- |
| `SyntaxError` | Le code ne respecte pas la syntaxe Python. | Corriger avant de pouvoir exécuter les tests. |
| `ModuleNotFoundError` | Import introuvable dans l'environnement utilisé. | Vérifier le dossier, `uv sync` et `uv run`. |
| `TypeError` | Mauvais type ou mauvais appel d'une fonction. | Examiner les arguments et le contrat. |
| `ValueError` | Valeur refusée par une règle de validation. | Identifier la valeur et la règle concernée. |
| `KeyError` | Clé absente d'un dictionnaire. | Déterminer si elle était obligatoire ou facultative. |
| `ValidationError` de Pydantic | Un objet ne respecte pas le modèle. | Lire les champs et contraintes en erreur. |
| `httpx.TimeoutException` | Une opération HTTP dépasse le délai configuré. | Vérifier la source et la politique de reprise. |
| `httpx.HTTPStatusError` | `raise_for_status()` signale une réponse HTTP en erreur. | Examiner le statut et la nature temporaire ou durable du problème. |
| `SQLAlchemyError` | Une erreur de base de données ou de son accès. | Examiner connexion, logs, transaction et disponibilité. |

Une réponse HTTP en erreur ne lève pas automatiquement une exception pour tous les clients.
Dans notre collecteur, c'est `response.raise_for_status()` qui provoque l'exception sur
les réponses concernées.

| Statut HTTP | Usage dans le laboratoire |
| --- | --- |
| 200 | Appel réussi. |
| 404 | Route inconnue ; ce n'est pas ici le statut d'une journée sans vente. |
| 422 | Paramètre de requête ou date non conforme au modèle FastAPI. |
| 502 | La source a répondu mais ses données ne respectent pas le contrat. |
| 503 | Source ou base indisponible, y compris le timeout prévu dans cet exercice. |
| 500 | Erreur interne non gérée : un bug à diagnostiquer, pas à masquer systématiquement. |

Ces correspondances sont des **choix de cette API**. Une API différente peut exposer
un timeout de fournisseur avec 504. L'essentiel est un contrat explicite et testé.

Une erreur permanente de données appelle une correction des données. Une panne temporaire
peut justifier un retry limité. Attraper toutes les exceptions et renvoyer un succès
ferait disparaître le signal d'échec attendu par les tests et par Airflow.

## 7. FastAPI et l'asynchrone

Une route associe une méthode HTTP et un chemin à une fonction Python. FastAPI valide
les paramètres typés et expose une description OpenAPI consultable dans `/docs`.
Le test de la logique métier et le test d'une route ne couvrent pas exactement la même chose.
[Tests FastAPI](https://fastapi.tiangolo.com/tutorial/testing/).

| Notion | Signification |
| --- | --- |
| `def` | Fonction synchrone ordinaire. |
| `async def` | Fonction qui crée une coroutine lorsqu'on l'appelle. |
| `await` | Attendre une opération compatible en permettant à la boucle d'événements d'exécuter d'autres tâches. |
| `asyncio.gather` | Attendre plusieurs opérations concurrentes. |
| Concurrence | Plusieurs tâches progressent au cours de la même période. |
| Parallélisme | Plusieurs calculs s'exécutent réellement au même instant sur des ressources distinctes. |

Dans le projet, `fetch_sales` attend deux fournisseurs avec `httpx.AsyncClient`.
La base est accédée avec un pilote synchrone. Les routes concernées sont donc en `def` :
FastAPI les exécute dans des threads de travail. `import_sales` lance sa collecte avec
`asyncio.run` depuis ce contexte synchrone. **Ne pas convertir seulement la route en
`async def` en gardant cet appel : on tenterait de lancer une boucle dans une boucle active.**

L'asynchrone aide pendant les attentes d'entrées/sorties. Ajouter `async` n'accélère pas
automatiquement un calcul CPU ; une opération bloquante reste bloquante si on l'appelle
directement dans la boucle d'événements.
[Guide officiel FastAPI sur async/await](https://fastapi.tiangolo.com/async/).

## 8. Docker et configuration

| Notion | Rôle dans le projet |
| --- | --- |
| Dockerfile | Instructions permettant de construire l'image. |
| Image | Paquet versionnable contenant fichiers et dépendances nécessaires. |
| Conteneur | Instance créée à partir d'une image, avec son état et sa configuration. |
| `RUN` | Commande exécutée pendant la construction de l'image. |
| `CMD` | Commande par défaut au démarrage du conteneur. |
| Build context | Ensemble de fichiers rendus accessibles au build. |
| `.dockerignore` | Exclut des fichiers du contexte, par exemple environnement virtuel et secrets. |
| Registry | Service qui stocke les images, comme Docker Hub ou GHCR. |
| Tag / digest | Le tag est un nom qui peut changer de cible ; un digest identifie un contenu. |
| Volume | Stockage dont la durée de vie peut dépasser celle d'un conteneur. |
| Docker Compose | Description et gestion des services, réseaux, volumes et configurations. |

`-p 8000:8000` associe un port de l'hôte à un port du conteneur, dans cet ordre.
`EXPOSE` documente un port ; il ne publie pas ce port à lui seul.
Dans le réseau Compose, `api` joint PostgreSQL sur le nom `db`. Son propre `localhost`
désigne son propre conteneur. Une application doit écouter sur une interface appropriée,
par exemple `0.0.0.0` dans son conteneur, pour être jointe par les autres services.

Commandes à pratiquer : `docker build`, `docker run`, `docker ps`, `docker logs`,
`docker compose up -d`, `docker compose ps`, `docker compose logs api`, `docker compose down`.
L'option `down -v` retire aussi les volumes déclarés concernés : la distinguer d'un arrêt ordinaire.
[Démarrage Docker](https://docs.docker.com/get-started/tutorials/run-an-app/),
[Docker avec uv](https://docs.astral.sh/uv/guides/integration/docker/).

## 9. CI, livraison et déploiement

| Notion | Ce que tu vas en faire |
| --- | --- |
| CI, intégration continue | Vérifier régulièrement les changements : tests et construction. |
| Livraison continue | Produire une version déployable ; la mise en production peut rester déclenchée manuellement. |
| Déploiement continu | Déployer automatiquement après les validations prévues. |
| Workflow | Fichier qui décrit événements déclencheurs, jobs et étapes. |
| Runner | Machine qui exécute les jobs. |
| Job / step | Un groupe d'opérations / une opération dans ce groupe. |
| Secret | Valeur sensible transmise au workflow par le mécanisme de secrets, pas inscrite dans le code. |
| Artifact | Résultat conservé d'un job, par exemple un rapport de tests. |
| Rollback | Redéployer une version précédente quand la nouvelle ne convient pas. |

Sur la PR, lancer les tests sans les accès de déploiement. Après intégration, revalider
le commit résultant, construire l'image, la publier et déployer sa version précise.
Une image qui se construit n'est pas une preuve que les tests passent, et des tests
unitaires verts ne prouvent pas que le serveur distant est correctement configuré.
[CI Python avec GitHub Actions](https://docs.github.com/en/actions/tutorials/build-and-test-code/python).

SSH permet de se connecter au serveur pour lancer les commandes de déploiement. La clé
privée reste du côté du client de déploiement ; la clé publique autorisée est installée
sur le serveur. Le laboratoire utilisera un compte dédié et une version d'image identifiable.

## 10. Airflow et fiabilité des imports

| Notion | Exemple |
| --- | --- |
| DAG | Les tâches d'un traitement et leurs dépendances, sans cycle. |
| Task | Vérifier l'API, importer une date, contrôler les indicateurs. |
| Scheduler | Décide quand déclencher les traitements planifiés. |
| Executor | Mécanisme chargé de faire exécuter les tâches. |
| DAG run / task instance | Une exécution du DAG / d'une tâche pour ce traitement. |
| Retry | Nouvelle tentative après un échec, suivant les règles configurées. |
| Data interval | Période de données visée par le traitement. |
| Catchup / backfill | Traitement d'intervalles passés selon la configuration ou une demande explicite. |
| XCom | Petits échanges d'informations entre tâches. |
| Métadonnées Airflow | État et historique des traitements ; différent des données métier. |

Le DAG appelle l'API avec une date explicite. Réessayer cette même journée conserve le
même état métier final grâce à la clé unique et à l'insertion qui ignore les clés déjà
présentes. Les réponses `inserted` et `skipped` peuvent changer entre les appels : c'est
l'état final des ventes qui est idempotent.

Airflow planifie les imports même lorsqu'aucun code n'a changé. GitHub Actions déploie
une nouvelle version lorsque tu intègres du code. Un DAG peut lancer des scripts,
appeler des API ou utiliser d'autres systèmes ; il ne remplace pas les fonctions métier.
[Architecture officielle Airflow](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/overview.html).

Pour rester court, on commencera avec un seul DAG et une installation Linux via Docker.
On fixera la version et utilisera les instructions correspondantes lors de la mission :
les exemples Airflow 2 et Airflow 3 ne sont pas interchangeables sans vérification.

## 11. Un diagnostic en cinq questions

1. Quel comportement précis était attendu ?
2. Quelle est la première erreur observable : statut HTTP, exception, test ou log ?
3. Quel composant est concerné : code, configuration, réseau, base ou orchestrateur ?
4. Quelle vérification simple départage les hypothèses ?
5. Quel test ou contrôle permettra de détecter ce problème la prochaine fois ?

Exemple : `/health` répond, `/imports/...` renvoie 503 et la synthèse reste inchangée.
Vérifier d'abord la source et sa configuration, puis les logs. Le fait que l'API démarre
n'implique pas que toutes ses dépendances fonctionnent.

Référence préparée le 12 septembre 2026. Les commandes du socle ont leur état de validation
dans `VERIFICATION.md`. Les missions d'infrastructure constituent la suite de l'exercice.

