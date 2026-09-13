# Les missions — une seule application, une progression concrète

Le code métier fourni évite de consacrer le projet au développement d'une application.
Tu dois toutefois savoir raconter son fonctionnement : deux sources, un import validé,
une base et une API. Une modification utile, une panne comprise et un résultat vérifié
constituent une meilleure preuve d'apprentissage qu'un nombre de vidéos regardées.

**Estimation de travail actif : 10 à 15 heures pour les sept missions**, avec une marge
supplémentaire possible pour les installations, les comptes et le serveur. Les estimations
ci-dessous sont des repères, pas une promesse de durée. On valide chaque mission avant
d'ajouter le prochain outil. Chaque mission peut devenir une branche puis une pull request.

## Mission 1 — comprendre Git par une vraie modification (45 à 75 min)

Lire les sections Git et tests avant merge dans `REFERENCE.md` : environ 15 à 20 minutes.

Dans le dossier du projet :

```powershell
git init
git branch -M main
git status
git add .
git diff --cached --stat
git commit -m "Ajoute le socle du projet ventes"
```

Si Git demande ton identité, configurer ton nom et l'adresse de ton choix pour **ce dépôt**
avec `git config user.name "TON NOM"` et `git config user.email "TON ADRESSE"`.
Utiliser ton adresse GitHub privée si c'est ton choix, puis recommencer le commit.

Créer sur GitHub un dépôt vide, sans README généré. Copier son URL, puis :

```powershell
git remote add origin URL_DE_TON_DEPOT
git push -u origin main
git switch -c docs/presentation
```

Ajouter au README une phrase décrivant ce que tu veux apprendre. Puis :

```powershell
git diff
git add README.md
git commit -m "Précise mon objectif de formation"
git push -u origin docs/presentation
```

Ouvrir sur GitHub une pull request de `docs/presentation` vers `main`. Regarder le diff,
puis fusionner cette première modification de documentation. Les tests automatiques seront
configurés en mission 5 ; on ne prétend pas qu'ils protègent déjà cette première PR.

```powershell
git switch main
git pull --ff-only
git log --oneline --graph --all
```

**Mission terminée si :** tu sais distinguer commit, push, PR et merge, et montrer où se
trouve ta modification. L'exercice de conflit et la démonstration de rebase se feront sur
des branches locales d'entraînement après ce premier cycle. Comprendre le principe du
rebase suffit pour commencer les autres missions.

## Mission 2 — faire échouer puis réussir de vrais tests (1 h 30 à 2 h 30)

Créer `tests/qualite-import`. Exécuter le test fourni, puis écrire ces tests :

| Test à écrire | Ce qu'il protège |
| --- | --- |
| Synthèse d'une liste vide et de plusieurs ventes | Calcul métier et cas limite. |
| Quantité zéro ou négative, prix négatif, champ absent | Contrat des données. |
| Deux boutiques attendues, bonne date et bon nom de boutique | Cohérence du lot collecté. |
| Doublon dans un lot | Qualité des identifiants reçus. |
| Import normal dans une base temporaire | Coopération API, métier et stockage. |
| Deux imports de la même journée | Absence de double comptage. |
| Fournisseur indisponible et données invalides | Réponses HTTP 503 et 502 ; absence d'écriture partielle. |
| Date illisible dans l'URL | Réponse HTTP 422. |

Utiliser `parametrize` pour les variantes d'une même règle, une fixture pour la base
temporaire, `pytest.raises` pour les exceptions, et `AsyncMock` pour remplacer la collecte
HTTP dans les tests d'API. La référence indique où remplacer la fonction.

Changer volontairement `quantity * unit_price_cents` en `unit_price_cents` dans le calcul.
Constater l'échec du test, lire attendu/obtenu, puis restaurer la bonne formule.

**Mission terminée si :** tu peux expliquer le risque couvert par chaque test et reproduire
un échec utile. Les tests rapides doivent fonctionner sans démarrer la source réelle.

## Mission 3 — FastAPI et attente réseau (45 à 75 min)

