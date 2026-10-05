import sqlite3

DATABASE = "database/campus.db"

conn = sqlite3.connect(DATABASE)

# Library ka ID = 1
facility_id = 1

students_in = 50
students_out = 10

current_occupancy = students_in - students_out

conn.execute("""
    INSERT INTO occupancy
    (facility_id, students_in, students_out, current_occupancy)
    VALUES (?, ?, ?, ?)
""", (
    facility_id,
    students_in,
    students_out,
    current_occupancy
))

conn.commit()
conn.close()

print("Occupancy added successfully!")
print("Current Library Occupancy:", current_occupancy)