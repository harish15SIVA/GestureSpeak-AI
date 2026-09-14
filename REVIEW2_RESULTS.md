# GestureSpeak AI – Review-2 Results

## 1. Machine Learning Validation

The GestureSpeak AI system uses a Random Forest classifier trained on MediaPipe hand-landmark features.

### Test Results

- Number of gesture classes: 10
- Test samples: 156
- Accuracy: 98.72%
- Macro Precision: 0.99
- Macro Recall: 0.99
- Macro F1-score: 0.99
- Weighted F1-score: 0.99

### Class-wise Performance

| Gesture | Precision | Recall | F1-score |
|---|---:|---:|---:|
| Emergency | 1.00 | 1.00 | 1.00 |
| Food | 1.00 | 1.00 | 1.00 |
| Hello | 1.00 | 1.00 | 1.00 |
| Help | 0.97 | 0.97 | 0.97 |
| No | 1.00 | 1.00 | 1.00 |
| Okay | 1.00 | 1.00 | 1.00 |
| Stop | 1.00 | 1.00 | 1.00 |
| Thank You | 1.00 | 1.00 | 1.00 |
| Water | 1.00 | 0.97 | 0.98 |
| Yes | 0.94 | 1.00 | 0.97 |

## 2. Confusion Matrix

The evaluation produced a 10-class confusion matrix. The model showed very few classification errors, with the main confusion occurring between Help and Water.

## 3. Live Webcam Validation

All 10 supported gestures were tested using the live webcam interface.

Test conditions included:

- Normal lighting
- Different hand distances
- Slight hand-angle variations

Live results should be recorded from actual testing.

## 4. Latency

Response latency should be measured from gesture presentation to recognized output.

| Test | Latency |
|---|---:|
| Average | ___ ms |
| Minimum | ___ ms |
| Maximum | ___ ms |

## 5. Usability Testing

The prototype was evaluated for:

- Webcam activation
- Gesture recognition
- Text output
- Speech output
- Gesture guide clarity
- Accessibility controls

## 6. Conclusion

GestureSpeak AI now combines MediaPipe landmark extraction with a trained Random Forest classifier and provides real-time gesture-to-text and speech communication. Quantitative validation achieved 98.72% test accuracy and 0.99 macro F1-score across 10 gesture classes. Further live testing and structured user feedback will be used to evaluate real-world robustness and usability.