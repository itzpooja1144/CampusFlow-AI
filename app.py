from flask import Flask, render_template, request, redirect
import sqlite3
import joblib
import pandas as pd
import uuid
import os
from datetime import datetime

app = Flask(__name__)

# ============================================================
# DATABASE PATH
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_DIR = os.path.join(BASE_DIR, "database")

# Create database folder if it does not exist
os.makedirs(DATABASE_DIR, exist_ok=True)

DATABASE = os.path.join(DATABASE_DIR, "campus.db")


# ============================================================
# LOAD AI MODELS
# ============================================================

linear_model = joblib.load(
    os.path.join(BASE_DIR, "ml", "linear_model.pkl")
)

logistic_model = joblib.load(
    os.path.join(BASE_DIR, "ml", "logistic_model.pkl")
)


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_db():

    conn = sqlite3.connect(DATABASE)

    conn.row_factory = sqlite3.Row

    return conn


# ============================================================
# CREATE TABLES
# ============================================================

def create_tables():

    conn = get_db()

    # --------------------------------------------------------
    # FACILITIES
    # --------------------------------------------------------

    conn.execute("""
        CREATE TABLE IF NOT EXISTS facilities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            capacity INTEGER NOT NULL
        )
    """)

    # --------------------------------------------------------
    # OCCUPANCY / MOVEMENT HISTORY
    # --------------------------------------------------------

    conn.execute("""
        CREATE TABLE IF NOT EXISTS occupancy (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            facility_id INTEGER NOT NULL,
            students_in INTEGER DEFAULT 0,
            students_out INTEGER DEFAULT 0,
            current_occupancy INTEGER DEFAULT 0,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (facility_id) REFERENCES facilities(id)
        )
    """)

    # --------------------------------------------------------
    # STUDENT SESSIONS
    # --------------------------------------------------------

    conn.execute("""
        CREATE TABLE IF NOT EXISTS student_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            facility_id INTEGER NOT NULL,
            checkin_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            checkout_time DATETIME,
            active INTEGER DEFAULT 1,
            FOREIGN KEY (facility_id) REFERENCES facilities(id)
        )
    """)

    # --------------------------------------------------------
    # STUDENTS
    # --------------------------------------------------------

    conn.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT UNIQUE NOT NULL,
            student_name TEXT,
            facility_id INTEGER,
            inside INTEGER DEFAULT 0,
            checkin_time DATETIME,
            checkout_time DATETIME,
            FOREIGN KEY (facility_id) REFERENCES facilities(id)
        )
    """)

    conn.commit()
    conn.close()


# Create tables when application starts
create_tables()


# ============================================================
# HELPER: CURRENT FACILITY OCCUPANCY
# ============================================================

def get_facility_occupancy(conn):

    rows = conn.execute("""
        SELECT
            f.id,
            f.name,
            f.capacity,

            COUNT(
                CASE
                    WHEN s.inside = 1
                    THEN s.id
                END
            ) AS current_occupancy

        FROM facilities f

        LEFT JOIN students s
            ON s.facility_id = f.id

        GROUP BY f.id
        ORDER BY f.id
    """).fetchall()

    return rows


# ============================================================
# HOME / DASHBOARD
# ============================================================

@app.route("/")
def home():

    conn = get_db()

    facilities_db = get_facility_occupancy(conn)

    # --------------------------------------------------------
    # TOTAL REGISTERED STUDENTS
    # --------------------------------------------------------

    total_students = conn.execute("""
        SELECT COUNT(*)
        FROM students
    """).fetchone()[0]

    # --------------------------------------------------------
    # STUDENTS CURRENTLY INSIDE
    # --------------------------------------------------------

    total_students_inside = conn.execute("""
        SELECT COUNT(*)
        FROM students
        WHERE inside = 1
    """).fetchone()[0]

    # --------------------------------------------------------
    # MOVEMENT IN LAST 30 MINUTES
    # --------------------------------------------------------

    latest_activity = conn.execute("""
        SELECT
            COALESCE(SUM(students_in), 0) AS inflow,
            COALESCE(SUM(students_out), 0) AS outflow

        FROM occupancy

        WHERE timestamp >= datetime('now', '-30 minutes')

        AND (
            students_in > 0
            OR students_out > 0
        )
    """).fetchone()

    inflow = int(
        latest_activity["inflow"] or 0
    )

    outflow = int(
        latest_activity["outflow"] or 0
    )

    total_flow = inflow + outflow

    # --------------------------------------------------------
    # CURRENT TIME
    # --------------------------------------------------------

    now = datetime.now()

    hour = now.hour
    minute = now.minute
    day_of_week = now.weekday()

    is_weekend = 1 if day_of_week >= 5 else 0

    # --------------------------------------------------------
    # LINEAR REGRESSION
    # --------------------------------------------------------

    linear_input = pd.DataFrame([{

        "hour": hour,

        "minute": minute,

        "day_of_week": day_of_week,

        "is_weekend": is_weekend,

        "inflow": inflow,

        "outflow": outflow,

        "total_flow": total_flow

    }])

    try:

        predicted_flow = linear_model.predict(
            linear_input
        )[0]

        predicted_flow = max(
            0,
            round(float(predicted_flow))
        )

    except Exception as e:

        print(
            "Linear Prediction Error:",
            e
        )

        predicted_flow = 0

    # --------------------------------------------------------
    # LOGISTIC REGRESSION
    # FACILITY CROWD RISK
    # --------------------------------------------------------

    facilities = []

    for facility in facilities_db:

        current_occupancy = int(
            facility["current_occupancy"] or 0
        )

        capacity = int(
            facility["capacity"] or 0
        )

        # ----------------------------------------------------
        # OCCUPANCY RATIO
        # ----------------------------------------------------

        if capacity > 0:

            occupancy_ratio = (
                current_occupancy / capacity
            )

        else:

            occupancy_ratio = 0

        # ----------------------------------------------------
        # OCCUPANCY PERCENTAGE
        # IMPORTANT:
        # Defined BEFORE Logistic Prediction
        # ----------------------------------------------------

        occupancy_percentage = round(
            occupancy_ratio * 100,
            1
        )

        # ----------------------------------------------------
        # LOGISTIC MODEL INPUT
        # ----------------------------------------------------

        logistic_input = pd.DataFrame([{

            "current_occupancy":
                current_occupancy,

            "capacity":
                capacity,

            "occupancy_ratio":
                occupancy_ratio,

            "hour":
                hour,

            "day_of_week":
                day_of_week

        }])

        # Default values
        prediction = 0
        probability = 0

        try:

            prediction = logistic_model.predict(
                logistic_input
            )[0]

            probability = (
                logistic_model.predict_proba(
                    logistic_input
                )[0][1] * 100
            )

            probability = round(
                float(probability),
                2
            )

            # ------------------------------------------------
            # RISK STATUS
            # ------------------------------------------------

            if prediction == 1:

                risk_status = "Overcrowding Risk"

            elif occupancy_percentage >= 70:

                risk_status = "Medium Risk"

            else:

                risk_status = "Low Risk"

        except Exception as e:

            print(
                f"Logistic Prediction Error "
                f"for {facility['name']}:",
                e
            )

            risk_status = "Prediction Error"

            probability = 0

        # ----------------------------------------------------
        # CAPACITY REMAINING
        # ----------------------------------------------------

        capacity_remaining = max(
            0,
            capacity - current_occupancy
        )

        # ----------------------------------------------------
        # AI CROWD LEVEL
        # ----------------------------------------------------

        if prediction == 1:

            crowd_level = "High Crowd"

        elif occupancy_percentage >= 70:

            crowd_level = "Medium Crowd"

        else:

            crowd_level = "Low Crowd"

        # ----------------------------------------------------
        # ADD FACILITY DATA
        # ----------------------------------------------------

        facilities.append({

            "id": facility["id"],

            "name": facility["name"],

            "capacity": capacity,

            "current_occupancy":
                current_occupancy,

            "capacity_remaining":
                capacity_remaining,

            "occupancy_percentage":
                occupancy_percentage,

            "crowd_level":
                crowd_level,

            "risk_status":
                risk_status,

            "risk_probability":
                probability

        })

    conn.close()

    # --------------------------------------------------------
    # DASHBOARD
    # --------------------------------------------------------

    return render_template(

        "index.html",

        facilities=facilities,

        predicted_flow=predicted_flow,

        inflow=inflow,

        outflow=outflow,

        total_flow=total_flow,

        total_students_inside=total_students_inside,

        total_students=total_students
    )


# ============================================================
# CHECK-IN
# ============================================================

@app.route(
    "/checkin",
    methods=["GET", "POST"]
)
def checkin():

    conn = get_db()

    # --------------------------------------------------------
    # SHOW CHECK-IN PAGE
    # --------------------------------------------------------

    if request.method == "GET":

        facilities = conn.execute("""
            SELECT
                id,
                name,
                capacity
            FROM facilities
            ORDER BY id
        """).fetchall()

        conn.close()

        return render_template(
            "checkin.html",
            facilities=facilities
        )

    # --------------------------------------------------------
    # FORM DATA
    # --------------------------------------------------------

    student_name = request.form.get(
        "student_name",
        ""
    ).strip()

    student_id = request.form.get(
        "student_id",
        ""
    ).strip()

    if not student_name:

        conn.close()

        return "Student name is required!"

    if not student_id:

        student_id = (
            "STU-"
            + uuid.uuid4().hex[:10].upper()
        )

    try:

        facility_id = int(
            request.form["facility_id"]
        )

    except (ValueError, KeyError):

        conn.close()

        return "Invalid facility!"

    # --------------------------------------------------------
    # FIND STUDENT
    # --------------------------------------------------------

    student = conn.execute("""
        SELECT *
        FROM students
        WHERE student_id = ?
    """, (
        student_id,
    )).fetchone()

    if not student:

        conn.execute("""
            INSERT INTO students
            (
                student_id,
                student_name,
                inside
            )

            VALUES (?, ?, 0)
        """, (
            student_id,
            student_name
        ))

        student = conn.execute("""
            SELECT *
            FROM students
            WHERE student_id = ?
        """, (
            student_id,
        )).fetchone()

    # --------------------------------------------------------
    # STUDENT ALREADY INSIDE
    # --------------------------------------------------------

    if int(student["inside"] or 0) == 1:

        current_facility = conn.execute("""
            SELECT name
            FROM facilities
            WHERE id = ?
        """, (
            student["facility_id"],
        )).fetchone()

        conn.close()

        if current_facility:

            return (
                f"{student_id} is already inside "
                f"{current_facility['name']}. "
                "Please check out first."
            )

        return (
            f"{student_id} is already inside. "
            "Please check out first."
        )

    # --------------------------------------------------------
    # CHECK FACILITY
    # --------------------------------------------------------

    facility = conn.execute("""
        SELECT *
        FROM facilities
        WHERE id = ?
    """, (
        facility_id,
    )).fetchone()

    if not facility:

        conn.close()

        return "Invalid facility!"

    capacity = int(
        facility["capacity"]
    )

    # --------------------------------------------------------
    # CURRENT FACILITY OCCUPANCY
    # --------------------------------------------------------

    current = conn.execute("""
        SELECT COUNT(*)
        FROM students
        WHERE facility_id = ?
        AND inside = 1
    """, (
        facility_id,
    )).fetchone()[0]

    # --------------------------------------------------------
    # CAPACITY CHECK
    # --------------------------------------------------------

    if current >= capacity:

        conn.close()

        return (
            "This facility is currently "
            "at full capacity!"
        )

    # --------------------------------------------------------
    # CURRENT TIME
    # --------------------------------------------------------

    current_time = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    # --------------------------------------------------------
    # UPDATE STUDENT
    # --------------------------------------------------------

    conn.execute("""
        UPDATE students

        SET
            student_name = ?,
            facility_id = ?,
            inside = 1,
            checkin_time = ?,
            checkout_time = NULL

        WHERE student_id = ?
    """, (
        student_name,
        facility_id,
        current_time,
        student_id
    ))

    # --------------------------------------------------------
    # CREATE ACTIVE SESSION
    # --------------------------------------------------------

    conn.execute("""
        INSERT INTO student_sessions
        (
            student_id,
            facility_id,
            checkin_time,
            checkout_time,
            active
        )

        VALUES (?, ?, ?, NULL, 1)
    """, (
        student_id,
        facility_id,
        current_time
    ))

    # --------------------------------------------------------
    # SAVE CHECK-IN FLOW
    # --------------------------------------------------------

    conn.execute("""
        INSERT INTO occupancy
        (
            facility_id,
            students_in,
            students_out,
            current_occupancy,
            timestamp
        )

        VALUES (?, 1, 0, ?, ?)
    """, (
        facility_id,
        current + 1,
        current_time
    ))

    conn.commit()
    conn.close()

    return redirect("/")


# ============================================================
# CHECK-OUT
# ============================================================

@app.route(
    "/checkout",
    methods=["GET", "POST"]
)
def checkout():

    conn = get_db()

    # --------------------------------------------------------
    # SHOW CHECKOUT PAGE
    # --------------------------------------------------------

    if request.method == "GET":

        facilities = conn.execute("""
            SELECT
                id,
                name,
                capacity
            FROM facilities
            ORDER BY id
        """).fetchall()

        conn.close()

        return render_template(
            "checkout.html",
            facilities=facilities
        )

    # --------------------------------------------------------
    # FORM DATA
    # --------------------------------------------------------

    student_id = request.form.get(
        "student_id",
        ""
    ).strip()

    if not student_id:

        conn.close()

        return "Student ID is required!"

    # --------------------------------------------------------
    # FIND CURRENT STUDENT
    # --------------------------------------------------------

    student = conn.execute("""
        SELECT *
        FROM students

        WHERE student_id = ?
        AND inside = 1
    """, (
        student_id,
    )).fetchone()

    if not student:

        conn.close()

        return (
            "Student is not currently "
            "inside the campus!"
        )

    # --------------------------------------------------------
    # ACTUAL FACILITY
    # --------------------------------------------------------

    actual_facility_id = student[
        "facility_id"
    ]

    if actual_facility_id is None:

        conn.close()

        return (
            "Student location "
            "was not found!"
        )

    actual_facility_id = int(
        actual_facility_id
    )

    # --------------------------------------------------------
    # FIND ACTIVE SESSION
    # --------------------------------------------------------

    session = conn.execute("""
        SELECT id

        FROM student_sessions

        WHERE student_id = ?

        AND facility_id = ?

        AND active = 1

        ORDER BY id DESC

        LIMIT 1
    """, (
        student_id,
        actual_facility_id
    )).fetchone()

    # --------------------------------------------------------
    # CURRENT TIME
    # --------------------------------------------------------

    current_time = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    # --------------------------------------------------------
    # CURRENT FACILITY OCCUPANCY
    # --------------------------------------------------------

    current = conn.execute("""
        SELECT COUNT(*)

        FROM students

        WHERE facility_id = ?

        AND inside = 1
    """, (
        actual_facility_id,
    )).fetchone()[0]

    new_occupancy = max(
        0,
        current - 1
    )

    # --------------------------------------------------------
    # UPDATE STUDENT
    # --------------------------------------------------------

    conn.execute("""
        UPDATE students

        SET
            inside = 0,
            facility_id = NULL,
            checkout_time = ?

        WHERE student_id = ?
    """, (
        current_time,
        student_id
    ))

    # --------------------------------------------------------
    # CLOSE SESSION
    # --------------------------------------------------------

    if session:

        conn.execute("""
            UPDATE student_sessions

            SET
                active = 0,
                checkout_time = ?

            WHERE id = ?
        """, (
            current_time,
            session["id"]
        ))

    # --------------------------------------------------------
    # SAVE CHECK-OUT FLOW
    # --------------------------------------------------------

    conn.execute("""
        INSERT INTO occupancy
        (
            facility_id,
            students_in,
            students_out,
            current_occupancy,
            timestamp
        )

        VALUES (?, 0, 1, ?, ?)
    """, (
        actual_facility_id,
        new_occupancy,
        current_time
    ))

    conn.commit()
    conn.close()

    return redirect("/")


# ============================================================
# STUDENT LOCATIONS
# ============================================================

@app.route("/students")
def students():

    conn = get_db()

    student_rows = conn.execute("""
        SELECT

            s.student_id,

            s.student_name,

            s.inside,

            s.checkin_time,

            s.checkout_time,

            f.name AS facility_name

        FROM students s

        LEFT JOIN facilities f
            ON s.facility_id = f.id

        ORDER BY s.student_id
    """).fetchall()

    total_students = conn.execute("""
        SELECT COUNT(*)
        FROM students
    """).fetchone()[0]

    total_inside = conn.execute("""
        SELECT COUNT(*)
        FROM students
        WHERE inside = 1
    """).fetchone()[0]

    conn.close()

    return render_template(

        "students.html",

        students=student_rows,

        total_students=total_students,

        total_inside=total_inside
    )


# ============================================================
# ANALYTICS
# ============================================================

@app.route("/analytics")
def analytics():

    # --------------------------------------------------------
    # LOAD DATASET
    # --------------------------------------------------------

    df = pd.read_csv(
        os.path.join(
            BASE_DIR,
            "data",
            "calit2_ml.csv"
        )
    )

    chart_data = df.tail(30).copy()

    latest = df.iloc[-1]

    inflow = int(
        latest["inflow"]
    )

    outflow = int(
        latest["outflow"]
    )

    current_flow = int(
        latest["total_flow"]
    )

    # --------------------------------------------------------
    # LINEAR PREDICTION
    # --------------------------------------------------------

    try:

        now = datetime.now()

        prediction_input = pd.DataFrame([{

            "hour":
                now.hour,

            "minute":
                0
                if now.minute < 30
                else 30,

            "day_of_week":
                now.weekday(),

            "is_weekend":
                1
                if now.weekday() >= 5
                else 0,

            "inflow":
                inflow,

            "outflow":
                outflow,

            "total_flow":
                current_flow

        }])

        predicted_flow = int(
            max(
                0,
                round(
                    linear_model.predict(
                        prediction_input
                    )[0]
                )
            )
        )

    except Exception as e:

        print(
            "Analytics prediction error:",
            e
        )

        predicted_flow = 0

    # --------------------------------------------------------
    # DATABASE
    # --------------------------------------------------------

    conn = get_db()

    facilities = get_facility_occupancy(
        conn
    )

    # --------------------------------------------------------
    # TOTAL STUDENTS
    # --------------------------------------------------------

    total_students_inside = conn.execute("""
        SELECT COUNT(*)
        FROM students
        WHERE inside = 1
    """).fetchone()[0]

    total_students = conn.execute("""
        SELECT COUNT(*)
        FROM students
    """).fetchone()[0]

    # --------------------------------------------------------
    # TOTAL CAPACITY / OCCUPANCY
    # --------------------------------------------------------

    total_capacity = 0

    total_occupancy = 0

    overcrowded_count = 0

    for facility in facilities:

        capacity = int(
            facility["capacity"]
        )

        occupancy = int(
            facility["current_occupancy"]
        )

        total_capacity += capacity

        total_occupancy += occupancy

        if (
            capacity > 0
            and occupancy / capacity >= 0.90
        ):

            overcrowded_count += 1

    if total_capacity > 0:

        campus_percentage = (
            total_occupancy
            / total_capacity
        ) * 100

    else:

        campus_percentage = 0

    conn.close()

    # --------------------------------------------------------
    # ANALYTICS PAGE
    # --------------------------------------------------------

    return render_template(

        "analytics.html",

        predicted_flow=predicted_flow,

        inflow=inflow,

        outflow=outflow,

        current_flow=current_flow,

        total_occupancy=total_occupancy,

        total_students_inside=total_students_inside,

        total_students=total_students,

        total_capacity=total_capacity,

        campus_percentage=round(
            campus_percentage,
            1
        ),

        overcrowded_count=overcrowded_count,

        facilities=facilities,

        chart_labels=
            chart_data["time"].tolist(),

        chart_inflow=
            chart_data["inflow"]
            .astype(int)
            .tolist(),

        chart_outflow=
            chart_data["outflow"]
            .astype(int)
            .tolist(),

        chart_total=
            chart_data["total_flow"]
            .astype(int)
            .tolist()
    )


# ============================================================
# START APPLICATION
# ============================================================

if __name__ == "__main__":

    create_tables()

    # Render provides the PORT environment variable.
    port = int(
        os.environ.get(
            "PORT",
            5000
        )
    )

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )