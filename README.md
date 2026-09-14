````
# GestureSpeak AI 🤟

### AI-Based Hand Gesture Communication System for Non-Speaking Individuals

> **AI Immersion C29 Project Deliverable** | Review-2 Prototype | Assistive Communication

---

## 🌟 Overview

**GestureSpeak AI** is an AI-powered assistive communication web application designed to help non-speaking individuals communicate common everyday needs through predefined hand gestures.

The system uses a webcam to capture hand movements, **MediaPipe Hands** to extract 21 hand landmarks, and a **Random Forest machine-learning classifier** to recognize 10 predefined gestures.

The recognized gesture is converted into meaningful text and can optionally be vocalized using the browser's **Web Speech API**.

---

## 🎯 Project Objective

The objective of GestureSpeak AI is to provide a simple, affordable, and accessible communication interface using:

- Computer Vision
- Machine Learning
- Web Technologies
- Accessibility-focused design

The project focuses on a predefined set of practical everyday gestures rather than attempting complete sign-language translation.

---

## 🔄 Recognition Pipeline

```text
Webcam
   ↓
Browser Camera Capture
   ↓
Flask Backend
   ↓
OpenCV Frame Processing
   ↓
MediaPipe Hands
   ↓
21 Hand Landmarks
   ↓
63 Landmark Features
   ↓
Random Forest ML Classifier
   ↓
Gesture + Confidence
   ↓
Temporal Stability Confirmation
   ↓
Text Message
   ↓
Optional Browser Text-to-Speech
````

---

## ✋ 10 Predefined Communication Gestures

| #GestureIconCategoryGesture DescriptionOutput |               |     |           |                                                           |                                     |
| --------------------------------------------- | ------------- | --- | --------- | --------------------------------------------------------- | ----------------------------------- |
| 1                                             | **HELLO**     | 👋  | Social    | Open hand raised with all 5 fingers upright               | "Hello, nice to meet you!"          |
| 2                                             | **YES**       | 👍  | Response  | Thumb pointing upward with remaining fingers curled       | "Yes."                              |
| 3                                             | **NO**        | 👎  | Response  | Thumb pointing downward with remaining fingers curled     | "No."                               |
| 4                                             | **HELP**      | ✌️  | Need      | Index and middle fingers extended in a V-sign             | "I need help."                      |
| 5                                             | **WATER**     | 💧  | Need      | Three fingers extended upward with thumb and pinky curled | "I need water."                     |
| 6                                             | **FOOD**      | 🍽️ | Need      | Pinch gesture with fingertips gathered near the thumb     | "I want food."                      |
| 7                                             | **STOP**      | ✋   | Command   | Open flat palm facing the camera                          | "Please stop."                      |
| 8                                             | **THANK YOU** | 🙏  | Social    | Index and middle fingers extended together side-by-side   | "Thank you."                        |
| 9                                             | **OKAY**      | 👌  | Response  | Thumb and index fingertips forming an OK circle           | "Everything is okay."               |
| 10                                            | **EMERGENCY** | 🚨  | Emergency | Clenched fist held steadily toward the camera             | "Emergency! I need immediate help." |

---

# 🧠 Machine Learning

GestureSpeak AI uses a **Random Forest classifier** trained on hand-landmark features extracted using MediaPipe Hands.

### Feature Extraction

MediaPipe provides **21 hand landmarks**.

Each landmark contains:


```
X coordinate
Y coordinate
Z coordinate
```

Therefore:


```
21 landmarks × 3 coordinates = 63 features
```

These 63 landmark features are used as input to the Random Forest classifier.

---

# 📊 Model Evaluation

The trained model was evaluated using a stratified **80/20 train-test split**.

## Overall Performance

| MetricResult      |            |
| ----------------- | ---------- |
| Gesture Classes   | **10**     |
| Test Samples      | **156**    |
| Accuracy          | **98.72%** |
| Macro Precision   | **0.99**   |
| Macro Recall      | **0.99**   |
| Macro F1-Score    | **0.99**   |
| Weighted F1-Score | **0.99**   |

## Class-wise Performance

| GesturePrecisionRecallF1-Score |      |      |      |
| ------------------------------ | ---- | ---- | ---- |
| Emergency                      | 1.00 | 1.00 | 1.00 |
| Food                           | 1.00 | 1.00 | 1.00 |
| Hello                          | 1.00 | 1.00 | 1.00 |
| Help                           | 0.97 | 0.97 | 0.97 |
| No                             | 1.00 | 1.00 | 1.00 |
| Okay                           | 1.00 | 1.00 | 1.00 |
| Stop                           | 1.00 | 1.00 | 1.00 |
| Thank You                      | 1.00 | 1.00 | 1.00 |
| Water                          | 1.00 | 0.97 | 0.98 |
| Yes                            | 0.94 | 1.00 | 0.97 |

The model achieved **98.72% test accuracy** with a **0.99 macro F1-score** across all 10 gesture classes.

---

# 📈 Confusion Matrix

The evaluation process generates a confusion matrix to identify classification errors between gesture classes.

The current evaluation shows very few classification errors, with the main remaining confusion occurring between the **Help** and **Water** classes.

Run the following command to generate the evaluation:


```
.\.venv\Scripts\python.exe evaluate_model.py
```

---

# 🏗️ System Architecture


```
┌───────────────────────────┐
│       Web Browser         │
│                           │
│     Webcam Capture        │
└─────────────┬─────────────┘
              │
              ▼
