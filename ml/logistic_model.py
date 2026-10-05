import pandas as pd
import pickle

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix


print("================================")
print("CampusFlow Logistic Regression")
print("================================")


# Load dataset
df = pd.read_csv("data/logistic_dataset.csv")


# Features
X = df[
    [
        "current_occupancy",
        "capacity",
        "occupancy_ratio",
        "hour",
        "day_of_week"
    ]
]


# Target
y = df["overcrowding"]


# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)


print("Training rows:", len(X_train))
print("Testing rows:", len(X_test))


# Create model
model = LogisticRegression(
    max_iter=1000
)


# Train
model.fit(X_train, y_train)


# Predict
y_pred = model.predict(X_test)


# Accuracy
accuracy = accuracy_score(
    y_test,
    y_pred
)


print("--------------------------------")
print("Accuracy:", round(accuracy, 3))
print("--------------------------------")


# Classification report
print("\nClassification Report:")
print(
    classification_report(
        y_test,
        y_pred
    )
)


# Confusion matrix
print("Confusion Matrix:")
print(
    confusion_matrix(
        y_test,
        y_pred
    )
)


# Save model
with open(
    "ml/logistic_model.pkl",
    "wb"
) as file:

    pickle.dump(
        model,
        file
    )


print("\nModel saved successfully!")
print("File: ml/logistic_model.pkl")