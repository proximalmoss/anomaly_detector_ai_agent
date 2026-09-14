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

def update_column_stats(sheet_id: str, column_name: str, new_value: float):
    conn=get_connection()
    cursor=conn.cursor()

    cursor.execute("""
        SELECT count, mean, m2 FROM column_stats
        where sheet_id= ? AND column_name= ?
    """, (sheet_id, column_name))
    row=cursor.fetchone()

    if row is None:
        count=1
        mean=new_value
        m2=0.0
    else:
        old_count, old_mean, old_m2=row
        count=old_count+1
        delta=new_value-old_mean
        mean=old_mean+delta / count
        delta2=new_value-mean
        m2=old_m2 + delta * delta2

    cursor.execute("""
        INSERT INTO column_stats(sheet_id, column_name, count, mean, m2)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(sheet_id, column_name)
        DO UPDATE SET count = ?, mean= ?, m2= ?
    """, (sheet_id, column_name, count, mean, m2, count, mean, m2))

    conn.commit()
    conn.close()

# test block
if __name__=="__main__":
    init_db()
    test_sheet_id="test_sheet_123"
    print("Before any updates:", get_column_stats(test_sheet_id, "Amount"))

    for value in [21, 22, 23, 24, 25, 999999]:
        update_column_stats(test_sheet_id, "Amount", value)
        print(f"After adding {value}:", get_column_stats(test_sheet_id, "Amount"))