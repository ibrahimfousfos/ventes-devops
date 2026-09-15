# Publication de l'image et déploiement local

Le workflow lance les tests sur les pull requests et sur `main`. Après une
fusion sur `main`, il publie l'image de l'application dans le registre GitHub
Container Registry (GHCR), uniquement si les tests réussissent.

Le lancement de cette image sur le PC reste manuel. Ce laboratoire démontre
une CI, une publication automatique d'image et un déploiement local choisi
par l'utilisateur. Il ne démontre pas un déploiement automatique en production.

## Fichiers

| Fichier | Utilité |
| --- | --- |
| `.github/workflows/tests.yml` | Déclenche les tests puis, sur `main`, la construction et la publication. |
| `Dockerfile` | Recette utilisée par GitHub pour construire l'image de l'application. |
| `compose.yaml` | Définit l'API, la source, PostgreSQL et Airflow. |
| `compose.registry.yaml` | Sélectionne l'image publiée pour l'API et la source. |

`compose.registry.yaml` s'utilise avec `compose.yaml` : le deuxième fichier
remplace la valeur `image` des deux services. Les autres réglages viennent du
premier fichier. Les ventes restent dans le volume PostgreSQL existant.

## Comprendre le workflow YAML

| Élément | Sens |
| --- | --- |
| `on` | Événements qui déclenchent le workflow : pull request ou push sur `main`. |
| `jobs` | Groupes de commandes exécutés par GitHub Actions. |
| `runs-on: ubuntu-latest` | Machine Linux fournie par GitHub pour exécuter le job. |
| `steps` | Actions et commandes exécutées dans l'ordre au sein d'un job. |
| `uses` | Réutilise une action, par exemple récupérer le code ou installer `uv`. |
| `run` | Exécute une commande shell ; ici les commandes s'exécutent sous Linux. |
| `needs: tests` | Le job de publication attend la réussite des tests. |
| `if` du job `image` | Autorise la publication pour les pushes sur `main` uniquement. |
| `packages: write` | Autorise ce job à publier dans le registre GitHub. |
| `GITHUB_TOKEN` | Jeton temporaire fourni par GitHub au workflow. Aucun secret à créer pour ce cas. |
| `concurrency` | Évite plusieurs workflows simultanés pour la même référence Git. |

Le nom du contrôle requis reste `Pytest`. Sur une PR, le job `Image Docker` est
normalement marqué `skipped`. Après fusion, le workflow du push sur `main`
exécute `Pytest`, puis `Image Docker`. Les deux jobs récupèrent le commit de
l'événement qui les a déclenchés.

## Tags et versions

L'image reçoit deux tags :

- `ghcr.io/ibrahimfousfos/ventes-devops:dev` : alias mis à jour à chaque publication réussie.
- `ghcr.io/ibrahimfousfos/ventes-devops:sha-<commit>` : permet de retrouver le commit associé à cette construction.

Un tag est une étiquette et peut être réaffecté. Pour identifier exactement le
contenu d'une image, on utilise son digest `sha256:...`. Le tag fondé sur le
commit facilite ici la traçabilité ; il ne rend pas les tags immuables.

## Publier la modification

Après la fusion de la PR Docker/Airflow, dans PowerShell à la racine du projet :

```powershell
git switch main
git pull --ff-only
git switch -c ci/publication-image
```

Remplacer `.github/workflows/tests.yml`, ajouter `compose.registry.yaml` à la
racine et placer cette fiche dans `docs/LIVRAISON.md`. Puis :

```powershell
git add .github/workflows/tests.yml compose.registry.yaml docs/LIVRAISON.md
git commit -m "Publie l'image Docker apres les tests"
git push -u origin ci/publication-image
```

Créer la PR vers `main`. Attendre `Pytest` vert puis fusionner. Dans l'onglet
**Actions**, ouvrir le workflow **CI Python** déclenché sur **main** après cette
fusion. Attendre que **Pytest** et **Image Docker** réussissent.

## Autoriser le téléchargement de l'image de démonstration

