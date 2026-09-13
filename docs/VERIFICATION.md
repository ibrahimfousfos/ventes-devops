# État du kit livré — 12 septembre 2026

## Vérifié

- Installation avec `uv sync`, environnement Python 3.12 sous Linux et lockfile `uv.lock`.
- Le test d'exemple livré passe avec `uv run pytest`.
- **21 cas de contrôle** ont été exécutés lors de la préparation : validation, calcul,
  idempotence, stockage, routes, erreurs HTTP et collecte concurrente. Cette suite de
  contrôle inclut le test d'exemple ; le kit contient ce premier test pour que tu écrives
  et comprennes les autres au cours des missions.
- Deux serveurs Uvicorn ont été réellement démarrés et ont communiqué par HTTP local :
  source fictive et API principale, avec une base SQLite temporaire.
- L'import réel donne 4 ventes, 7 articles et 13 000 centimes. Le réimport ne double pas les ventes.
- Les modes `invalid`, `unavailable` et `timeout` de la source donnent respectivement
  502, 503 et 503, avec zéro vente ajoutée à la journée de test en erreur.
- Les données restent consultables après un redémarrage réel de l'API.
- `/docs` et `/ready` répondent avec succès.

Le client de test des bibliothèques installées émet deux avertissements internes de
dépréciation. Ils n'ont pas empêché les tests de réussir ; aucun avertissement n'a été masqué.

## À réaliser pendant l'apprentissage

- Exécution sur ton PC Windows : les commandes PowerShell sont fournies mais n'ont pas
  été exécutées dans un environnement Windows lors de cette préparation.
- Connexion à PostgreSQL : le chemin de code est fourni ; un serveur PostgreSQL réel
  n'a pas été utilisé pour ces vérifications.
- Dockerfile, Docker Compose, contrôles de PR, CI, registre, Airflow et déploiement distant :
  ce sont les missions à construire, pas des étapes déjà terminées.

Le résultat testé à cette livraison est donc **le socle métier et l'API locale**, prêt
à servir de support au parcours. Le kit n'est pas présenté comme une infrastructure de production.

