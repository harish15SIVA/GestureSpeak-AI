import pandas as pd
import pickle

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

# Load landmark dataset
df = pd.read_csv("landmarks.csv")

print("Dataset shape:", df.shape)
print("\nClass distribution:")
print(df["label"].value_counts())

# Features and labels
X = df.drop("label", axis=1)
y = df["label"]

# Split dataset
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print("\nTraining samples:", len(X_train))
print("Testing samples:", len(X_test))

# Create Random Forest model
model = RandomForestClassifier(
    n_estimators=200,
    random_state=42,
    class_weight="balanced"
)

# Train
print("\nTraining model...")
model.fit(X_train, y_train)

# Test
y_pred = model.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)

print("\n==============================")
print("MODEL TRAINING COMPLETED")
print("==============================")
print(f"Accuracy: {accuracy * 100:.2f}%")

print("\nClassification Report:")
print(classification_report(y_test, y_pred))

# Save model
with open("gesture_model.pkl", "wb") as file:
    pickle.dump(model, file)

print("\nModel saved as: gesture_model.pkl")