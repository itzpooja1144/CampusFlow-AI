import sqlite3

DATABASE = "database/campus.db"

DISTRIBUTION = {
    "Library": 145,
    "Canteen": 235,
    "Parking": 180,
    "Lab": 68,
    "Admin Office": 42
}

conn = sqlite3.connect(DATABASE)
conn.row_factory = sqlite3.Row

# Get facility IDs
facilities = {}

rows = conn.execute("""
    SELECT id, name
    FROM facilities
""").fetchall()

for row in rows:
    facilities[row["name"]] = row["id"]

# Check facilities
for name in DISTRIBUTION:

    if name not in facilities:
        print("Facility not found:", name)
        conn.close()
        exit()

# Check existing students
count = conn.execute("""
    SELECT COUNT(*)
    FROM students
""").fetchone()[0]

if count > 0:
    print(f"Students already exist: {count}")
    print("No duplicate students created.")
    conn.close()
    exit()

# Create students
student_number = 1

for facility_name, number_of_students in DISTRIBUTION.items():

    facility_id = facilities[facility_name]

    for i in range(number_of_students):

        student_id = f"STU{student_number:03d}"
        student_name = f"Student {student_number}"

        conn.execute("""
            INSERT INTO students
            (
                student_id,
                student_name,
                facility_id,
                inside
            )
            VALUES (?, ?, ?, 1)
        """, (
            student_id,
            student_name,
            facility_id
        ))

        student_number += 1

conn.commit()

# Verify total
total = conn.execute("""
    SELECT COUNT(*)
    FROM students
""").fetchone()[0]

print()
print("================================")
print("Student Location Data Created")
print("================================")
print("Total Students:", total)

# Show location-wise count
rows = conn.execute("""
    SELECT
        f.name,
        COUNT(s.id) AS total
    FROM facilities f
    LEFT JOIN students s
        ON s.facility_id = f.id
        AND s.inside = 1
    GROUP BY f.id, f.name
    ORDER BY f.id
""").fetchall()

print()

for row in rows:
    print(
        f"{row['name']}: "
        f"{row['total']} students"
    )

conn.close()