Faire tourner les deux serveurs et utiliser `/docs`. Tester une journée valide et une
date incorrecte. Lire les routes de `api.py`, puis les fonctions `import_sales` et `fetch_sales`.

Repérer où le programme attend le réseau. La collecte utilise deux requêtes concurrentes.
Faire une variante séquentielle dans une branche locale : elle doit rendre les mêmes
données. Comparer plusieurs durées à titre d'observation, sans transformer un seuil de
chronométrage fragile en test de réussite.

Expliquer pourquoi les routes qui appellent le stockage synchrone sont écrites avec
`def`, et pourquoi `fetch_sales` est écrit avec `async def`. La référence détaille le
passage par le thread de travail de FastAPI et `asyncio.run`.

**Mission terminée si :** tu sais ce qu'est une route, ce que signifient 200/422/502/503,
et où l'asynchrone aide réellement dans ce projet.

## Mission 4 — Docker puis PostgreSQL avec Compose (2 à 3 h)

Installer et lancer Docker Desktop sur Windows, puis vérifier `docker version` et
`docker compose version`. Vérifier la configuration WSL 2 indiquée par Docker Desktop.

Construire **une image du projet**. La même image pourra lancer l'API principale ou
la source selon la commande de démarrage. Écrire le Dockerfile et `.dockerignore` :
Python, dépendances fixées, copie du code, utilisateur d'exécution et commande de lancement.
Comprendre la différence entre `RUN` et `CMD`, le cache et le contexte de build.

Si on choisit un Dockerfile utilisant pip, produire la liste figée depuis uv :

```powershell
uv export --frozen --no-dev --no-emit-project --format requirements-txt --output-file requirements.txt
```

Créer ensuite `compose.yaml` avec trois services : `api`, `source` et `db` (PostgreSQL).

| Service | Point à configurer |
| --- | --- |
| `source` | Uvicorn écoute sur `0.0.0.0:8001` dans le conteneur. |
| `api` | Écoute sur `0.0.0.0:8000`, source `http://source:8001`, base sur le nom `db`. |
| `db` | Base `ventes`, utilisateur, mot de passe d'exercice, volume de données et healthcheck. |

La base de données utilise `postgresql+psycopg://...@db:5432/ventes`.
Choisir et fixer les versions des images lors de cette mission. Relier le démarrage de
l'API à la bonne santé de PostgreSQL ; le simple ordre de démarrage ne suffit pas à garantir
qu'une base accepte déjà les connexions.

**Mission terminée si :** une commande démarre l'ensemble ; une journée donne 130 EUR ;
redémarrer/recréer les conteneurs en conservant le volume garde les données. Tester aussi
une adresse de source incorrecte et retrouver l'erreur avec les logs.

## Mission 5 — CI et contrôle du merge (1 à 2 h)

Écrire `.github/workflows/ci.yml`. Sur une pull request vers `main`, le workflow doit
installer Python et uv, synchroniser le lockfile puis lancer `uv run pytest`.
Il peut également construire l'image pour vérifier que le Dockerfile reste valide.

Donner un nom clair au job, par exemple `tests`. Attendre qu'il ait été exécuté, puis
configurer ce contrôle comme obligatoire pour fusionner vers `main`, via la protection
de branche ou un ruleset adapté au dépôt. Appliquer la règle au compte qui fera l'exercice,
sans contournement administrateur. La disponibilité varie selon le type de dépôt et le plan GitHub.

Ouvrir une PR avec la formule de calcul volontairement cassée. Observer le contrôle rouge
et le blocage du merge. Corriger, pousser le nouveau commit, constater le contrôle vert,
puis fusionner. Ajouter ensuite un test d'intégration sur une vraie base PostgreSQL en CI
pour couvrir aussi le moteur utilisé dans Compose : les tests SQLite seuls ne le prouvent pas.

**Mission terminée si :** tu peux montrer « bug → échec CI → merge bloqué → correction → merge ».

## Mission 6 — Airflow et reprise d'un import (1 h 30 à 3 h)

L'objectif est un **seul DAG quotidien** :

