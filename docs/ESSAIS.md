# Premiers essais de l’API

- Exécution de pytest : un test réussi.
- Consultation des ventes du 13 septembre 2026 :
  4 ventes, 7 articles et 130 euros de chiffre d’affaires.
- Réimport de la même journée : aucune nouvelle vente enregistrée.
- Après le réimport, le chiffre d’affaires reste à 130 euros.

- CI GitHub Actions : le test de quantité négative détecte la régression.
- Le contrôle Pytest est obligatoire pour fusionner dans main.