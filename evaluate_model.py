import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)

# Load dataset
df = pd.read_csv("landmarks.csv")

X = df.drop(columns=["label"])
y = df["label"]

# Same 80/20 split used for validation
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

# Load trained model
model = joblib.load("gesture_model.pkl")

# Predict
y_pred = model.predict(X_test)

# Accuracy
accuracy = accuracy_score(y_test, y_pred)

print("\n==============================")
print(" GESTURESPEAK AI ML EVALUATION")
print("==============================")

print(f"\nAccuracy: {accuracy * 100:.2f}%")

print("\nClassification Report:")
print(classification_report(y_test, y_pred))

print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred))

print("\nClass Labels:")
print(model.classes_)