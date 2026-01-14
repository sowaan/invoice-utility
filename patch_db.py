import sqlite3
import config

def column_exists(cursor, table, column):
    cursor.execute(f"PRAGMA table_info({table})")
    return column in [row[1] for row in cursor.fetchall()]

def main():
    db_path = config.DATABASE_CONFIG["DB_PATH"]
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    table_name = "shipment_numbers"
    column_name = "manifest_input_date"

    if column_exists(cursor, table_name, column_name):
        print(f"[OK] Column '{column_name}' already exists.")
    else:
        print(f"[PATCH] Adding column '{column_name}'...")
        cursor.execute(
            f"ALTER TABLE {table_name} ADD COLUMN {column_name} TEXT"
        )
        conn.commit()
        print(f"[DONE] Column '{column_name}' added successfully.")

    conn.close()

if __name__ == "__main__":
    main()
