"""
GestureSpeak AI - Flask Application Server
Connects OpenCV + MediaPipe backend with the modern responsive web application.
"""

import os
import sys
import json
import base64
import time
from flask import Flask, request, jsonify, send_from_directory, Response

try:
    import cv2
    import numpy as np
    HAS_OPENCV = True
except ImportError:
    HAS_OPENCV = False

try:
    import mediapipe as mp
    HAS_MEDIAPIPE = True
except ImportError:
    HAS_MEDIAPIPE = False

import gesture_engine

app = Flask(__name__, static_folder=".", static_url_path="")
smoother = gesture_engine.TemporalGestureSmoother(window_size=10, consistency_ratio=0.7)

# Initialize MediaPipe Hands if available
mp_hands = None
hands_detector = None
if HAS_MEDIAPIPE:
    try:
        mp_hands = mp.solutions.hands
        hands_detector = mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.6,
            min_tracking_confidence=0.6
        )
    except Exception as e:
        print(f"Warning: MediaPipe Hands initialization deferred: {e}")

@app.route("/")
def index():
    return send_from_directory(".", "index.html")

@app.route("/api/health")
def health():
    return jsonify({
        "status": "online",
        "has_opencv": HAS_OPENCV,
        "has_mediapipe": HAS_MEDIAPIPE,
        "gesture_count": len(gesture_engine.GESTURE_CONFIG),
        "engine": "Python + OpenCV + MediaPipe Hybrid"
    })

@app.route("/api/gestures")
def get_gestures():
    return jsonify(gesture_engine.GESTURE_CONFIG)

@app.route("/api/classify", methods=["POST"])
def classify_endpoint():
    data = request.get_json(force=True, silent=True) or {}

    # Case 1: Landmarks array provided directly
    if "landmarks" in data and data["landmarks"]:
        landmarks = data["landmarks"]
        raw_gesture, raw_conf = gesture_engine.classify_hand_landmarks(landmarks)
        stable_result = smoother.add_prediction(raw_gesture, raw_conf)

        if stable_result:
            return jsonify({
                "status": "success",
                "gesture": stable_result["gesture"],
                "confidence": stable_result["confidence"],
                "is_stable": True,
                "message": stable_result["info"].get("message", ""),
                "name": stable_result["info"].get("name", ""),
                "is_emergency": stable_result["info"].get("is_emergency", False)
            })
        else:
            info = gesture_engine.GESTURE_CONFIG.get(raw_gesture, {})
            return jsonify({
                "status": "partial",
                "gesture": raw_gesture,
                "confidence": round(raw_conf, 2),
                "is_stable": False,
                "message": info.get("message", ""),
                "name": info.get("name", "")
            })

    # Case 2: Base64 image provided and OpenCV + MediaPipe available
    elif "image" in data and HAS_OPENCV and HAS_MEDIAPIPE and hands_detector:
        try:
            img_data = data["image"]
            if "," in img_data:
                img_data = img_data.split(",")[1]
            img_bytes = base64.b64decode(img_data)
            nparr = np.frombuffer(img_bytes, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands_detector.process(rgb_frame)

            if results.multi_hand_landmarks:
                landmarks = results.multi_hand_landmarks[0].landmark
                raw_gesture, raw_conf = gesture_engine.classify_hand_landmarks(landmarks)
                stable_result = smoother.add_prediction(raw_gesture, raw_conf)

                lms_list = [{"x": lm.x, "y": lm.y, "z": lm.z} for lm in landmarks]
                info = gesture_engine.GESTURE_CONFIG.get(raw_gesture, {})

                if stable_result:
                    return jsonify({
                        "status": "success",
                        "gesture": stable_result["gesture"],
                        "confidence": stable_result["confidence"],
                        "is_stable": True,
                        "message": stable_result["info"].get("message", ""),
                        "landmarks": lms_list
                    })
                else:
                    return jsonify({
                        "status": "partial",
                        "gesture": raw_gesture,
                        "confidence": round(raw_conf, 2),
                        "is_stable": False,
                        "message": info.get("message", ""),
                        "landmarks": lms_list
                    })
            else:
                smoother.reset()
                return jsonify({
                    "status": "no_hand",
                    "gesture": "UNKNOWN",
                    "confidence": 0.0,
                    "message": "No hand detected in frame"
                })

        except Exception as e:
            return jsonify({"status": "error", "error": str(e)}), 400

    return jsonify({"status": "error", "message": "Invalid input or missing components"}), 400

@app.route("/api/reset", methods=["POST"])
def reset_smoother():
    smoother.reset()
    return jsonify({"status": "reset"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"============================================================")
    print(f" GestureSpeak AI - Python Flask Server")
    print(f" URL: http://localhost:{port}")
    print(f" OpenCV: {'Available' if HAS_OPENCV else 'Not installed (fallback ready)'}")
    print(f" MediaPipe: {'Available' if HAS_MEDIAPIPE else 'Not installed (fallback ready)'}")
    print(f"============================================================")
    app.run(host="0.0.0.0", port=port, debug=False)