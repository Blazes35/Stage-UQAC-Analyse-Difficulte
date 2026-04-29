from pathlib import Path
import pandas as pd

def import_csv_to_sql(conn, csv_filename, table_name, column_mapping):
    """
    Importe un CSV en filtrant et renommant les colonnes via un mapping.
    column_mapping: Dictionnaire { 'nom_colonne_csv' : 'nom_colonne_sql' }
    """
    if not Path(csv_filename).exists():
        print(f"  [X] Fichier introuvable : {csv_filename}")
        return

    try:
        # Lire uniquement les colonnes du CSV qui sont dans le mapping (les clés du dico)
        csv_columns_to_keep = list(column_mapping.keys())
        df = pd.read_csv(csv_filename, usecols=csv_columns_to_keep)

        # Renommer les colonnes Pandas pour matcher les noms SQL (les valeurs du dico)
        df = df.rename(columns=column_mapping)

        # # --- GESTION DES CAS PARTICULIERS ---
        # # Si on importe dans Videos, vérifier s'il manque le framerate
        if table_name == 'Videos':
            if 'framerate' not in df.columns:
                df['framerate'] = 60  # Valeur par défaut si la colonne n'existe pas dans le CSV
            else:
                df['framerate'] = df['framerate'].fillna(60)  # Remplacer les valeurs vides (NaN) par 60

        # ------------------------------------

        # Insérer dans la base de données
        df.to_sql(table_name, conn, if_exists='append', index=False)
        print(f"  [V] Succès : {len(df)} lignes importées dans '{table_name}' depuis {csv_filename}")

    except Exception as e:
        print(f"  [!] Erreur lors de l'import de {csv_filename} : {e}")
