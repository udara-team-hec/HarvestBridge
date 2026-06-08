import sqlite3

conn = sqlite3.connect("data/harvestbridge.db")

tables = conn.execute(
    "SELECT name FROM sqlite_master WHERE type='table'"
).fetchall()
print("Tables:", tables)

cols = conn.execute(
    "PRAGMA table_info(farmers_registry)"
).fetchall()
print("farmers_registry columns:", cols)

conn.close()