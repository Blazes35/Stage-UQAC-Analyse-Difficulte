# Base de données SQLite

## 📂 Structure du dossier

Voici les fichiers de la base de données :
```text
projet/
├──database/
    ├── create_database.py
    ├── csv/
        ├── deaths.csv
        ├── events.csv
        ├── levels.csv
        └── videos.csv
    ├── Database.sqlite
    ├── import_csv.py
    ├── insert_values.py
```


### Database
* **`create_database.py`**: Ce fichier génère la base de données dans le fichier `Database.sqlite`.
* **`insert_values.py`**: Un script qui insert les données récoltés pendant notre stage.
* **`import_csv.py`**: Un script qui lit les fichiers dans le dossier `csv\` grâce à Pandas et relie/insère les données dans SQLite.
---

## 🚀 Comment utiliser la base de données

### Étape 1 : Créer la base de données
Ouvrer un terminal et utiliser la commande suivante :
```bash
python create_database.py
```
(Optionnel) Si vous souhaitez insérer nos données récoltées lors de notre stage 
```bash
python insert_values.py
```

### Étape 2 : Importer les données d'analyses (CSV)

Pour importer les données, mettez les tableurs dans le dossier `csv/` et utiliser la fonction `import_csv_to_sql()` de `import_csv.py` (exemple dans `insert_values.py`)
marrera le serveur localement (habituellement à l'adresse `http://127.0.0.1:8000/`).