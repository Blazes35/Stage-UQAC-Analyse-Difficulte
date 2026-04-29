# Application web shiny

## 📂 Structure du dossier

Voici les fichiers principaux de l'application web :
```text
projet/
├──dossier_shiny/
    ├── app.py
    ├── shared.py
    └── www/
        ├── Level_1-1.png
        └── Level_1-2.png
```

### Application web (Shiny for Python)
* **`shared.py`**: La partie backend de l'application. Il gère la connexion à la base de données et prépare, néttoie, formate les données dans un DataFrame Pandas pour le frontend.
* **`app.py`**: La partie frontend. Il construit la partie intéractive du tableau de bord avec deux pages :
    * **Base des Niveaux** : Une vue unifiée des tables contenant les informations d'un niveau.
    * **Logs Vidéos Détallés** : Une vue unifiée chronologique des différentes données récupérées lors des analyses vidéos.
    * Il contient aussi une partie affichant la carte du niveau sélectionné
---

analysed 

## 🚀 Comment utiliser le projet

### Étape 1 : Créer la base de données
Voir le [Database README](../database/README.md)

### Étape 2 : Préparer les images des niveaux

Pour que l'application affiche correctement les images, tu **dois** placer les images dans le dossier `www/`.
* **Convention de nommage** : L'image doit s'appeler exactement comme l'identifiant du niveau avec le mot `Level` devant (e.g., `Level_1-1.png`, `Level_1-2.png`).

### Étape 3 : Lancer l'application web

Une fois les étapes précédentes terminées, lancer le serveur shiny depuis le dossier racine du projet avec :
```bash
shiny run --reload shiny/app.py
```
Cela démarrera le serveur localement (habituellement à l'adresse `http://127.0.0.1:8000/`).