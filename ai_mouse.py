import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import time

# --- Configuration ---
CAMERA_ID = 0
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
SCREEN_WIDTH, SCREEN_HEIGHT = pyautogui.size()
SMOOTHING = 0.1 
MOUSE_SENSITIVITY = 3.00 

# --- Setup ---
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)
mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(CAMERA_ID)
cap.set(3, FRAME_WIDTH)
cap.set(4, FRAME_HEIGHT)

if not cap.isOpened():
    print("ERROR: Could not open camera.")
    exit()

prev_screen_x, prev_screen_y = 0, 0
curr_screen_x, curr_screen_y = 0, 0

print("Bhootiya Mouse Started!")
print("Gestures:")
print("- 5 Fingers: Move")
print("- Fist: Stop")
print("- Pinch (Thumb+Index): Left Click")
print("- 3 Fingers: Right Click")

def count_fingers(landmarks):
    fingers_up = []
    # Index (8) < PIP (6) means finger is UP (Y increases downwards)
    fingers_up.append(landmarks[8].y < landmarks[6].y)
    fingers_up.append(landmarks[12].y < landmarks[10].y)
    fingers_up.append(landmarks[16].y < landmarks[14].y)
    fingers_up.append(landmarks[20].y < landmarks[18].y)
    
    # Text Thumb: Check generic x-offset
    if landmarks[4].x < landmarks[3].x: 
        fingers_up.insert(0, True) 
    else:
        fingers_up.insert(0, False)
        
    return fingers_up.count(True), fingers_up

def get_centroid(landmarks, frame_w, frame_h):
    x_sum = 0
    y_sum = 0
    tips = [4, 8, 12, 16, 20]
    for i in tips:
        x_sum += landmarks[i].x * frame_w
        y_sum += landmarks[i].y * frame_h
    return x_sum / 5, y_sum / 5

while True:
    success, img = cap.read()
    if not success:
        break

    img = cv2.flip(img, 1)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)
    
    h, w, c = img.shape
    
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            lm_list = hand_landmarks.landmark
            
            count, fingers_status = count_fingers(lm_list)
            
            # Logic based on finger count
            # 1. STOP: Fist (0 fingers)
            if count == 0:
                 cv2.putText(img, "Stopped", (10, 50), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 3)
            
            # 2. LEFT CLICK: 2 Fingers (Index + Middle usually)
            elif count == 2:
                cv2.putText(img, "L Click", (10, 50), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 3)
                pyautogui.click()
                time.sleep(0.3) # Debounce

            # 3. RIGHT CLICK: 3 Fingers
            elif count == 3:
                cv2.putText(img, "R Click", (10, 50), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 3)
                pyautogui.click(button='right')
                time.sleep(0.3)
            
            # 4. MOVE: 1, 4, or 5 Fingers (Any other count > 0)
            else:
                # Get Centroid of visible fingertips (or all for stability, let's use all tips for consistent center)
                cx, cy = get_centroid(lm_list, w, h)
                cv2.circle(img, (int(cx), int(cy)), 10, (255, 0, 255), cv2.FILLED)
                
                margin = 50
                x3 = np.interp(cx, (margin, w - margin), (0, SCREEN_WIDTH))
                y3 = np.interp(cy, (margin, h - margin), (0, SCREEN_HEIGHT))
                
                curr_screen_x = prev_screen_x + (x3 - prev_screen_x) * SMOOTHING
                curr_screen_y = prev_screen_y + (y3 - prev_screen_y) * SMOOTHING
                
                pyautogui.moveTo(curr_screen_x, curr_screen_y)
                prev_screen_x, prev_screen_y = curr_screen_x, curr_screen_y
                cv2.putText(img, "Moving", (10, 50), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 3)

    cv2.imshow("AI Vision Mouse", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
