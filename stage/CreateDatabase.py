import sqlite3


def create_database(db_filename='Database.sqlite'):
    # Connect to SQLite (this creates the file if it doesn't exist)
    conn = sqlite3.connect(db_filename)
    cursor = conn.cursor()

    # Enable foreign key constraints (required in SQLite)
    cursor.execute("PRAGMA foreign_keys = ON;")

    print(f"Creating normalized schema in '{db_filename}'...")

    # ==========================================
    # 1. CORE LEVEL TABLE
    # ==========================================
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS Levels (
                       Level_ID TEXT PRIMARY KEY,
                       Theme TEXT,
                       Coins INTEGER,
                       Hidden_Boxes INTEGER,
                       Brick_Boxes INTEGER,
                       Mystery_boxes INTEGER,
                       Length INTEGER,
                       Pixel_Length INTEGER
                   );
                   ''')

    # ==========================================
    # 2. SUB-AREAS
    # ==========================================
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS Sub_Areas (
                       Level_ID TEXT,
                       Sub_Area TEXT,
                       Theme TEXT,
                       Coins INTEGER,
                       PRIMARY KEY (Level_ID, Sub_Area),
                       FOREIGN KEY (Level_ID) REFERENCES Levels (Level_ID)
                   );
                   ''')

    # ==========================================
    # 3. DICTIONARY TABLES (The "Types")
    # ==========================================
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS Powerup_Types (
                       Powerup_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                       Name TEXT UNIQUE NOT NULL
                   );
                   ''')

    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS Enemy_Types (
                       Enemy_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                       Name TEXT UNIQUE NOT NULL
                   );
                   ''')

    # ==========================================
    # 4. JUNCTION TABLES (The "Placements")
    # ==========================================
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS Level_Powerups (
                       Level_ID TEXT,
                       Powerup_ID INTEGER,
                       Count INTEGER,
                       PRIMARY KEY (Level_ID, Powerup_ID),
                       FOREIGN KEY (Level_ID) REFERENCES Levels (Level_ID),
                       FOREIGN KEY (Powerup_ID) REFERENCES Powerup_Types (Powerup_ID)
                   );
                   ''')

    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS Level_Enemies (
                       Level_ID TEXT,
                       Enemy_ID INTEGER,
                       Count INTEGER,
                        PRIMARY KEY (Level_ID, Enemy_ID),
                       FOREIGN KEY (Level_ID) REFERENCES Levels (Level_ID),
                       FOREIGN KEY (Enemy_ID) REFERENCES Enemy_Types (Enemy_ID)
                   );
                   ''')



    # ==========================================
    # 5. OTHER PLACEMENT TABLES
    # ==========================================
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS Holes (
                       Level_ID TEXT,
                       Size INTEGER,
                       Number INTEGER,
                       PRIMARY KEY (Level_ID, Size),
                       FOREIGN KEY (Level_ID) REFERENCES Levels (Level_ID)
                   );
                   ''')

    # Assuming pipes have generic properties based on your previous CSV
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS Pipes (
                       Level_ID TEXT PRIMARY KEY,
                       Normal INTEGER,
                       Special INTEGER,
                       FOREIGN KEY (Level_ID) REFERENCES Levels (Level_ID)
                   );
                   ''')

    # Assuming pipes have generic properties based on your previous CSV
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS Next_Levels (
                       Level_ID TEXT,
                       NextLevel_ID TEXT,
                       PRIMARY KEY (Level_ID, NextLevel_ID),
                       FOREIGN KEY (Level_ID) REFERENCES Levels (Level_ID)
                       FOREIGN KEY (NextLevel_ID) REFERENCES Levels (Level_ID)
                   );
                   ''')

    # Commit changes and close the connection
    conn.commit()
    conn.close()

    print("Database schema created successfully!")


# Run the function
if __name__ == "__main__":
    create_database()