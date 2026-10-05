import sqlite3

DATABASE = "database/campus.db"

conn = sqlite3.connect(DATABASE)

facilities = [
    ("Library", 200),
    ("Canteen", 500),
    ("Parking", 300),
    ("Lab", 100),
    ("Admin Office", 80)
]

for name, capacity in facilities:
    conn.execute(
        "INSERT INTO facilities (name, capacity) VALUES (?, ?)",
        (name, capacity)
    )

conn.commit()
conn.close()

print("Facilities added successfully!")