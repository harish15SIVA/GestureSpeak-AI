r"""
gesture_classifier.py
----------------------
Rule-based gesture classifier for GestureSpeak AI.

This module takes MediaPipe hand-landmark output and turns it into one of
the 10 supported everyday-communication gestures. It is intentionally kept
separate from app.py: the interface (classify(hands_data)) is stable, so the
rule-based logic below can later be swapped for a trained ML model (e.g. a
small classifier trained on landmark vectors) without touching Flask code or
the frontend.

Landmark indexing follows the standard MediaPipe Hands topology:

        8   12  16  20
        |    |   |   |
        7   11  15  19
        |    |   |   |
        6   10  14  18
        |    |   |   |
        5    9  13  17
         \   |   |   /
          \  |   |  /
    4       \ |   | /
     \       \|   |/
      3       [ 0 ]        0 = wrist
       \       /
        2     /
         \   /
          1

Thumb:  1 (CMC) -> 2 (MCP) -> 3 (IP) -> 4 (TIP)
Index:  5 (MCP)  -> 6 (PIP) -> 7 (DIP) -> 8 (TIP)
Middle: 9        -> 10      -> 11      -> 12 (TIP)
Ring:   13       -> 14      -> 15      -> 16 (TIP)
Pinky:  17       -> 18      -> 19      -> 20 (TIP)
"""

import math
import time
from collections import deque

# ---------------------------------------------------------------------------
# Gesture metadata: single source of truth for names, messages and emoji.
# Keeping this here (rather than duplicated in JS) means the frontend simply
# mirrors whatever the backend returns.
# ---------------------------------------------------------------------------
GESTURES = {
    "FOOD": {"message": "I want food.", "emoji": "🍛"},
    "WATER": {"message": "I need water.", "emoji": "💧"},
    "TEA_COFFEE": {"message": "I want tea or coffee.", "emoji": "☕"},
    "HELP": {"message": "I need help.", "emoji": "🆘"},
    "YES": {"message": "Yes.", "emoji": "👍"},
    "NO": {"message": "No.", "emoji": "👎"},
    "PLEASE": {"message": "Please.", "emoji": "🙏"},
    "WANT_THAT": {"message": "I want that.", "emoji": "☝️"},
    "OKAY": {"message": "I am okay.", "emoji": "👌"},
    "HELLO": {"message": "Hello. Please notice me.", "emoji": "👋"},
    "UNKNOWN": {"message": "Show one supported gesture clearly.", "emoji": "🤔"},
}


# ---------------------------------------------------------------------------
# Small geometry helpers
# ---------------------------------------------------------------------------
def _dist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def _finger_extended(landmarks, tip_idx, pip_idx, mcp_idx, wrist):
    """A non-thumb finger counts as extended if its tip is meaningfully
    farther from the wrist than its own PIP joint - this is robust to hand
    rotation, unlike a plain y-coordinate comparison."""
    tip = landmarks[tip_idx]
    pip = landmarks[pip_idx]
    return _dist(tip, wrist) > _dist(pip, wrist) * 1.10


def _thumb_extended(landmarks, handedness_label):
    """The thumb folds *across* the palm rather than curling like the other
    fingers, so tip-vs-PIP distance-from-wrist doesn't work well for it.
    Instead: a folded thumb tip rests close to the index-finger base
    (inside the palm); an extended thumb (up, down, or out to the side)
    moves well clear of it. Distances are normalised by palm width so this
    holds regardless of how close the hand is to the camera."""
    tip = landmarks[4]
    mcp = landmarks[2]
    index_mcp = landmarks[5]
    pinky_mcp = landmarks[17]
    palm_width = _dist(index_mcp, pinky_mcp)
    tip_to_index_mcp = _dist(tip, index_mcp)
    return tip_to_index_mcp > palm_width * 0.6 and tip_to_index_mcp > _dist(mcp, index_mcp)


def _finger_states(landmarks, handedness_label):
    wrist = landmarks[0]
    return {
        "thumb": _thumb_extended(landmarks, handedness_label),
        "index": _finger_extended(landmarks, 8, 6, 5, wrist),
        "middle": _finger_extended(landmarks, 12, 10, 9, wrist),
        "ring": _finger_extended(landmarks, 16, 14, 13, wrist),
        "pinky": _finger_extended(landmarks, 20, 18, 17, wrist),
    }


def _hand_size(landmarks):
    """Rough scale reference (wrist to middle-finger MCP) used to normalise
    distance thresholds like the OK-sign pinch, so the classifier works at
    different distances from the camera."""
    return max(_dist(landmarks[0], landmarks[9]), 1e-6)


