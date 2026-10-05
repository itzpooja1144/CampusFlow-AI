import pandas as pd
import pickle

print("================================")
print("CampusFlow AI Risk Prediction")
print("================================")

# Load trained model
with open("ml/logistic_model.pkl", "rb") as file:
    model = pickle.load(file)


# Example current facility situation
facility_name = "Library"

current_occupancy = 180
capacity = 200

hour = 18
day_of_week = 6


# Calculate occupancy ratio
occupancy_ratio = current_occupancy / capacity


# Create input
input_data = pd.DataFrame({
    "current_occupancy": [current_occupancy],
    "capacity": [capacity],
    "occupancy_ratio": [occupancy_ratio],
    "hour": [hour],
    "day_of_week": [day_of_week]
})


# Prediction
prediction = model.predict(input_data)[0]

probability = model.predict_proba(input_data)[0][1]


print("Facility:", facility_name)
print("Current Occupancy:", current_occupancy)
print("Capacity:", capacity)
print("Occupancy Ratio:", round(occupancy_ratio * 100, 2), "%")

print("--------------------------------")

if prediction == 1:
    print("Risk Status: OVERCROWDING RISK")
else:
    print("Risk Status: NORMAL")

print("Overcrowding Probability:",
      round(probability * 100, 2), "%")