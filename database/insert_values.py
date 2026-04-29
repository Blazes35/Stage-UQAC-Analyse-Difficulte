import sqlite3
from import_csv import import_csv_to_sql


def insert_hardcoded_data(db_filename='Database.sqlite'):
    # Connect to the database
    conn = sqlite3.connect(db_filename)
    cursor = conn.cursor()

    # Enforce foreign key constraints
    cursor.execute("PRAGMA foreign_keys = ON;")

    try:
        print("Inserting Levels...")
        levels_data = [
            ('1-1', 'overworld', 0, 1, 30, 13, 211, 3376),
            ('1-2', 'underground', 17, 0, 414, 5, 192, 3072),
            ('1-3', 'overworld', 23, 0, 0, 1, 164, 2624),
            ('1-4', 'castle', 0, 6, 0, 1, 160, 2560),
            # --- ADD THESE PLACEHOLDERS ---
            ('2-1', 'needed for next levels', 0, 0, 0, 0, 0, 0),
            ('3-1', 'needed for next levels', 0, 0, 0, 0, 0, 0),
            ('4-1', 'needed for next levels', 0, 0, 0, 0, 0, 0)
        ]
        cursor.executemany('''
                           INSERT INTO Levels
                           (Level_ID, Theme, Coins, Hidden_Boxes, Brick_Boxes, Mystery_boxes, Length, Pixel_Length)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?   )
                           ''', levels_data)

        print("Inserting Sub-Areas...")
        sub_areas_data = [
            ('1-1', 'A', 'underground', 19),
            ('1-2', 'A', 'underground', 17),
            ('1-2', 'B', 'overworld', 0)
        ]
        cursor.executemany('INSERT INTO Sub_Areas VALUES (?, ?, ?, ?)', sub_areas_data)

        print("Inserting Holes...")
        holes_data = [
            ('1-1', 2, 2),
            ('1-1', 3, 1),
            ('1-2', 2, 2),
            ('1-2', 3, 1),
            ('1-2', 7, 2),
            ('1-3', 113, 1),
            ('1-4', 2, 1),
            ('1-4', 3, 2)
        ]
        cursor.executemany('INSERT INTO Holes VALUES (?, ?, ?)', holes_data)

        print("Inserting Powerup Dictionary & Placements...")
        powerup_types = [('Stars',), ('1-Up',), ('Mushroom',)]
        cursor.executemany('INSERT INTO Powerup_Types (Name) VALUES (?)', powerup_types)

        level_powerups = [
            ('1-1', 1, 1),
            ('1-1', 2, 1),
            ('1-1', 3, 3),
            ('1-2', 3, 1),
            ('1-3', 3, 1),
            ('1-4', 3, 1)
        ]
        cursor.executemany('INSERT INTO Level_Powerups VALUES (?, ?, ?)', level_powerups)

        print("Inserting Enemy Dictionary & Placements...")
        enemy_types = [('Goomba',), ('Koopa',), ('Piranha Flower',), ('Flying Koopas',), ('Fire bars',), ('Bowser',)]
        cursor.executemany('INSERT INTO Enemy_Types (Name) VALUES (?)', enemy_types)

        level_enemies = [
            ('1-1', 1, 16),
            ('1-1', 2, 1),
            ('1-2', 1, 14),
            ('1-2', 2, 4),
            ('1-2', 3, 3),
            ('1-3', 1, 3),
            ('1-3', 2, 3),
            ('1-3', 4, 2),
            ('1-4', 5, 7),
            ('1-4', 6, 1),
        ]
        cursor.executemany('INSERT INTO Level_Enemies VALUES (?, ?, ?)', level_enemies)

        print("Inserting Next Levels...")
        next_levels = [
            ('1-1', '1-2'),
            ('1-2', '1-3'),
            ('1-2', '2-1'),
            ('1-2', '3-1'),
            ('1-2', '4-1'),
            ('1-3', '1-4'),
            ('1-4', '2-1'),
        ]
        cursor.executemany('INSERT INTO Next_Levels VALUES (?, ?)', next_levels)

        # Commit all the changes
        conn.commit()
        print("\nSuccess! All known values have been inserted into the database.")

        # ==========================================
        # EXÉCUTION DES IMPORTS AVEC MAPPING
        # ==========================================
        # Format du mapping : {'colonne_dans_le_csv': 'colonne_dans_sql'}

        import_csv_to_sql(conn, 'csv/videos.csv', 'Videos',
                          {'id': 'id', 'name': 'name'}
                          )

        import_csv_to_sql(conn, 'csv/events.csv', 'Events',
                          {'event': 'event', 'frame': 'frame', 'level': 'level', 'video_id': 'video_id'}
                          )

        import_csv_to_sql(conn, 'csv/deaths.csv', 'Deaths',
                          {'type': 'type', 'frame': 'frame', 'level': 'level', 'video_id': 'video_id'}
                          )

        import_csv_to_sql(conn, 'csv/levels.csv', 'Video_Levels',
                          {'frame': 'frame', 'level': 'level', 'video_id': 'video_id'}
                          )

        # Commit all the changes
        conn.commit()
        print("\nMise à jour de la base de données terminée !")

    except sqlite3.IntegrityError as e:
        print(f"\nDatabase Constraint Error: {e}")
        print("Note: If you already ran this script once, the data is already there and Primary Keys prevent duplicates.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        conn.rollback()
    finally:
        conn.close()


if __name__ == "__main__":
    insert_hardcoded_data()