┌───────────────────────────┐
│       Flask Backend       │
│                           │
│     Frame Reception       │
└─────────────┬─────────────┘
              │
              ▼
┌───────────────────────────┐
│          OpenCV           │
│                           │
│      Image Processing     │
└─────────────┬─────────────┘
              │
              ▼
┌───────────────────────────┐
│      MediaPipe Hands      │
│                           │
│   21 Hand Landmark Points │
└─────────────┬─────────────┘
              │
              ▼
┌───────────────────────────┐
│   Landmark Feature Vector │
│        63 Features        │
└─────────────┬─────────────┘
              │
              ▼
┌───────────────────────────┐
│   Random Forest Model     │
│                           │
│   Gesture Classification  │
└─────────────┬─────────────┘
              │
              ▼
┌───────────────────────────┐
│ Gesture + Confidence      │
└─────────────┬─────────────┘
              │
              ▼
┌───────────────────────────┐
│ Temporal Stability Filter │
│                           │
│ Reduce transient errors   │
└─────────────┬─────────────┘
              │
              ▼
┌───────────────────────────┐
│     Text Communication    │
└─────────────┬─────────────┘
              │
              ▼
┌───────────────────────────┐
│ Optional Speech Output    │
│      Web Speech API       │
└───────────────────────────┘
```

---

# 🚀 How to Run

## Requirements

-  Python 3.10 or 3.11
-  Webcam
-  Modern web browser
-  Windows, Linux, or macOS

## 1. Create Virtual Environment


```
python -m venv .venv
```

## 2. Activate Virtual Environment

### Windows PowerShell


```
.\.venv\Scripts\Activate.ps1
```

## 3. Install Dependencies


```
pip install -r requirements.txt
```

## 4. Start the Application


```
.\.venv\Scripts\python.exe app.py
```

Open:


```
http://127.0.0.1:5000
```

Allow webcam access when prompted.

---

# 🧪 Model Training Pipeline

The project includes a complete dataset-to-model training pipeline.

## Dataset Structure


```
dataset/
├── emergency/
├── food/
├── hello/
├── help/
├── no/
├── okay/
├── stop/
├── thank you/
├── water/
└── yes/
```

## Step 1 — Extract Landmarks


```
.\.venv\Scripts\python.exe extract_landmarks.py
```

This processes the gesture images using MediaPipe Hands and generates:


```
landmarks.csv
```

## Step 2 — Train the Random Forest Model


```
.\.venv\Scripts\python.exe train_model.py
```

The trained model is saved as:


```
gesture_model.pkl
```

## Step 3 — Evaluate the Model


```
.\.venv\Scripts\python.exe evaluate_model.py
```

The evaluation provides:

-  Accuracy
-  Precision
-  Recall
-  F1-score
-  Confusion Matrix
-  Class labels

---

# ⏱️ Temporal Stability

GestureSpeak AI uses temporal confirmation to reduce transient false predictions.

A gesture must remain sufficiently consistent over a short time window before it is accepted as the final prediction.

This helps reduce:

-  Accidental triggers
-  Frame-to-frame prediction changes
-  Temporary landmark noise
-  Unstable outputs

---

# 🔊 Text-to-Speech

After a gesture is confirmed, the corresponding communication message is displayed.

Users can optionally enable speech output using the browser's:


```
Web Speech API
```

This provides vocal output without requiring an external speech service.

---

# ♿ Accessibility Features

GestureSpeak AI includes accessibility-focused interface features:

-  Clear gesture instructions
-  Visual gesture feedback
-  Text communication output
-  Optional speech output
-  Font-size controls
-  High-contrast presentation
-  Camera start/stop controls
-  Simple gesture-based interaction
-  Screen-reader-friendly interface elements

---

# 🔐 Privacy

The application is designed to operate locally during normal development.

Webcam data is processed through the local Flask application and is not intentionally uploaded to an external cloud-based gesture recognition service.

No external AI API is required for gesture classification.

---

# 🛠️ Technology Stack

## Frontend

-  HTML5
-  CSS3
-  JavaScript
-  Tailwind CSS
-  Web Speech API

## Backend

-  Python
-  Flask

## Computer Vision

-  OpenCV
-  MediaPipe Hands

## Machine Learning

-  scikit-learn
-  Random Forest Classifier
-  Pandas
-  Joblib

---

# 📁 Project Structure


```
GestureSpeak-AI/
│
├── dataset/
│
├── static/
├── templates/
│
├── app.py
├── gesture_engine.py
├── gesture_classifier.py
├── extract_landmarks.py
├── train_model.py
├── evaluate_model.py
│
├── requirements.txt
├── REVIEW2_RESULTS.md
├── user_testing.md
├── README.md
└── Screenshot.png
```

---

## 📸 Project Evidence

### Working Prototype

The repository includes a screenshot of the live GestureSpeak AI interface.

![GestureSpeak AI](Screenshot.png)

---

## Demonstrated Workflow


```
Webcam
   ↓
