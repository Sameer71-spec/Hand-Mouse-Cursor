import cv2
import mediapipe as mp
import pyautogui

# Screen size
screen_w, screen_h = pyautogui.size()

# MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)
mp_draw = mp.solutions.drawing_utils

# Camera
cap = cv2.VideoCapture(0)

# Smooth cursor
prev_x, prev_y = 0, 0
smoothening = 7

while True:
    _, frame = cap.read()
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb_frame)

    if result.multi_hand_landmarks:
        for handLms in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, handLms, mp_hands.HAND_CONNECTIONS)
            # Index finger tip
            x1 = handLms.landmark[8].x
            y1 = handLms.landmark[8].y

            # Convert to screen coordinates
            screen_x = screen_w * x1
            screen_y = screen_h * y1

            # Smooth cursor
            curr_x = prev_x + (screen_x - prev_x) / smoothening
            curr_y = prev_y + (screen_y - prev_y) / smoothening

            pyautogui.moveTo(curr_x, curr_y)
            prev_x, prev_y = curr_x, curr_y

            # Left click gesture (index + thumb)
            thumb_tip = handLms.landmark[4]
            distance = ((thumb_tip.x - x1)**2 + (thumb_tip.y - y1)**2)**0.5
            if distance < 0.04:
                pyautogui.click()

    cv2.imshow("Virtual Mouse", frame)
    if cv2.waitKey(1) & 0xFF == 27:  # ESC key to exit
        break

cap.release()
cv2.destroyAllWindows()
