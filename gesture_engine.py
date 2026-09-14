import os
import pickle
import numpy as np

# ---------------------------------------------------------
# Gesture configuration
# ---------------------------------------------------------

GESTURE_CONFIG = {
    "food": {
        "name": "Food",
        "message": "I want food.",
        "emoji": "🍛",
        "is_emergency": False
    },
    "water": {
        "name": "Water",
        "message": "I need water.",
        "emoji": "💧",
        "is_emergency": False
    },
    "tea coffee": {
        "name": "Tea / Coffee",
        "message": "I want tea or coffee.",
        "emoji": "☕",
        "is_emergency": False
    },
    "help": {
        "name": "Help",
        "message": "I need help.",
        "emoji": "🆘",
        "is_emergency": False
    },
    "yes": {
        "name": "Yes",
        "message": "Yes.",
        "emoji": "👍",
        "is_emergency": False
    },
    "no": {
        "name": "No",
        "message": "No.",
        "emoji": "👎",
        "is_emergency": False
    },
    "please": {
        "name": "Please",
        "message": "Please.",
        "emoji": "🙏",
        "is_emergency": False
    },
    "want that": {
        "name": "Want That",
        "message": "I want that.",
        "emoji": "☝️",
        "is_emergency": False
    },
    "okay": {
        "name": "Okay",
        "message": "I am okay.",
        "emoji": "👌",
        "is_emergency": False
    },
    "hello": {
        "name": "Hello",
        "message": "Hello. Please notice me.",
        "emoji": "👋",
        "is_emergency": False
    }
}


# ---------------------------------------------------------
# Load trained Random Forest model
# ---------------------------------------------------------

MODEL_PATH = os.path.join(
    os.path.dirname(__file__),
    "gesture_model.pkl"
)

with open(MODEL_PATH, "rb") as file:
    MODEL = pickle.load(file)

print("ML gesture model loaded successfully.")


# ---------------------------------------------------------
# Temporal stability
# ---------------------------------------------------------

class TemporalGestureSmoother:

    def __init__(self, window_size=10, consistency_ratio=0.7):
        self.window_size = window_size
        self.consistency_ratio = consistency_ratio
        self.history = []

    def add_prediction(self, gesture, confidence):

        self.history.append((gesture, confidence))

        if len(self.history) > self.window_size:
            self.history.pop(0)

        if not self.history:
            return None

        gestures = [item[0] for item in self.history]

        latest_gesture = gestures[-1]

        count = gestures.count(latest_gesture)
        ratio = count / len(gestures)

        if ratio >= self.consistency_ratio:

            info = GESTURE_CONFIG.get(latest_gesture, {})

            return {
                "gesture": latest_gesture,
                "confidence": round(float(confidence), 2),
                "info": info
            }

        return None

    def reset(self):
        self.history.clear()


# ---------------------------------------------------------
# Convert MediaPipe landmarks → 63 ML features
# ---------------------------------------------------------

def _extract_features(landmarks):

    features = []

    for lm in landmarks:

        if hasattr(lm, "x"):
            features.extend([
                float(lm.x),
                float(lm.y),
                float(lm.z)
            ])

        elif isinstance(lm, dict):
            features.extend([
                float(lm["x"]),
                float(lm["y"]),
                float(lm["z"])
            ])

        else:
            features.extend([
                float(lm[0]),
                float(lm[1]),
                float(lm[2])
            ])

    return features


# ---------------------------------------------------------
# ML CLASSIFICATION
# ---------------------------------------------------------

def classify_hand_landmarks(landmarks):

    features = _extract_features(landmarks)

    if len(features) != 63:
        return "UNKNOWN", 0.0

    X = np.array(features, dtype=np.float32).reshape(1, -1)

    prediction = MODEL.predict(X)[0]

    if hasattr(MODEL, "predict_proba"):
        probabilities = MODEL.predict_proba(X)[0]
        confidence = float(np.max(probabilities))
    else:
        confidence = 1.0

    gesture = str(prediction).lower()

    if gesture not in GESTURE_CONFIG:
        return "UNKNOWN", confidence

    return gesture, confidence