Hand Detection
   ↓
Landmark Extraction
   ↓
ML Gesture Recognition
   ↓
Confidence
   ↓
Text
   ↓
Optional Speech
```

---

# 🔎 Verification Guide

1.  Install Python.
2.  Install dependencies using `requirements.txt`.
3.  Start the Flask application.
4.  Open `http://127.0.0.1:5000`.
5.  Open the Live Translator.
6.  Allow webcam access.
7.  Show one of the supported gestures.
8.  Hold the gesture steadily.
9.  Observe the predicted gesture.
10.  Observe the confidence score.
11.  Verify the generated text.
12.  Enable speech output if required.

---

# 🧪 Testing & Validation

GestureSpeak AI uses quantitative machine-learning validation and live webcam testing.

## Quantitative ML Validation

The Random Forest model is evaluated using a held-out test set.

Current measured performance:


```
10 Gesture Classes
156 Test Samples
98.72% Accuracy
0.99 Macro Precision
0.99 Macro Recall
0.99 Macro F1
0.99 Weighted F1
```

## Live Webcam Testing

The application is tested through real-time webcam interaction under practical conditions including :

-  Different hand positions
-  Different distances from the camera
-  Slight hand-angle variations
-  Different lighting conditions

## Usability Testing

Structured usability testing can be conducted with real users to evaluate:

-  Ease of use
-  Gesture guide clarity
-  Recognition experience
-  Text output
-  Speech output
-  Accessibility

Actual user-testing results should be recorded in `user_testing.md`.
