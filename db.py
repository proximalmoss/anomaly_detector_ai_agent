import sqlite3
DB_PATH= "agent_state.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn=get_connection()
    cursor=conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS column_stats (
            sheet_id TEXT NOT NULL,
            column_name TEXT NOT NULL,
            count INTEGER NOT NULL,
            mean REAL NOT NULL,
            m2 REAL NOT NULL,
            PRIMARY KEY (sheet_id, column_name)
        )
    """)
    conn.commit()
    conn.close()

def get_column_stats(sheet_id: str, column_name: str) -> dict:
    conn=get_connection()
    cursor=conn.cursor()

    cursor.execute("""
        SELECT count, mean, m2 FROM column_stats
        WHERE sheet_id= ? and column_name= ?
    """, (sheet_id, column_name))

    row=cursor.fetchone()
    conn.close()

    if row is None:
        return None

    count, mean, m2=row
    variance=m2/count if count>0 else 0
    std_dev=variance**0.5

    return {
        "count":count,
        "mean":mean,
        "std_dev": std_dev,
    }