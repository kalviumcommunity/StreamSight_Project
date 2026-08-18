import sqlite3

conn = sqlite3.connect("analytics.db")

tables = conn.execute(
    "SELECT name FROM sqlite_master WHERE type='table'"
).fetchall()

print("DATABASE TABLES:")

for table in tables:
    print("-", table[0])

conn.close()