La visibilité initiale d'un nouveau package GHCR est privée, même si le dépôt
de code est public. Pour rendre l'image de ce projet de démonstration accessible
sans connexion au registre :

1. Ouvrir **Packages** sur le profil GitHub, puis le package **ventes-devops**.
2. Ouvrir **Package settings**.
3. Dans **Danger Zone**, choisir **Change visibility**, puis **Public**.
4. Saisir le nom demandé et confirmer le changement dans GitHub.

Cela rend l'image téléchargeable par tous, comme le code de ce projet public.
GitHub ne permet pas de repasser ce package en privé après ce changement.

## Déployer la version publiée sur le PC

Après le succès du workflow de publication, récupérer `main`. Le commit choisi
doit correspondre à un workflow de publication réussi :

```powershell
git switch main
git pull --ff-only
$versionVentes = git rev-parse HEAD
$env:VENTES_IMAGE = "ghcr.io/ibrahimfousfos/ventes-devops:sha-$versionVentes"

docker compose -f .\compose.yaml -f .\compose.registry.yaml pull api source
docker compose -f .\compose.yaml -f .\compose.registry.yaml up -d --no-build --wait --wait-timeout 240 api source
docker compose -f .\compose.yaml -f .\compose.registry.yaml ps
```

Dans la colonne `IMAGE`, l'API et la source doivent utiliser l'image
`ghcr.io/ibrahimfousfos/ventes-devops:sha-...`. Le téléchargement et le
redémarrage des conteneurs remplacent leur version en cours d'exécution.

Effectuer un contrôle du fonctionnement de l'image récupérée :

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/ready" | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/imports/2026-09-14" | ConvertTo-Json
Invoke-RestMethod -Uri "http://127.0.0.1:8000/sales/summary?day=2026-09-14" | ConvertTo-Json
```

Attendu sur la base déjà alimentée : `ready`, puis quatre ventes reçues,
zéro nouvelle insertion, quatre ignorées ; enfin quatre ventes, sept articles
et 13 000 centimes. Airflow continue à appeler l'API par `http://api:8000`.

`VENTES_IMAGE` est défini pour le terminal PowerShell courant. Dans un nouveau
terminal, redéfinir cette variable avant de réutiliser le fichier du registre.
Pour relancer avec l'image publiée, conserver les deux options `-f`.

## Retour à une version précédente

Pour une ancienne version déjà publiée, sélectionner son tag ou son digest
dans `VENTES_IMAGE`, puis refaire `pull` et `up` avec les deux fichiers Compose.
Cela remplace le code exécuté. Cela n'annule pas les changements de données :
en production, les migrations et leur compatibilité demandent un traitement
spécifique. Notre laboratoire ne change pas le schéma pendant ce déploiement.

## Ce que tu pourras expliquer après validation

« Une pull request déclenche mes tests. Le contrôle requis empêche de fusionner
si les tests échouent. Après fusion, GitHub teste le commit de main, construit
une image Docker et la publie dans GHCR. Je choisis ensuite sa version et la
lance avec Docker Compose sur mon PC. Airflow orchestre l'import quotidien et
ses reprises. C'est une démonstration locale ; le déploiement en production
n'est pas automatisé dans ce projet. »

La **CI** automatise les vérifications de l'intégration des changements.
La **livraison continue** vise à disposer d'une version validée et déployable,
avec une décision possible avant sa mise en production. Le **déploiement
continu** automatise aussi cette mise en production après validation. La
publication d'une image est une étape de la chaîne, pas la preuve à elle seule
d'un processus complet de livraison ou de déploiement continu.

## Sources officielles

- [Publier une image avec GitHub Actions](https://docs.github.com/en/actions/tutorials/publish-packages/publish-docker-images)
- [Jetons, tags et visibilité du registre](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
- [Modifier la visibilité d'un package](https://docs.github.com/en/packages/learn-github-packages/configuring-a-packages-access-control-and-visibility)
- [Combiner deux fichiers Compose](https://docs.docker.com/compose/how-tos/multiple-compose-files/merge/)
