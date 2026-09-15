# Airflow : la demonstration et les notions pour l'entretien

## Ce que l'on ajoute

Airflow appelle l'API FastAPI existante. Le DAG `ventes_quotidiennes` contient
trois taches successives : verifier l'API, importer une journee, puis controler
le bilan. Le calcul et le stockage des ventes restent dans l'application.

| Element | Role dans ce laboratoire |
| --- | --- |
| `dags/ventes_quotidiennes.py` | Definit les taches, leurs dependances, la planification et les reprises. |
| Service Compose `airflow` | Execute Airflow 3.3.1 en mode `standalone`. |
| `http://api:8000` | Adresse de FastAPI depuis le reseau Docker. |
| `http://127.0.0.1:8080` | Interface Airflow accessible depuis le PC. |
| Volume `airflow-state` | Configuration, journaux et base SQLite des etats d'Airflow. |
| Volume `ventes-data` | Donnees commerciales dans PostgreSQL. |

Le mode `standalone` regroupe les composants pour apprendre en local. En
production, on les deploierait separement, avec une base de metadonnees adaptee,
une authentification d'entreprise et une supervision.

## Lancer

Dans PowerShell, a la racine du projet `ventes-devops`, apres avoir remplace
`compose.yaml` et ajoute `dags/ventes_quotidiennes.py` :

```powershell
docker compose up -d --wait --wait-timeout 240
docker compose ps
```

L'image Airflow est telechargee au premier lancement. Aucun `uv add airflow`
n'est necessaire : Airflow a son propre environnement dans son conteneur.

Pour lire le mot de passe du compte `admin` :

```powershell
docker compose exec airflow cat /opt/airflow/simple_auth_manager_passwords.json.generated
```

Ouvrir <http://127.0.0.1:8080> et utiliser le mot de passe genere pour `admin`.
Ce mot de passe reste local ; il n'a pas besoin d'etre copie dans Git.

## Une execution reussie

1. Ouvrir le DAG `ventes_quotidiennes` dans la liste des DAGs.
2. Activer le DAG s'il est en pause.
3. Cliquer sur **Trigger** / **Trigger DAG** et renseigner `day = 2026-09-14`.
4. Ouvrir cette execution puis sa vue **Graph**.
5. Ouvrir les **Logs** de `importer_ventes` puis de `verifier_bilan`.

Les trois taches doivent finir en `success`. La date du 14/09 ayant deja ete
importee, un nouvel import doit annoncer `received=4`, `inserted=0`, `skipped=4`.
Le bilan attendu est de quatre ventes, sept articles et 13 000 centimes, soit
130 EUR. Le controle du DAG utilise ces valeurs car notre source est fictive.

Une execution automatique peut egalement apparaitre apres activation : sa date
provient de l'intervalle quotidien du DAG. La date `day` choisie dans le
formulaire concerne uniquement l'execution manuelle correspondante.

## Voir une reprise, une seule fois

Apres une execution reussie :

```powershell
docker compose stop source
```

Relancer le DAG avec `day = 2026-09-14`. `verifier_api` peut reussir car `/ready`
controle la connexion de l'API a la base. `importer_ventes` echoue : la source
HTTP est arretee. Ouvrir ses journaux ; la tache doit passer en `up_for_retry`.
Des que cet etat apparait, remettre la source en marche :

```powershell
docker compose start source
```

Airflow retente la tache apres 30 secondes. Deux nouvelles tentatives sont
autorisees, soit trois essais au maximum. `verifier_bilan` attend le succes de
l'import. Si les essais ont tous ete consommes avant le redemarrage de la
source, declencher une nouvelle execution manuelle.

## Les notions a expliquer

| Notion | Explication avec ce projet |
| --- | --- |
| DAG | Graphe de taches et de dependances, sans cycle. |
| Scheduler | Determine quelles executions et quelles taches doivent demarrer. |
| Executor | Mecanisme charge de lancer les taches ; ici execution locale dans le conteneur Airflow. |
| DAG processor | Lit les fichiers Python et transmet les definitions des DAGs. |
| Schedule | Minuit, heure de Paris ; l'execution traite la journee qui vient de se terminer. |
| `catchup=False` | Ne rattrape pas automatiquement toutes les anciennes journees manquees. |
| `max_active_runs=1` | Limite ce DAG a une execution active a la fois. |
| Retry | Relance une tache ayant echoue, avec une limite et un delai. |
| Idempotence | Rejouer la meme journee ne duplique pas les ventes, grace a la cle unique en base. |
| XCom | Transporte ici le petit resultat de l'import vers la tache suivante, dont la date a verifier. |
| Journaux | Permettent de retrouver la cause d'un echec et le resultat de chaque tentative. |

La planification ne fonctionne que lorsque le PC, Docker et les composants
Airflow tournent. Il n'est pas necessaire d'attendre minuit pour la demonstration
manuelle. Programmer un DAG a minuit ne signifie pas que cette execution
planifiee a deja ete observee.

`asyncio.gather`, deja utilise par l'application, permet d'attendre les reponses
des deux boutiques en concurrence. Airflow, lui, organise les etapes du
traitement et leurs reprises. Dev, IAT, UAT, preproduction et production sont
des environnements ou etapes de validation ; ce ne sont pas des types
d'asynchronisme. Le sens exact d'IAT depend de l'organisation.

## Formulation honnete apres avoir observe les executions

« Pour preparer cet entretien, j'ai utilise une petite API de ventes fournie
comme point de depart. Je l'ai lancee avec Docker Compose et PostgreSQL.
J'ai ajoute un DAG Airflow qui verifie l'API, declenche un import puis controle
le resultat. J'ai observe une execution et une reprise apres indisponibilite
de la source. Les imports peuvent etre rejoues sans doublons. C'est un
laboratoire local, qui m'a permis de comprendre le role des composants. »

Ne mentionner la reprise comme realisee qu'apres l'avoir observee. La CI Python
existe deja ; la publication automatique d'image et le deploiement automatique
restent des etapes distinctes a mettre en place.

## Arret et diagnostic

```powershell
docker compose logs --tail 60 airflow
docker compose stop
```

`stop` conserve les conteneurs et leurs volumes. Pour reprendre le laboratoire :

```powershell
docker compose up -d --wait --wait-timeout 240
```

## Sources officielles

- [Demarrage standalone et connexion](https://airflow.apache.org/docs/apache-airflow/stable/start.html)
- [Intervalles de donnees et planification](https://airflow.apache.org/docs/apache-airflow/stable/authoring-and-scheduling/timetable.html)
- [Parametres et formulaire de declenchement](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/params.html)
