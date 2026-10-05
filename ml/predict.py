import pandas as pd
import joblib


# Load trained model
model = joblib.load("ml/linear_model.pkl")


# Example current situation
input_data = pd.DataFrame({
    "hour": [18],
    "minute": [0],
    "day_of_week": [1],
    "is_weekend": [0],
    "inflow": [20],
    "outflow": [10],
    "total_flow": [30]
})


# Predict next 30-minute flow
prediction = model.predict(input_data)


predicted_flow = max(0, round(prediction[0]))


print("================================")
print("CampusFlow AI Prediction")
print("================================")

print("Current Time: 18:00")
print("Current Inflow: 20")
print("Current Outflow: 10")
print("Current Total Flow: 30")

print("--------------------------------")

print(
    "Predicted People Flow "
    "for Next 30 Minutes:",
    predicted_flow
)

