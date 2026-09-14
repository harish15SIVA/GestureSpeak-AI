import pickle
import numpy as np

GESTURES = {
    "food": {"message": "I want food.", "emoji": "🍛"},
    "water": {"message": "I need water.", "emoji": "💧"},
    "tea coffee": {"message": "I want tea or coffee.", "emoji": "☕"},
    "help": {"message": "I need help.", "emoji": "🆘"},
    "yes": {"message": "Yes.", "emoji": "👍"},
    "no": {"message": "No.", "emoji": "👎"},
    "please": {"message": "Please.", "emoji": "🙏"},
    "want that": {"message": "I want that.", "emoji": "☝️"},
    "okay": {"message": "I am okay.", "emoji": "👌"},
    "hello": {"message": "Hello. Please notice me.", "emoji": "👋"},
}

# Load trained ML model
with open("gesture_model.pkl", "rb") as file:
    model = pickle.load(file)


def extract_features(landmarks):
    """
    Convert 21 MediaPipe landmarks into
    63 features: x1,y1,z1,...,x21,y21,z21
    """

    features = []

    for point in landmarks:
        # Supports MediaPipe landmark objects
        if hasattr(point, "x"):
            features.extend([point.x, point.y, point.z])

        # Supports tuples/lists
        elif len(point) >= 3:
            features.extend([point[0], point[1], point[2]])

        elif len(point) == 2:
            # Temporary fallback
            features.extend([point[0], point[1], 0.0])

    return features


def classify(hands_data):
    """
    ML-based gesture classification.

    Returns:
        gesture, confidence, hands_count
    """

    hands_count = len(hands_data)

    if hands_count == 0:
        return "UNKNOWN", 0.0, 0

    best_gesture = "UNKNOWN"
    best_confidence = 0.0

    for hand in hands_data:

        landmarks = hand["landmarks"]

        features = extract_features(landmarks)

        # Model expects 63 features
        if len(features) != 63:
            print(f"Invalid feature count: {len(features)}")
            continue

        X = np.array(features).reshape(1, -1)

        # Prediction
        prediction = model.predict(X)[0]

        # Confidence
        probabilities = model.predict_proba(X)[0]
        confidence = float(np.max(probabilities))

        if confidence > best_confidence:
            best_gesture = str(prediction)
            best_confidence = confidence

    return best_gesture, best_confidence, hands_count


def gesture_payload(key, confidence, hands_count):

    key_lower = key.lower()

    info = GESTURES.get(
        key_lower,
        {
            "message": "Gesture not recognized.",
            "emoji": "🤔"
        }
    )

    if key == "UNKNOWN":
        message = (
            "No hand detected."
            if hands_count == 0
            else "Gesture not recognized. Hold your hand clearly."
        )
    else:
        message = info["message"]

    return {
        "ok": True,
        "gesture": key,
        "message": message,
        "emoji": info["emoji"],
        "confidence": round(float(confidence), 2),
        "hands": hands_count,
    }