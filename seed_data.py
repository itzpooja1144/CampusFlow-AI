import sqlite3
from datetime import datetime

DATABASE = "database/campus.db"

# Realistic starting occupancy for demo
starting_occupancy = {
    "Library": 145,
    "Canteen": 235,
    "Parking": 180,
    "Lab": 68,
    "Admin Office": 42
}

conn = sqlite3.connect(DATABASE)
conn.row_factory = sqlite3.Row

facilities = conn.execute("""
    SELECT id, name, capacity
    FROM facilities
    ORDER BY id
""").fetchall()

for facility in facilities:

    facility_id = facility["id"]
    name = facility["name"]
    capacity = facility["capacity"]

    occupancy = starting_occupancy.get(name, 0)

    # Never exceed capacity
    occupancy = min(occupancy, capacity)

    # Add starting occupancy record
    conn.execute("""
        INSERT INTO occupancy
        (
            facility_id,
            students_in,
            students_out,
            current_occupancy,
            timestamp
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        facility_id,
        occupancy,
        0,
        occupancy,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    print(
        f"{name}: {occupancy}/{capacity} students"
    )

conn.commit()
conn.close()

print()
print("================================")
print("CampusFlow Seed Data Added")
print("================================")