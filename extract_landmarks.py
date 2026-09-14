import os
import csv
import cv2
import mediapipe as mp

# Dataset and output paths
DATASET_DIR = "dataset"
OUTPUT_FILE = "landmarks.csv"

# MediaPipe Hands
mp_hands = mp.solutions.hands

# 10 gesture classes
GESTURES = [
    "emergency",
    "food",
    "hello",
    "help",
    "no",
    "okay",
    "stop",
    "thank you",
    "water",
    "yes"
]

# Create MediaPipe detector
hands = mp_hands.Hands(
    static_image_mode=True,
    max_num_hands=1,
    min_detection_confidence=0.5
)

rows = []
total_images = 0
successful = 0
failed = 0

print("Starting landmark extraction...\n")

for gesture in GESTURES:

    gesture_folder = os.path.join(DATASET_DIR, gesture)

    if not os.path.exists(gesture_folder):
        print(f"Folder not found: {gesture_folder}")
        continue

    files = [
        f for f in os.listdir(gesture_folder)
        if f.lower().endswith((".jpg", ".jpeg", ".png"))
    ]

    print(f"{gesture}: {len(files)} images")

    for filename in files:

        image_path = os.path.join(gesture_folder, filename)
        image = cv2.imread(image_path)

        if image is None:
            failed += 1
            continue

        total_images += 1

        # Convert BGR → RGB
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Detect hand
        result = hands.process(rgb_image)

        if not result.multi_hand_landmarks:
            failed += 1
            continue

        hand = result.multi_hand_landmarks[0]

        # Use wrist as reference point
        wrist = hand.landmark[0]

        features = []

        # Create normalized landmark features
        for landmark in hand.landmark:
            x = landmark.x - wrist.x
            y = landmark.y - wrist.y
            z = landmark.z - wrist.z

            features.extend([x, y, z])

        # Add gesture label
        rows.append(features + [gesture])

        successful += 1

hands.close()

# Create CSV
header = []

for i in range(21):
    header.extend([
        f"x{i}",
        f"y{i}",
        f"z{i}"
    ])

header.append("label")

with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)

    writer.writerow(header)
    writer.writerows(rows)

print("\n--------------------------------")
print("LANDMARK EXTRACTION COMPLETED")
print("--------------------------------")
print(f"Total images processed : {total_images}")
print(f"Successful             : {successful}")
print(f"Failed / no hand       : {failed}")
print(f"Training samples       : {len(rows)}")
print(f"Output file            : {OUTPUT_FILE}")
print("--------------------------------")