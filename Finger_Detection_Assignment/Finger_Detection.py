import cv2
import mediapipe as mp
import urllib.request
import threading

# ── ESP32 target ─────────────────────────────────────────────────────────────
ESP32_IP   = "10.30.0.173"       # ← change to your ESP32's IP shown on serial
ESP32_PORT = 80

# ── Camera stream ─────────────────────────────────────────────────────────────
STREAM_URL = "http://10.30.0.55:81/stream"

# ── MediaPipe ─────────────────────────────────────────────────────────────────
mp_hands   = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils


def send_command(path: str):
    """Fire-and-forget HTTP GET to the ESP32 in a background thread."""
    def _send():
        url = f"http://{ESP32_IP}:{ESP32_PORT}{path}"
        try:
            with urllib.request.urlopen(url, timeout=2) as resp:
                body = resp.read().decode()
                print(f"ESP32 ← {path}  →  {body}")
        except Exception as e:
            print(f"HTTP error ({path}): {e}")
    threading.Thread(target=_send, daemon=True).start()


def count_fingers(hand_landmarks, handedness: str) -> int:
    """Return how many fingers are raised (0–5)."""
    lm = hand_landmarks.landmark
    fingers_up = 0

    # Thumb — uses x-axis because it moves sideways
    tip = lm[mp_hands.HandLandmark.THUMB_TIP]
    ip  = lm[mp_hands.HandLandmark.THUMB_IP]
    if handedness == "Right":
        if tip.x < ip.x:
            fingers_up += 1
    else:
        if tip.x > ip.x:
            fingers_up += 1

    # Four fingers — tip above PIP = extended
    tips = [
        mp_hands.HandLandmark.INDEX_FINGER_TIP,
        mp_hands.HandLandmark.MIDDLE_FINGER_TIP,
        mp_hands.HandLandmark.RING_FINGER_TIP,
        mp_hands.HandLandmark.PINKY_TIP,
    ]
    pips = [
        mp_hands.HandLandmark.INDEX_FINGER_PIP,
        mp_hands.HandLandmark.MIDDLE_FINGER_PIP,
        mp_hands.HandLandmark.RING_FINGER_PIP,
        mp_hands.HandLandmark.PINKY_PIP,
    ]
    for tip_id, pip_id in zip(tips, pips):
        if lm[tip_id].y < lm[pip_id].y:
            fingers_up += 1

    return fingers_up


def main():
    cap = cv2.VideoCapture(STREAM_URL)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  1000)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 840)

    # Debounce: only send a command when the finger count *changes*
    last_command = None

    with mp_hands.Hands(
        max_num_hands=2,
        model_complexity=1,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    ) as hands:

        while True:
            ret, frame = cap.read()
            if not ret:
                print("Frame grab failed — retrying …")
                continue

            frame = cv2.flip(frame, 1)
            rgb   = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb)

            total_fingers = 0

            if results.multi_hand_landmarks:
                for hand_lm, handedness in zip(
                        results.multi_hand_landmarks,
                        results.multi_handedness):

                    mp_drawing.draw_landmarks(
                        frame, hand_lm, mp_hands.HAND_CONNECTIONS)

                    label = handedness.classification[0].label
                    n     = count_fingers(hand_lm, label)
                    total_fingers += n

                    cv2.putText(
                        frame,
                        f"{label}: {n} finger{'s' if n != 1 else ''}",
                        (10, 60 if label == "Right" else 120),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1.4, (0, 255, 0), 3,
                    )

            # ── Send command only on change ───────────────────────────────
            if total_fingers == 1 and last_command != "on":
                send_command("/led/on")
                last_command = "on"

            elif total_fingers == 2 and last_command != "off":
                send_command("/led/off")
                last_command = "off"

            elif total_fingers not in (1, 2):
                last_command = None   # reset so next 1 or 2 triggers again

            # ── HUD overlay ──────────────────────────────────────────────
            status_text  = "LED: ON"  if last_command == "on"  else \
                           "LED: OFF" if last_command == "off" else \
                           "Show 1 finger = ON  |  2 fingers = OFF"
            status_color = (0, 255, 100) if last_command == "on" else \
                           (0, 100, 255) if last_command == "off" else \
                           (200, 200, 200)

            cv2.putText(frame, status_text, (10, frame.shape[0] - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, status_color, 2)

            cv2.imshow("Finger → LED Control", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()