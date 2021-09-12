import sqlite3


DB_NAME = "users.db"
conn = sqlite3.connect(DB_NAME)
cur = conn.cursor()

# DB schema
cur.execute(
    "CREATE TABLE email ("
        "email_id INTEGER PRIMARY KEY,"
        "email TEXT UNIQUE NOT NULL"
    ");"
)
cur.execute(
    "CREATE TABLE friend ("
        "email_id1 INTEGER NOT NULL,"
        "email_id2 INTEGER NOT NULL,"
        "FOREIGN KEY (email_id1) REFERENCES email (email_id) ON DELETE CASCADE,"
        "FOREIGN KEY (email_id2) REFERENCES email (email_id) ON DELETE CASCADE,"
        "PRIMARY KEY (email_id1, email_id2)"
    ");"
)
cur.execute(
    "CREATE TABLE subscription ("
        "subscriber_email_id INTEGER NOT NULL,"
        "target_email_id INTEGER NOT NULL,"
        "FOREIGN KEY (subscriber_email_id) REFERENCES email (email_id) ON DELETE CASCADE,"
        "FOREIGN KEY (target_email_id) REFERENCES email (email_id) ON DELETE CASCADE,"
        "PRIMARY KEY (subscriber_email_id, target_email_id)"
    ")"
)
cur.execute(
    "CREATE TABLE block ("
        "blocker_email_id INTEGER NOT NULL,"
        "blocked_email_id INTEGER NOT NULL,"
        "FOREIGN KEY (blocker_email_id) REFERENCES email (email_id) ON DELETE CASCADE,"
        "FOREIGN KEY (blocked_email_id) REFERENCES email (email_id) ON DELETE CASCADE,"
        "PRIMARY KEY (blocker_email_id, blocked_email_id)"
    ")"
)

conn.commit()
conn.close()