import sqlite3
import pandas as pd
from pathlib import Path

# Get the directory of the current file
app_dir = Path(__file__).parent

# Define the path to your SQLite database
db_path = app_dir / "Database.sqlite"


def load_level_data():
    """Connects to the database and retrieves a fully joined view of all level properties."""
    try:
        conn = sqlite3.connect(db_path)

        # Using CTEs to pre-group 1-to-many relationships to prevent duplicates
        query = """
                WITH Enemy_Data AS (SELECT Level_ID, \
                                           GROUP_CONCAT(ET.Name || ' (' || LE.Count || ')', ', ') AS Enemy_List \
                                    FROM Level_Enemies LE \
                                             JOIN Enemy_Types ET ON LE.Enemy_ID = ET.Enemy_ID \
                                    GROUP BY Level_ID),
                     Powerup_Data AS (SELECT Level_ID, \
                                             GROUP_CONCAT(PT.Name || ' (' || LP.Count || ')', ', ') AS Powerup_List \
                                      FROM Level_Powerups LP \
                                               JOIN Powerup_Types PT ON LP.Powerup_ID = PT.Powerup_ID \
                                      GROUP BY Level_ID),
                     Sub_Area_Data AS (SELECT Level_ID, \
                                              GROUP_CONCAT(Sub_Area || ' [' || Theme || ']', ', ') AS Sub_Area_List \
                                       FROM Sub_Areas \
                                       GROUP BY Level_ID),
                     Next_Level_Data AS (SELECT Level_ID, GROUP_CONCAT(NextLevel_ID, ', ') AS Next_Level_List \
                                         FROM Next_Levels \
                                         GROUP BY Level_ID),
                     Hole_Data AS (SELECT Level_ID, \
                                          GROUP_CONCAT('Size ' || Size || ' (' || Number || ')', ', ') AS Hole_List \
                                   FROM Holes \
                                   GROUP BY Level_ID)
                SELECT L.Level_ID, \
                       L.Theme, \
                       L.Coins, \
                       L.Hidden_Boxes, \
                       L.Brick_Boxes, \
                       L.Mystery_boxes, \
                       L.Length, \
                       L.Pixel_Length, \
                       COALESCE(ED.Enemy_List, 'None')       AS Enemies, \
                       COALESCE(PD.Powerup_List, 'None')     AS Powerups, \
                       COALESCE(SAD.Sub_Area_List, 'None')   AS Sub_Areas, \
                       COALESCE(NLD.Next_Level_List, 'None') AS Next_Levels, \
                       COALESCE(HD.Hole_List, 'None')        AS Holes, \
                       COALESCE(P.Normal, 0)                 AS Normal_Pipes, \
                       COALESCE(P.Special, 0)                AS Special_Pipes
                FROM Levels L
                         LEFT JOIN Enemy_Data ED ON L.Level_ID = ED.Level_ID
                         LEFT JOIN Powerup_Data PD ON L.Level_ID = PD.Level_ID
                         LEFT JOIN Sub_Area_Data SAD ON L.Level_ID = SAD.Level_ID
                         LEFT JOIN Next_Level_Data NLD ON L.Level_ID = NLD.Level_ID
                         LEFT JOIN Hole_Data HD ON L.Level_ID = HD.Level_ID
                         LEFT JOIN Pipes P ON L.Level_ID = P.Level_ID; \
                """

        # ... (rest of your SQL query above)
        df = pd.read_sql_query(query, conn)
        conn.close()

        # --- NEW CODE: Format cells for better readability ---
        list_columns = ['Enemies', 'Powerups', 'Sub_Areas', 'Next_Levels', 'Holes']
        for col in list_columns:
            if col in df.columns:
                # 1. Use regex to replace commas (with or without spaces) with a double newline
                df[col] = df[col].astype(str).str.replace(r',\s*', '\n', regex=True)

                # 2. Replace regular spaces with non-breaking spaces (\xa0)
                df[col] = df[col].str.replace(' ', '\xa0')

                # 3. Replace regular hyphens with non-breaking hyphens (\u2011)
                df[col] = df[col].str.replace('-', '\u2011')
        # -------------------------------------------------------------------

        return df

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return pd.DataFrame(columns=['Level_ID', 'Theme', 'Error'])


# Load the dataframe to be shared with app.py
df = load_level_data()