# ---------------------------------------------------------------------------
# Wave detection needs short-term motion history. This keeps a small
# in-memory buffer of recent wrist x-positions. It is process-global, which
# is a reasonable simplification for this single-user prototype - a
# multi-user deployment would key this by session id instead.
# ---------------------------------------------------------------------------
class _WaveTracker:
    def __init__(self, maxlen=14, window_seconds=1.6):
        self.positions = deque(maxlen=maxlen)
        self.window_seconds = window_seconds

    def push(self, x, hand_scale):
        now = time.time()
        self.positions.append((now, x, hand_scale))
        cutoff = now - self.window_seconds
        while self.positions and self.positions[0][0] < cutoff:
            self.positions.popleft()

    def is_waving(self):
        if len(self.positions) < 6:
            return False
        xs = [p[1] for p in self.positions]
        scale = max(p[2] for p in self.positions)
        # Count direction reversals in the recent x-track - a wave produces
        # several left-right reversals, a steady hand produces none.
        reversals = 0
        direction = 0
        span = max(xs) - min(xs)
        for i in range(1, len(xs)):
            delta = xs[i] - xs[i - 1]
            if abs(delta) < scale * 0.02:
                continue
            new_direction = 1 if delta > 0 else -1
            if direction != 0 and new_direction != direction:
                reversals += 1
            direction = new_direction
        return reversals >= 2 and span > scale * 0.35


_wave_tracker = _WaveTracker()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def classify(hands_data):
    """
    hands_data: list of hands, each a dict:
        {
            "landmarks": [(x, y), ...21 points, normalised 0-1],
            "handedness": "Left" | "Right"
        }

    Returns: (gesture_key, confidence, hands_count)
    """
    hands_count = len(hands_data)

    if hands_count == 0:
        return "UNKNOWN", 0.0, 0

    # --- Two hands close together -> PLEASE -----------------------------
    if hands_count == 2:
        wrist_a = hands_data[0]["landmarks"][0]
        wrist_b = hands_data[1]["landmarks"][0]
        scale_a = _hand_size(hands_data[0]["landmarks"])
        scale_b = _hand_size(hands_data[1]["landmarks"])
        avg_scale = (scale_a + scale_b) / 2
        if _dist(wrist_a, wrist_b) < avg_scale * 2.6:
            return "PLEASE", 0.9, 2
        # Two hands detected but not together: classify the more confident
        # single-hand gesture from either hand instead of forcing PLEASE.

    # --- Single-hand gestures --------------------------------------------
    best_key, best_conf = "UNKNOWN", 0.0
    for hand in hands_data:
        landmarks = hand["landmarks"]
        handedness = hand.get("handedness", "Right")
        fingers = _finger_states(landmarks, handedness)
        wrist = landmarks[0]
        scale = _hand_size(landmarks)
        extended_count = sum(fingers.values())

        key, conf = "UNKNOWN", 0.0

        # OK sign: thumb tip and index tip pinched together, other three
        # fingers extended.
        pinch_dist = _dist(landmarks[4], landmarks[8])
        if pinch_dist < scale * 0.55 and fingers["middle"] and fingers["ring"] and fingers["pinky"]:
            key, conf = "OKAY", 0.93

        # Closed fist: nothing extended.
        elif extended_count == 0:
            key, conf = "HELP", 0.95

        # Thumb only -> up or down, judged by tip position vs wrist.
        elif fingers["thumb"] and extended_count == 1:
            tip_y = landmarks[4][1]
            wrist_y = wrist[1]
            if tip_y < wrist_y - scale * 0.15:
                key, conf = "YES", 0.92
            elif tip_y > wrist_y + scale * 0.05:
                key, conf = "NO", 0.9
            else:
                key, conf = "YES", 0.7

        # Index only -> pointing.
        elif fingers["index"] and not fingers["middle"] and not fingers["ring"] \
                and not fingers["pinky"] and not fingers["thumb"]:
            key, conf = "WANT_THAT", 0.93

        # Index + middle only -> victory / tea-coffee.
        elif fingers["index"] and fingers["middle"] and not fingers["ring"] \
                and not fingers["pinky"]:
            key, conf = "TEA_COFFEE", 0.93

        # Index + middle + ring, thumb & pinky folded -> three fingers / water.
        elif fingers["index"] and fingers["middle"] and fingers["ring"] \
                and not fingers["pinky"]:
            key, conf = "WATER", 0.9

        # All five extended -> open palm. Distinguish a still palm (FOOD)
        # from a waving palm (HELLO) using the motion tracker.
        elif extended_count == 5:
            _wave_tracker.push(wrist[0], scale)
            if _wave_tracker.is_waving():
                key, conf = "HELLO", 0.88
            else:
                key, conf = "FOOD", 0.9

        if conf > best_conf:
            best_key, best_conf = key, conf

    return best_key, best_conf, hands_count


def gesture_payload(key, confidence, hands_count):
    """Builds the JSON-ready response for a classified gesture."""
    info = GESTURES.get(key, GESTURES["UNKNOWN"])
    if key == "UNKNOWN":
        message = (
            "No hand detected."
            if hands_count == 0
            else "Gesture not recognized. Hold your hand clearly and steadily."
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
