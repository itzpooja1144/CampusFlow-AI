import pandas as pd
import random

random.seed(42)

facilities = [
    (1, "Library", 200),
    (2, "Canteen", 500),
    (3, "Parking", 300),
    (4, "Lab", 100),
    (5, "Admin Office", 80)
]

rows = []

for facility_id, facility_name, capacity in facilities:

    for day in range(7):

        for hour in range(8, 21):

            # -----------------------------
            # Facility-specific patterns
            # -----------------------------

            if facility_id == 1:       # Library

                base_ratio = 0.55

                if hour >= 14:
                    base_ratio = 0.88

            elif facility_id == 2:     # Canteen

                base_ratio = 0.40

                if 12 <= hour <= 14:
                    base_ratio = 0.92

                elif 17 <= hour <= 19:
                    base_ratio = 0.70

            elif facility_id == 3:     # Parking

                if 8 <= hour <= 10:
                    base_ratio = 0.92
                else:
                    base_ratio = 0.35

            elif facility_id == 4:     # Lab

                if 10 <= hour <= 16:
                    base_ratio = 0.92
                else:
                    base_ratio = 0.30

            else:                       # Admin Office

                if 10 <= hour <= 16:
                    base_ratio = 0.92
                else:
                    base_ratio = 0.20

            # -----------------------------
            # Small realistic variation
            # -----------------------------

            variation = random.uniform(-0.08, 0.08)

            occupancy_ratio = base_ratio + variation

            # Keep ratio within realistic range
            occupancy_ratio = max(
                0.02,
                min(1.05, occupancy_ratio)
            )

            current_occupancy = round(
                capacity * occupancy_ratio
            )

            # -----------------------------
            # Overcrowding target
            # -----------------------------

            if occupancy_ratio >= 0.90:
                overcrowding = 1
            else:
                overcrowding = 0

            rows.append({
                "facility_id": facility_id,
                "facility_name": facility_name,
                "hour": hour,
                "day_of_week": day,
                "current_occupancy": current_occupancy,
                "capacity": capacity,
                "occupancy_ratio": round(
                    occupancy_ratio, 3
                ),
                "overcrowding": overcrowding
            })


# -----------------------------
# Create DataFrame
# -----------------------------

df = pd.DataFrame(rows)


# -----------------------------
# Save dataset
# -----------------------------

df.to_csv(
    "data/logistic_dataset.csv",
    index=False
)


# -----------------------------
# Display information
# -----------------------------

print("================================")
print("CampusFlow Logistic Dataset")
print("================================")

print("Rows:", len(df))
print("Columns:", len(df.columns))

print("\nOvercrowding distribution:")
print(df["overcrowding"].value_counts())

print("\nSample:")
print(df.head())

print("\nSaved successfully!")
print("File: data/logistic_dataset.csv")