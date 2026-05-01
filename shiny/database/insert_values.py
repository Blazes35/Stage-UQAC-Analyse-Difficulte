import sqlite3
from import_csv import import_csv_to_sql


def insert_hardcoded_data(db_filename='Database.sqlite'):
    # Connect to the database
    conn = sqlite3.connect(db_filename)
    cursor = conn.cursor()

    # Enforce foreign key constraints
    cursor.execute("PRAGMA foreign_keys = ON;")

    try:
        csv_path = "../../data/"

        print("Inserting Levels...")
        import_csv_to_sql(conn, f'{csv_path}world.csv', 'Levels',
                          {'Level_ID':'Level_ID', 'Theme':'Theme', 'Coins':'Coins',
                           'Hidden_Boxes':'Hidden_Boxes', 'Brick_Boxes':'Brick_Boxes', 'Mystery_boxes':'Mystery_boxes',
                           'Length':'Length', 'Pixel_Length':'Pixel_Length'}
                          )
        # levels_data = [
        #     ('1-1', 'overworld', 0, 1, 30, 13, 211, 3376),
        #     ('1-2', 'underground', 17, 0, 414, 5, 192, 3072),
        #     ('1-3', 'overworld', 23, 0, 0, 1, 164, 2624),
        #     ('1-4', 'castle', 0, 6, 0, 1, 160, 2560),
        #     # --- ADD THESE PLACEHOLDERS ---
        #     ('2-1', 'needed for next levels', 0, 0, 0, 0, 0, 0),
        #     ('3-1', 'needed for next levels', 0, 0, 0, 0, 0, 0),
        #     ('4-1', 'needed for next levels', 0, 0, 0, 0, 0, 0)
        # ]
        # cursor.executemany('''
        #                    INSERT INTO Levels
        #                    (Level_ID, Theme, Coins, Hidden_Boxes, Brick_Boxes, Mystery_boxes, Length, Pixel_Length)
        #                    VALUES (?, ?, ?, ?, ?, ?, ?, ?   )
        #                    ''', levels_data)

        print("Inserting Sub-Areas...")
        import_csv_to_sql(conn, f'{csv_path}subarea.csv', 'Sub_Areas',
                          {'Level_ID':'Level_ID','Sub_Area':'Sub_Area','Theme':'Theme','Coins':'Coins'}
                          )
        # sub_areas_data = [
        #     ('1-1', 'A', 'underground', 19),
        #     ('1-2', 'A', 'underground', 17),
        #     ('1-2', 'B', 'overworld', 0)
        # ]
        # cursor.executemany('INSERT INTO Sub_Areas VALUES (?, ?, ?, ?)', sub_areas_data)

        print("Inserting Holes...")
        import_csv_to_sql(conn, f'{csv_path}holes.csv', 'Holes',
                          {'Level_ID': 'Level_ID', 'Size': 'Size', 'Number': 'Number'}
                          )
        # holes_data = [
        #     ('1-1', 2, 2),
        #     ('1-1', 3, 1),
        #     ('1-2', 2, 2),
        #     ('1-2', 3, 1),
        #     ('1-2', 7, 2),
        #     ('1-3', 113, 1),
        #     ('1-4', 2, 1),
        #     ('1-4', 3, 2)
        # ]
        # cursor.executemany('INSERT INTO Holes VALUES (?, ?, ?)', holes_data)

        print("Inserting Powerup Dictionary & Placements...")
        import_csv_to_sql(conn, f'{csv_path}powerup-types.csv', 'Powerup_Types',
                          {'Name': 'Name'}
                          )
        import_csv_to_sql(conn, f'{csv_path}level-powerups.csv', 'Level_Powerups',
                          {'Level_ID':'Level_ID','Powerup_ID':'Powerup_ID','Count':'Count'}
                          )

        # powerup_types = [('Stars',), ('1-Up',), ('Mushroom',)]
        # cursor.executemany('INSERT INTO Powerup_Types (Name) VALUES (?)', powerup_types)
        #
        # level_powerups = [
        #     ('1-1', 1, 1),
        #     ('1-1', 2, 1),
        #     ('1-1', 3, 3),
        #     ('1-2', 3, 1),
        #     ('1-3', 3, 1),
        #     ('1-4', 3, 1)
        # ]
        # cursor.executemany('INSERT INTO Level_Powerups VALUES (?, ?, ?)', level_powerups)

        print("Inserting Enemy Dictionary & Placements...")
        import_csv_to_sql(conn, f'{csv_path}enemy-types.csv', 'Enemy_Types',
                          {'Name': 'Name'}
                          )
        import_csv_to_sql(conn, f'{csv_path}level-enemies.csv', 'Level_Enemies',
                          {'Level_ID':'Level_ID','Enemy_ID':'Enemy_ID','Count':'Count'}
                          )


        # enemy_types = [('Goomba',), ('Koopa',), ('Piranha Flower',), ('Flying Koopas',), ('Fire bars',), ('Bowser',)]
        # cursor.executemany('INSERT INTO Enemy_Types (Name) VALUES (?)', enemy_types)
        #
        # level_enemies = [
        #     ('1-1', 1, 16),
        #     ('1-1', 2, 1),
        #     ('1-2', 1, 14),
        #     ('1-2', 2, 4),
        #     ('1-2', 3, 3),
        #     ('1-3', 1, 3),
        #     ('1-3', 2, 3),
        #     ('1-3', 4, 2),
        #     ('1-4', 5, 7),
        #     ('1-4', 6, 1),
        # ]
        # cursor.executemany('INSERT INTO Level_Enemies VALUES (?, ?, ?)', level_enemies)

        print("Inserting Next Levels...")
        import_csv_to_sql(conn, f'{csv_path}next-levels.csv', 'Next_Levels',
                          {'Level_ID': 'Level_ID', 'Level_ID':'Level_ID'}
                          )

        # next_levels = [
        #     ('1-1', '1-2'),
        #     ('1-2', '1-3'),
        #     ('1-2', '2-1'),
        #     ('1-2', '3-1'),
        #     ('1-2', '4-1'),
        #     ('1-3', '1-4'),
        #     ('1-4', '2-1'),
        # ]
        # cursor.executemany('INSERT INTO Next_Levels VALUES (?, ?)', next_levels)

        # Commit all the changes
        conn.commit()
        print("\nSuccess! All known values have been inserted into the database.")

        # ==========================================
        # EXÉCUTION DES IMPORTS AVEC MAPPING
        # ==========================================
        # Format du mapping : {'colonne_dans_le_csv': 'colonne_dans_sql'}

        print("Inserting Videos...")
        import_csv_to_sql(conn, f'{csv_path}videos.csv', 'Videos',
                          {'id': 'id', 'name': 'name'}
                          )
        print("Inserting Events...")
        import_csv_to_sql(conn, f'{csv_path}events.csv', 'Events',
                          {'event': 'event', 'frame': 'frame', 'level': 'level', 'video_id': 'video_id'}
                          )
        print("Inserting Deaths...")
        import_csv_to_sql(conn, f'{csv_path}deaths.csv', 'Deaths',
                          {'type': 'type', 'frame': 'frame', 'level': 'level', 'video_id': 'video_id'}
                          )
        print("Inserting Video Levels...")
        import_csv_to_sql(conn, f'{csv_path}levels.csv', 'Video_Levels',
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