1. Vérifier que `/ready` répond.
2. Appeler `POST /imports/{date_du_traitement}`.
3. Lire `/sales/summary` et vérifier le résultat attendu pour les données fictives.

Airflow orchestre les tâches et les reprises ; le code métier reste dans l'API.
Dans ce petit exercice les échanges restent petits. Dans un pipeline réel, on préfère
échanger des références de données dans XCom plutôt que des tables volumineuses.

Airflow sera installé dans Linux via Docker, dans une configuration de développement.
Lire le [guide officiel Docker pour Airflow](https://airflow.apache.org/docs/apache-airflow/stable/howto/docker-compose/index.html)
correspondant à la version choisie. Le quick-start complet recommande au moins 4 Go de
mémoire alloués à Docker, idéalement 8 Go ; on vérifiera la machine à cette étape.
Cette configuration est destinée à l'apprentissage. Sa base de métadonnées stocke
l'état des tâches : elle est distincte de la base métier `ventes`, même si les deux utilisent PostgreSQL.
Le lancement Airflow de développement peut être fourni lors de cette mission pour éviter
que son administration absorbe tout le temps d'apprentissage.

Configurer les dépendances des tâches, une date de traitement issue de l'intervalle du DAG,
`catchup=False`, une concurrence limitée et des retries sur les erreurs temporaires.
Utiliser la même date lors d'un retry ; recalculer « aujourd'hui » à chaque tentative
pourrait changer les données visées.

Provoquer une panne de la source, observer la tâche en erreur et sa tentative suivante,
puis remettre la source en état. Relancer une journée réussie : le montant reste 130 EUR.
Les validations de données invalides ne se résolvent pas automatiquement avec plus de retries.

**Mission terminée si :** tu sais déclencher le DAG, lire ses logs, expliquer ses dépendances
et prouver que la reprise ne double pas les ventes.

## Mission 7 — déployer et mettre à jour (1 h 30 à 3 h)

Sur un serveur Linux de démonstration accessible en SSH, installer les composants nécessaires
et déployer une première version manuellement avec Docker Compose. Conserver les secrets sur
le serveur ou dans les secrets GitHub adaptés, avec un utilisateur de déploiement dédié.

Pour ce laboratoire sans authentification applicative, exposer l'API seulement sur
`127.0.0.1` du serveur et y accéder par tunnel SSH. L'interface Airflow reste privée aussi.
L'achat éventuel d'un hébergement dépendra de ce dont tu disposes à cette étape.

Après un merge sur `main` et une nouvelle vérification des tests : construire une image
portant le SHA du commit, la publier dans un registre et déployer **cette même image** par SSH.
Faire les opérations séquentiellement et vérifier `/ready`, puis une synthèse connue.
En cas d'échec, redéployer le tag précédent. Éviter de dépendre uniquement du tag `latest`
pour savoir quelle version tourne. Une recréation simple des conteneurs ne garantit pas
une mise à jour sans aucune interruption.

Publier seulement après succès des contrôles. Les PR servent aux tests ; le workflow de
déploiement s'exécute sur la branche validée, avec les accès nécessaires au serveur.

**Mission terminée si :** tu peux montrer la version déployée, la mettre à jour et revenir
à la précédente. C'est un déploiement de démonstration ; la haute disponibilité et l'exploitation
d'un Airflow de production demandent du travail supplémentaire.

## Ce que tu dois savoir raconter à l'entretien

- Pourquoi une branche et une PR précèdent l'intégration dans `main`.
- Quel bug concret ton test a détecté et comment la CI a empêché son intégration.
- Ce qui est dans l'image, ce qui se configure au lancement et ce qui persiste dans le volume.
- Comment tu diagnostiques une API qui répond mais ne peut plus importer.
- Pourquoi un retry Airflow ne doit pas dupliquer une journée de ventes.
- Quelle différence tu fais entre CI/CD, orchestration de données et asynchrone Python.
- Comment tu identifies une version et reviens à une version précédente.

Tenir un petit journal dans `notes.md` : symptôme, hypothèse, commande de diagnostic,
cause trouvée, correction. Trois incidents bien compris suffisent pour commencer.
