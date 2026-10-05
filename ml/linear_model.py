import pandas as pd
import joblib

from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score


# Load ML dataset
data = pd.read_csv("data/calit2_ml.csv")


# Input features
X = data[
    [
        "hour",
        "minute",
        "day_of_week",
        "is_weekend",
        "inflow",
        "outflow",
        "total_flow"
    ]
]


# Target
y = data["next_flow"]


# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)


# Create Linear Regression model
model = LinearRegression()


# Train model
model.fit(X_train, y_train)


# Test model
predictions = model.predict(X_test)


# Evaluation
mae = mean_absolute_error(y_test, predictions)
r2 = r2_score(y_test, predictions)


print("================================")
print("CampusFlow Linear Regression")
print("================================")

print("Training rows:", len(X_train))
print("Testing rows:", len(X_test))

print("Mean Absolute Error:", round(mae, 2))
print("R2 Score:", round(r2, 3))


# Save model
joblib.dump(
    model,
    "ml/linear_model.pkl"
)


print("\nModel saved successfully!")
print("File: ml/linear_model.pkl")