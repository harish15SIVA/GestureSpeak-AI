# GestureSpeak AI
### AI-Based Hand Gesture Communication System for Non-Speaking Individuals

> **AI Immersion C29 Project Deliverable** | Prototype — Predefined Everyday Needs

---

## 🌟 Overview
**GestureSpeak AI** is an accessible, real-time communication web system engineered to empower non-speaking individuals, post-operative patients, and individuals with speech impairments. 

By leveraging computer vision and hand landmark tracking, the system recognizes **10 predefined everyday physical hand gestures** in real time, translates them into high-contrast sentences, and vocalizes them using browser-native text-to-speech.

---

## 🔄 Core AI Pipeline Flow
```
Webcam 
  ↓ [Raw video frames at 30–60 FPS]
Hand Detection (MediaPipe Hands / BlazePalm)
  ↓ [21 normalized 3D keypoint landmarks]
Feature Extraction
  ↓ [Finger extension states, Euclidean distance matrix, thumb angle]
AI Gesture Classification
  ↓ [Matches 1 of 10 predefined communication classes]
Temporal Consistency Buffer
  ↓ [10-frame sliding window, >=70% agreement to prevent flickering]
Text Translation & Display
  ↓ [Large, accessible high-contrast UI display]
Voice Output (Web Speech API)
    [Synthesized audio speech pronunciation]
```

---

## ✋ 10 Predefined Communication Gestures

| # | Gesture | Icon | Category | Pose Requirement | Output Sentence |
|---|---------|------|----------|------------------|-----------------|
| 1 | **HELLO** | 🖐️ | Social | Open hand raised, palm facing camera | *"Hello, nice to meet you!"* |
| 2 | **YES** | 👍 | Response | Thumb pointing straight up, fingers curled | *"Yes."* |
| 3 | **NO** | 👎 | Response | Thumb pointing straight down, fingers curled | *"No."* |
| 4 | **HELP** | ✌️ | Need | V-sign: index and middle fingers extended & spread | *"I need help."* |
| 5 | **WATER** | 💧 | Need | 'W' sign: three middle fingers extended upright | *"I need water."* |
| 6 | **FOOD** | 🍽️ | Need | Pinch pose: all fingertips clustered touching thumb | *"I want food."* |
| 7 | **STOP** | ✋ | Command | Open flat palm facing forward, fingers firmly spread | *"Please stop."* |
| 8 | **THANK YOU** | 🙏 | Social | Index and middle fingers extended together (parallel) | *"Thank you."* |
| 9 | **OKAY** | 👌 | Response | OK sign: thumb and index forming circle, other 3 up | *"Everything is okay."* |
| 10 | **EMERGENCY** | 🚨 | Emergency | Tightly clenched fist held steadily in frame | *"Emergency! I need immediate help."* |

---

## 🚀 How to Run the Application

### Option A: Zero-Installation Direct Browser Mode (Recommended)
1. Double-click or open `index.html` in any modern web browser (**Google Chrome, Microsoft Edge, Mozilla Firefox, or Safari**).
2. Click **"Start Camera Feed"** and allow webcam permission.
3. Hold predefined gestures in front of your camera.
4. Or switch to **"Demo Mode"** at any time to test all 10 gestures without requiring camera hardware!

### Option B: Python + OpenCV + MediaPipe Engine
If you wish to test with the Python backend:
1. Install Python dependencies:
   ```bash
   py -m pip install -r requirements.txt
   ```
2. Start the Flask server:
   ```bash
   py app.py
   ```
   Open `http://localhost:5000` in your browser.
3. Or run the standalone native desktop OpenCV runner:
   ```bash
   py gesture_detector.py
   ```

---

## 💻 Tech Stack & Architecture
- **Frontend UI:** Modern Dark AI Theme with Cyan/Teal Accents (`#06b6d4`, `#14b8a6`, `#070b14`), Tailwind CSS, Space Grotesk + Inter fonts.
- **Computer Vision:** MediaPipe Hands (21 3D skeleton keypoints), OpenCV (`cv2`).
- **Classification Engine:** Multi-point geometric angle & Euclidean distance vector analysis (`gesture_engine.py` & in-browser JS equivalent).
- **Audio Output:** Web Speech API (`SpeechSynthesis`) with configurable rate, pitch, and voice profiles.
- **Accessibility:** Dynamic font scaling (A- to A++), High Contrast mode, screen-reader friendly ARIA markup.
- **Privacy Guarantee:** 100% client-side local computation. No video or biometric data is stored or transmitted.

---

*GestureSpeak AI — AI Immersion C29 Engineering Project*